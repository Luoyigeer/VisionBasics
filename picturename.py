import os
#爬下来的图片就是各种中文和符号名称，很复杂。你用这个，图片名称，统一修改一下，方便你后面操作
# 修改前缀
prefix = "yanhuo"

# 图片目录路径
dir_path = "E:/yanhuo/yanhuo"

# 获取目录下所有图片文件名
files = os.listdir(dir_path)
# 对文件名进行排序
files.sort()

# 遍历排序后的文件名列表
for i, filename in enumerate(files):
    # 判断是否为图片文件
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # 构造新的文件名
        new_filename = prefix + str(i + 1).zfill(3) + os.path.splitext(filename)[1]
        # 构造旧的文件路径
        old_filepath = os.path.join(dir_path, filename)
        # 构造新的文件路径
        new_filepath = os.path.join(dir_path, new_filename)
        # 重命名文件
        os.rename(old_filepath, new_filepath)
        print(f"Renamed {old_filepath} to {new_filepath}")