import cv2
import numpy as np
import insightface
from keras.models import load_model
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import sqlite3
import os
import json


class YCfaceAnalysis:
    def __init__(self):
        """
        初始化YCfaceAnalysis对象。
        """
        self.initialized = False  # 用于记录初始化是否成功
        try:
            self.app = FaceAnalysis(name="buffalo_sc",providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self.fas_model = load_model("/home/l/桌面/fas.h5")  # 加载活体检测模型
            self.registered_features = {}  # 存放所有注册的人脸特征信息
            self._init_database()  # 初始化数据库
            self._load_registered_features()  # 加载已注册的人脸特征
            self.initialized = True  # 标记初始化成功
        except Exception as e:
            print(f"初始化失败: {e}")
            self.initialized = False  # 标记初始化失败

    def is_initialized(self):
        """
        检查初始化是否成功。

        返回:
        - True: 初始化成功
        - False: 初始化失败
        """
        return self.initialized

    def _init_database(self):
        """
        初始化SQLite数据库。
        """
        os.makedirs("./YCDATA", exist_ok=True)
        self.conn = sqlite3.connect("./faceInfo.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                face_id TEXT PRIMARY KEY,
                name TEXT,
                feature TEXT
            )
        ''')
        self.conn.commit()

    def _load_registered_features(self):
        """
        从数据库加载已注册的人脸特征信息。
        """
        self.cursor.execute("SELECT face_id, name, feature FROM faces")
        rows = self.cursor.fetchall()
        for row in rows:
            face_id, name, feature = row
            self.registered_features[face_id] = {
                'name': name,
                'feature': json.loads(feature)
            }

    def face_detection(self, image):
        """
        人脸检测。

        参数:
        - image: 输入的一张图像，可以是文件路径或numpy数组。

        返回:
        - Json形式返回字典（Dict）:
          {
              'faceNum': 人脸数量,
              'faceInfo': [[x1, y1, w1, h1], ...]  # 人脸坐标，bbox的中心点和宽高
          }
        """
        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image

        faces = self.app.get(img)
        face_info = []

        for face in faces:
            bbox = face.bbox
            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) / 2  # 中心点横坐标
            cy = (y1 + y2) / 2  # 中心点纵坐标
            w = x2 - x1
            h = y2 - y1
            face_info.append([cx, cy, w, h])

        result = {
            'faceNum': len(faces),
            'faceInfo': face_info if len(faces) > 0 else []
        }

        return result

    def face_registration(self, image, name, face_id):
        """
        人脸注册。

        参数:
        - image: 输入的一张单人人脸图像，可以是文件路径或numpy数组。
        - name: 人脸对应的姓名。
        - face_id: 人脸对应的唯一标识符。

        返回:
        - Json形式返回字典（Dict）:
          {
              'errCode': 0  # 处理成功默认是0；处理失败,1代表没检测到人脸
          }
        """
        detection_result = self.face_detection(image)
        if detection_result['faceNum'] == 0:
            return {'errCode': 1}

        # 获取面积最大的人脸
        faces = self.app.get(image if isinstance(image, np.ndarray) else cv2.imread(image))
        largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))

        # 提取特征并转为字符串
        feature = largest_face.embedding.tolist()
        feature_str = json.dumps(feature)

        # 存入数据库
        try:
            self.cursor.execute("INSERT INTO faces (face_id, name, feature) VALUES (?, ?, ?)",
                                (face_id, name, feature_str))
            self.conn.commit()
            self.registered_features[face_id] = {'name': name, 'feature': feature}
            return {'errCode': 0}
        except sqlite3.IntegrityError:
            return {'errCode': 1}

    def face_recognition(self, image):
        """
        人脸识别。

        参数:
        - image: 输入的一张单人人脸图像，可以是文件路径或numpy数组。

        返回:
        - Json形式返回字典（Dict）:
          {
              'errCode': 0,  # 处理成功默认是0；处理失败,1代表没检测到人脸,2代表没有识别到相似人脸
              'regInfo': {'faceName': '', 'faceID': ''}
          }
        """
        detection_result = self.face_detection(image)
        if detection_result['faceNum'] == 0:
            return {'errCode': 1}

        # 获取面积最大的人脸
        faces = self.app.get(image if isinstance(image, np.ndarray) else cv2.imread(image))
        largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))

        # 计算与已注册特征的相似度
        target_feature = largest_face.embedding
        best_match = None
        best_score = 0

        for face_id, info in self.registered_features.items():
            registered_feature = np.array(info['feature'])
            score = np.dot(target_feature, registered_feature) / (
                    np.linalg.norm(target_feature) * np.linalg.norm(registered_feature))
            if score > best_score:
                best_score = score
                best_match = face_id

        if best_match and best_score > 0.6:  # 相似度阈值设为0.6
            return {
                'errCode': 0,
                'regInfo': {
                    'faceName': self.registered_features[best_match]['name'],
                    'faceID': best_match
                }
            }
        else:
            return {'errCode': 2}

    def liveness_detection(self, image):
        """
        活体检测。

        参数:
        - image: 输入的一张单人人脸图像，可以是文件路径或numpy数组。

        返回:
        - Json形式返回字典（Dict）:
          {
              'errCode': 0,  # 处理成功默认是0；处理失败,1代表没检测到人脸
              'liveInfo': 0  # 0表示非活体，1表示活体
          }
        """
        # 初始化返回结果
        result = {
            'errCode': 0,
            'liveInfo': 0,
        }

        if isinstance(image, str):
            img = cv2.imread(image)
        else:
            img = image

        faces = self.app.get(img)

        # 检查是否检测到人脸
        if not faces or len(faces) == 0:
            result['errCode'] = 1  # 未检测到人脸
            return result

        # 获取第一个人脸的边界框
        face = faces[0]  # 假设只处理第一个人脸
        bbox = face.bbox
        x1, y1, x2, y2 = bbox
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        # 截取人脸区域
        face_image = img[y1:y2, x1:x2]

        # 如果人脸区域为空，返回错误
        if face_image.size == 0:
            result['errCode'] = 1
            return result

        # 预处理人脸图像
        face_image = cv2.resize(face_image, (224, 224))  # 调整大小
        face_image = (face_image - 127.5) / 127.5  # 归一化
        face_image = np.expand_dims(face_image, axis=0)  # 增加批次维度

        # 进行活体检测
        score = self.fas_model.predict(face_image)[0][0]

        # 根据阈值判断活体
        if score > 0.85:  # 阈值可根据实际情况调整
            result['liveInfo'] = 1  # 活体
        else:
            result['liveInfo'] = 0  # 非活体

        return result


# 示例用法
if __name__ == "__main__":
    face_analysis = YCfaceAnalysis()
    if face_analysis.is_initialized():
        print("初始化成功")
        # 人脸检测
        detection_result = face_analysis.face_detection('/home/l/桌面/face.jpeg')
        print("人脸检测结果:", detection_result)

        # 人脸注册
        registration_result = face_analysis.face_registration('/home/l/桌面/singleface.jpg', 'Alice', '001')
        print("人脸注册结果:", registration_result)

        # 人脸识别
        recognition_result = face_analysis.face_recognition('/home/l/桌面/singleface.jpg')
        print("人脸识别结果:", recognition_result)

        # 活体检测
        liveness_result = face_analysis.liveness_detection('/home/l/桌面/fakeface.png')
        print("活体检测结果:", liveness_result)
    else:
        print("初始化失败")