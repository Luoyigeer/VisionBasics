import time
import os
from PIL import Image
import cv2
import numpy as np

'''人为构造xml文件的格式'''
out0 = '''<?xml version="1.0" ?>
<annotation>
    <folder>%(folder)s</folder>
    <filename>%(name)s</filename>
    <path>UnKnown</path>
    <source>
        <database>The VOC2007 Database</database>
    </source>
    <size>
        <width>%(width)d</width>
        <height>%(height)d</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
'''
out1 = '''    <object>
        <name>%(class)s</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%(xmin)d</xmin>
            <ymin>%(ymin)d</ymin>
            <xmax>%(xmax)d</xmax>
            <ymax>%(ymax)d</ymax>
        </bndbox>
    </object>
'''

out2 = '''</annotation>
'''

'''txt转xml函数'''


def translate(fdir, lists):
    source = {}
    label = {}
    for jpg in lists:
        print(jpg)
        if jpg[-4:] == '.jpg' or jpg[-4:] == '.png':
            #image = cv2.imread(jpg)  # 路径不能有中文
            image = cv2.imdecode(np.fromfile(jpg, dtype=np.uint8), -1)
            h, w, _ = image.shape  # 图片大小
            #            cv2.imshow('1',image)
            #            cv2.waitKey(1000)
            #            cv2.destroyAllWindows()

            fxml = jpg.replace('.jpg', '.xml').replace('.png', '.xml')
            fxml = open(fxml, 'w')
            imgfile = os.path.basename(jpg)
            source['name'] = imgfile
            source['path'] = jpg
            source['folder'] = os.path.basename(fdir)

            source['width'] = w
            source['height'] = h

            fxml.write(out0 % source)
            txt = jpg.replace('.jpg', '.txt').replace('.png', '.txt')

            lines = np.loadtxt(txt)  # 读入txt存为数组
            # print(type(lines))

            if len(np.array(lines).shape) == 1:
                lines = [lines]

        for box in lines:
            # print(box.shape)
            if box.shape != (5,):
                box = lines

            '''把txt上的第一列（类别）转成xml上的类别
               我这里是labelimg标1、2、3，对应txt上面的0、1、2'''
            #label['class'] = str(int(box[0]) + 1)  # 类别索引从1开始
            label['class'] = int(box[0])

            '''把txt上的数字（归一化）转成xml上框的坐标'''
            xmin = float(box[1] - 0.5 * box[3]) * w
            ymin = float(box[2] - 0.5 * box[4]) * h
            xmax = float(xmin + box[3] * w)
            ymax = float(ymin + box[4] * h)

            label['xmin'] = xmin
            label['ymin'] = ymin
            label['xmax'] = xmax
            label['ymax'] = ymax

            # if label['xmin']>=w or label['ymin']>=h or label['xmax']>=w or label['ymax']>=h:
            #     continue
            # if label['xmin']<0 or label['ymin']<0 or label['xmax']<0 or label['ymax']<0:
            #     continue

            fxml.write(out1 % label)
        fxml.write(out2)


def check_and_remove_files(file_dir, lists):
    for i in os.listdir(file_dir):
        if i[-3:] == 'jpg' or i[-3:] == 'png':
            jpg_file_path = os.path.join(file_dir, i)
            txt_file_path = os.path.join(file_dir, i[:-3] + 'txt')

            # 检查同名.txt文件是否存在
            if not os.path.exists(txt_file_path):
                # 如果.txt文件不存在，则从列表中删除对应的.jpg文件
                lists.remove(jpg_file_path)
                print(f"Deleted {jpg_file_path} as corresponding .txt file doesn't exist.")

if __name__ == '__main__':
    file_dir = r'C:\Users\Sept\Desktop\z_xml_30010002\综合'
    lists = []
    for i in os.listdir(file_dir):
        if i[-3:] == 'jpg' or i[-3:] == 'png':
            jpg_file_path = os.path.join(file_dir, i)
            lists.append(jpg_file_path)
    print(lists)
    check_and_remove_files(file_dir, lists)
    print(lists)
    translate(file_dir, lists)
    print('---------------Done!!!--------------')
