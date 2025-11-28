import os
import cv2


# 定义保存图片函数
# image:要保存的图片
# pic_address：图片保存地址
# num: 图片后缀名，用于区分图片，int 类型
def save_image(image, address, num):
    pic_address = address + str(num) + '.jpg'
    cv2.imwrite(pic_address, image)


def video_to_pic(video_path, save_path, frame_rate):
    # 读取视频文件
    videoCapture = cv2.VideoCapture(video_path)
    global j  # 将 j 声明为全局变量
    # 获取之前保存的最大 j 值
    j_start = j
    i = 0
    date="240619"
    # 读帧
    success, frame = videoCapture.read()
    while success:
        i = i + 1
        # 每隔固定帧保存一张图片
        if i % frame_rate == 0:
            j = j + 1
            save_image(frame, save_path, date+str(j))
            print('图片保存地址：', save_path + str(j) + '.jpg')
        success, frame = videoCapture.read()
    j = max(j, j_start)


if __name__ == '__main__':
    # 视频文件和图片保存地址
    SAMPLE_VIDEO = r'C:\Users\linc\Desktop\yanhuo2'#视频文件夹名
    SAVE_PATH = r'C:\Users\linc\Desktop\yanhuo2\\'#图片保存文件夹
    j=0
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    # 设置固定帧
    FRAME_RATE = 20
    #video_to_pic(SAMPLE_VIDEO, SAVE_PATH, FRAME_RATE)
    for root, dirs, files in os.walk(SAMPLE_VIDEO):
        for file in files:
            if file.endswith('.mp4'):
                video_path = os.path.join(root, file)
                video_to_pic(video_path, SAVE_PATH, FRAME_RATE)
