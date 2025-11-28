import os

def modify_class_index(annotation_folder, class_mapping):
    # 获取所有标注文件的路径
    annotation_files = [f for f in os.listdir(annotation_folder) if f.endswith('.txt')]

    # 遍历每个标注文件
    for annotation_file in annotation_files:
        file_path = os.path.join(annotation_folder, annotation_file)

        # 读取标注文件内容
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # 根据类别映射进行修改
        modified_lines = [f'{class_mapping.get(int(line.split(" ", 1)[0]), int(line.split(" ", 1)[0]))} {line.split(" ", 1)[1]}' for line in lines]

        # 将修改后的内容写回标注文件
        with open(file_path, 'w') as f:
            f.writelines(modified_lines)
            '''
            for line in lines:: 这是一个列表推导式的迭代部分，它遍历标注文件中的每一行。

int(line.split(" ", 1)[0]): 这部分代码将每一行按空格分割，并取得分割后的第一个部分，即原始的类别序号。int(...) 将这个字符串转换为整数。

class_mapping.get(int(line.split(" ", 1)[0]), int(line.split(" ", 1)[0])): 这部分代码使用字典 class_mapping 来获取映射后的新类别。get 方法的第一个参数是要查找的键（原始类别序号），第二个参数是如果找不到键时返回的默认值（即保持原始类别不变）。

{...} {line.split(" ", 1)[1]}: 这部分代码构建了新的行内容。花括号 {} 中的表达式是新的类别序号，然后后面接着空格和原始行中的其余部分（边界框信息）。

整体来说，这段代码的作用是遍历标注文件的每一行，将行中的原始类别序号映射为新的类别序号，然后构建新的行内容，形成了修改后的标注文件内容。这一行代码实现了将类别序号进行映射的功能。'''

if __name__ == "__main__":
    # 设置标注文件夹路径和类别映射字典
    annotation_folder_path = 'D:/pycharm/pycharm项目/yolotxt/val'
    class_mapping = {3: 0,2: 0,1:0,4:1,5:1,7:2}  # 在这里添加你的类别映射关系

    # 调用函数进行修改
    modify_class_index(annotation_folder_path, class_mapping)