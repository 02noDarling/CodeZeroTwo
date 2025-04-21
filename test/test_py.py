import subprocess

# 确保你的Python解释器路径正确，或者使用'python'（如果它在PATH中）
python_interpreter = r'C:\Users\DELL\AppData\Local\Programs\Python\Python39\python.exe'  # 或者 'python3'
main_py_path = 'main.py'  # 这是main.py的路径，如果它在同一目录下，则直接使用文件名
input_file_path = 'in.txt'  # 这是输入文件的路径
output_file_path = 'out.txt'  # 这是输出文件的路径

# 使用subprocess模块运行main.py，并将in.txt作为输入，将输出重定向到out.txt
with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    # 使用Popen来启动子进程，stdin和stdout使用管道
    process = subprocess.Popen([python_interpreter, main_py_path],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)  # 如果你想捕获stderr，可以将其重定向到stdout或一个文件

    # 读取in.txt的内容并传递给main.py
    output, _ = process.communicate(input_file.read().encode())  # communicate需要字节串，所以编码输入

    # 将main.py的输出写入out.txt
    output_file.write(output.decode())  # 解码输出以写入文件

# 检查main.py的退出状态
if process.returncode != 0:
    print(f"main.py执行失败，返回码为：{process.returncode}")