import subprocess


def compile_java(java_file):
    # 确保 javac 命令可用
    try:
        subprocess.check_call([r'E:\jdk-17\bin\javac', "--version"])
    except subprocess.CalledProcessError:
        print("Error: javac is not installed or not in PATH.")
        return

        # 编译 Java 文件
    try:
        subprocess.check_call([r'E:\jdk-17\bin\javac', java_file])
        print(f"Successfully compiled {java_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {java_file}: {e}")
        print(e.returncode)


def run_java_program(java_class_name, input_file_path, output_file_path):
    with open(output_file_path, 'wb') as outfile:  # 使用'wb'模式以二进制形式写入
    # 使用Popen启动Java程序，并将stdout重定向到outfile
        java_process = subprocess.Popen(['java', java_class_name], stdin=subprocess.PIPE, stdout=outfile, stderr=subprocess.PIPE)

        # 打开in.txt文件以读取内容，并通过PIPE传递给Java的stdin
        with open(input_file_path, 'r') as infile:
            # 将in.txt的内容传递给Java程序的stdin
            java_process.stdin.write(infile.read().encode())  # 将字符串编码为字节串
            java_process.stdin.close()  # 关闭stdin，确保所有数据都被发送

        # 等待Java程序完成并获取stderr（如果有的话）
        _, stderr = java_process.communicate()

        # 如果Java程序正常结束，stdout已经被写入到out.txt中
        # 否则，处理stderr中的错误信息
        if java_process.returncode != 0:
            print("Java error:")
            print(java_process.stderr)
            # print(stderr.decode('utf-8', errors='replace'))

            # print(stderr.decode())


    # try:
    #     # 假设我们运行一个Java命令，并希望捕获其输出和错误
    #     with open(output_file_path, 'wb') as outfile:  # 使用'wb'模式以二进制形式写入
    #         result = subprocess.Popen(['java', java_class_name], stdin=subprocess.PIPE, stdout=outfile, stderr=subprocess.PIPE)
    #
    #             # 打开in.txt文件以读取内容，并通过PIPE传递给Java的stdin
    #         with open(input_file_path, 'r') as infile:
    #             # 将in.txt的内容传递给Java程序的stdin
    #             result.stdin.write(infile.read().encode())  # 将字符串编码为字节串
    #             result.stdin.close()  # 关闭stdin，确保所有数据都被发送
    #         # 如果命令执行失败（returncode不为0），则打印stderr中的错误信息
    #         if result.returncode != 0:
    #             print("Java命令执行失败，错误信息如下：")
    #             print(result.stderr)  # 这里将直接打印出stderr中的字符串内容
    # except subprocess.CalledProcessError as e:
    #     # 当命令返回非零退出码时，subprocess.run会抛出CalledProcessError异常
    #     print(f"Java命令执行失败，返回码：{e.returncode}")
    #     print("错误信息如下：")
    #     print(e.stderr)  # 这里同样打印出stderr中的字符串内容
    # except Exception as e:
    #     # 处理其他可能的异常
    #     print(f"发生了一个错误：{e}")

compile_java("Main.java")
# 调用函数，传递输入文件路径
run_java_program("Main", "in.txt", "out.txt")