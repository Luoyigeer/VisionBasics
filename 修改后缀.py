import os

def change_extension(folder_path, old_ext, new_ext):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否以指定的旧后缀结尾
        if filename.endswith(old_ext):
            # 构造旧的文件路径和新的文件路径
            old_filepath = os.path.join(folder_path, filename)
            new_filename = os.path.splitext(filename)[0] + new_ext
            new_filepath = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_filepath, new_filepath)

# 指定要修改的文件夹路径、旧后缀和新后缀
folder_path = r"E:\yolov7s_traffic_car_det\Datasetprocessing\img1"
old_extension = ".png"
new_extension = ".jpg"

# 调用函数进行修改
change_extension(folder_path, old_extension, new_extension)
