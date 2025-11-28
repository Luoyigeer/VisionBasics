import os
import xml.etree.ElementTree as ET

#在xml文件第一行修改文件夹信息
def modify_xml_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                # 解析XML文件
                tree = ET.parse(file_path)
                root_elem = tree.getroot()

                # 遍历XML文件中的每一个元素
                for elem in root_elem.iter():
                    if elem.tag == "folder":
                        # 将<folder/>改为<folder>1</folder>
                        elem.text = "0"

                # 将修改后的XML写回文件
                tree.write(file_path, encoding='utf-8', xml_declaration=True)


# 指定要修改的文件夹路径
folder_path = r"E:\yanhuo\0"
# 调用函数进行修改
modify_xml_folder(folder_path)



