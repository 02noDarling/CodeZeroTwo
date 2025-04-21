# 导入 HttpResponse 模块
import platform

from django.core.paginator import Paginator
from django.http import HttpResponse

from django.shortcuts import render
# 导入数据模型ArticlePost
from .models import ProblemPost,Language,Submission,TestData
from django.db.models import Q
import markdown
import subprocess
import os
# import psutil
# import signal
import time
import threading
from subprocess import Popen, PIPE, TimeoutExpired
# 视图函数
def problem_list(request):
    search = request.GET.get('search')
    print(search)
    # 取出所有博客文章
    if search:
        problems_list = ProblemPost.objects.filter(
            (Q(title__icontains=search) | Q(body__icontains=search))
        )
    else:
        # 将 search 参数重置为空
        search = ''
        problems_list = ProblemPost.objects.all()

    paginator = Paginator(problems_list, 10)
    # 获取 url 中的页码
    # 将导航对象相应的页码内容返回给 articles
    page = request.GET.get('page')
    problems = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = { 'problems': problems,'search':search }
    # render函数：载入模板，并返回context对象
    return render(request, 'oj/list.html', context)

# 文章详情
def problem_detail(request, id):
    # 取出相应的文章
    languages=Language.objects.all()
    problem = ProblemPost.objects.get(id=id)
    # 将markdown语法渲染成html样式
    problem.body = markdown.markdown(problem.body,
     extensions=[
         # 包含 缩写、表格等常用扩展
         'markdown.extensions.extra',
         # 语法高亮扩展
         'markdown.extensions.codehilite',
     ])
    # 需要传递给模板的对象
    context = { 'problem': problem ,'status':"None",'user_code':"",'languages':languages,'input':"",'output':"None"}
    # 载入模板，并返回context对象
    return render(request, 'oj/detail.html', context)

def post_code(request, id):
    send=request.POST['functionToCall']
    input=request.POST['input']
    if send=='提交代码':
        problem = ProblemPost.objects.get(id=id)
        author = request.user
        user_code = request.POST['body']
        language = request.POST['language']
        # 将markdown语法渲染成html样式
        problem.body = markdown.markdown(problem.body,
         extensions=[
             # 包含 缩写、表格等常用扩展
             'markdown.extensions.extra',
             # 语法高亮扩展
             'markdown.extensions.codehilite',
         ])
        if language=='none':
            languages = Language.objects.all()
            context = {'problem': problem, 'status': 'None', 'user_code': user_code, 'languages': languages,
                       'type': language, 'input': input, 'output': "None"}
            # 载入模板，并返回context对象
            return render(request, 'oj/detail.html', context)
        if language=='c++':
            code_file = "usercode/"+language+"/main.cpp"  # 源文件
            exe_file = "usercode/" + language + "/main.exe"  # 你想要生成的可执行文件（在 Windows 上）
        elif language=='java':
            code_file = "usercode/" + language + "/Main.java"  # 源文件
            exe_file = "usercode/" + language + "/Main.java"  # 你想要生成的可执行文件（在 Windows 上）
        elif language=='python':
            code_file = "usercode/" + language + "/main.py"  # 源文件
            exe_file = "usercode/" + language + "/main.py"  # 你想要生成的可执行文件（在 Windows 上）
        # input_file = "problem_in_ans/1/in/in.txt"
        # output_file = "usercode/"+language+"/out/out.txt"  # 输出文件
        # ans_file="problem_in_ans/1/ans/ans.txt"

        output_file = "usercode/" + language + "/out/out.txt"  # 输出文件
        with open(code_file, 'w') as file:
            file.write(user_code)
            # 需要传递给模板的对象
        if language != 'python':
            is_compile_fail = compile_code(code_file, exe_file, output_file, language)
            print("NNN", is_compile_fail)
        else:
            is_compile_fail = False
        if is_compile_fail:
            status = "Compile Error"
        else:
            data_files=TestData.objects.filter(problem=problem)
            print(data_files)
            status="Accept"
            for data_file in data_files:
                input_file='media/'+str(data_file.input_file)
                ans_file='media/'+str(data_file.output_file)
                print(input_file)
                print(ans_file)
                # run_exe_with_redirect_and_timeout(exe_file, input_file, output_file,1)
                run_exe_with_redirect(exe_file, input_file, output_file,language)
                result = compare_files(output_file, ans_file)
                if  not result:
                    status = "Wrong Answer"
                    break
        # with open(code_file, 'w') as file:
        #     file.write(user_code)
        #     # 需要传递给模板的对象
        # if language!='python':
        #     is_compile_fail=compile_code(code_file, exe_file,output_file,language)
        #     print("NNN",is_compile_fail)
        # else:
        #     is_compile_fail=False
        # if is_compile_fail:
        #     status = "Compile Error"
        # else:
        #     # run_exe_with_redirect_and_timeout(exe_file, input_file, output_file,1)
        #     run_exe_with_redirect(exe_file, input_file, output_file,language)
        #     result = compare_files(output_file, ans_file)
        #     if result:
        #         status = "Accept"
        #     else:
        #         status = "Wrong Answer"
        #清空输出out.txt
        # if os.path.exists(output_file):
        #     os.remove(output_file)
        # with open(output_file, 'w') as f:
        #     pass
        languages=Language.objects.all()
        if status=='Accept':
            color='green'
        elif status=='Wrong Answer' or status=='Compile Error':
            color='red'
        elif status=='None':
            color='black'
        elif status=='Debugging successful':
            color='blue'
        else:
            color='black'
        submission = Submission(author=author, problem=problem, code=user_code,status=status,language=language)
        submission.save()
        context = {'problem': problem,'status':status,'user_code':user_code,'languages':languages,'type':language,'input':input,'output':"None",'color':color}
        # 载入模板，并返回context对象
        return render(request, 'oj/detail.html', context)
    elif send=='调试代码':
        output="None"
        problem = ProblemPost.objects.get(id=id)
        # 将markdown语法渲染成html样式
        problem.body = markdown.markdown(problem.body,
         extensions=[
             # 包含 缩写、表格等常用扩展
             'markdown.extensions.extra',
             # 语法高亮扩展
             'markdown.extensions.codehilite',
         ])
        user_code = request.POST['body']
        language = request.POST['language']
        if language=='none':
            languages = Language.objects.all()
            context = {'problem': problem, 'status': 'None', 'user_code': user_code, 'languages': languages,
                       'type': language, 'input': input, 'output': "None"}
            # 载入模板，并返回context对象
            return render(request, 'oj/detail.html', context)
        if language == 'c++':
            code_file = "usercode/" + language + "/main.cpp"  # 源文件
            exe_file = "usercode/" + language + "/main.exe"  # 你想要生成的可执行文件（在 Windows 上）
        elif language == 'java':
            code_file = "usercode/" + language + "/Main.java"  # 源文件
            exe_file = "usercode/" + language + "/Main.java"  # 你想要生成的可执行文件（在 Windows 上）
        elif language == 'python':
            code_file = "usercode/" + language + "/main.py"  # 源文件
            exe_file = "usercode/" + language + "/main.py"  # 你想要生成的可执行文件（在 Windows 上）
        input_file = "usercode/" + language + "/in/in.txt"
        output_file = "usercode/" + language + "/out/out.txt"  # 输出文件
        ans_file = "problem_in_ans/1/ans/ans.txt"
        with open(code_file, 'w') as file:
            file.write(user_code)
            # 需要传递给模板的对象
        with open(input_file, 'w') as file:
            file.write(input)
        if language != 'python':
            is_compile_fail = compile_code(code_file, exe_file,output_file, language)
            print("NNN", is_compile_fail)
        else:
            is_compile_fail = False
        if is_compile_fail:
            status = "Compile Error"
            with open(output_file, 'r', encoding='utf-8') as file:  # 你可以根据需要更改编码，比如'utf-8', 'gbk'等
                output = file.read()  # 读取文件全部内容并存储在output字符串中
        else:
            # run_exe_with_redirect_and_timeout(exe_file, input_file, output_file,1)
            status="Debugging successful"
            run_exe_with_redirect(exe_file, input_file, output_file, language)
            with open(output_file, 'r', encoding='utf-8') as file:  # 你可以根据需要更改编码，比如'utf-8', 'gbk'等
                output = file.read()  # 读取文件全部内容并存储在output字符串中

        # 清空输出out.txt
        # if os.path.exists(output_file):
        #     os.remove(output_file)
        # with open(output_file, 'w') as f:
        #     pass
        languages = Language.objects.all()
        if status=='Accept':
            color='green'
        elif status=='Wrong Answer' or status=='Compile Error':
            color='red'
        elif status=='None':
            color='black'
        elif status=='Debugging successful':
            color='blue'
        else:
            color = 'black'
        context = {'problem': problem, 'status': status, 'user_code': user_code, 'languages': languages,
                   'type': language, 'input': input, 'output': output,'color':color}
        # 载入模板，并返回context对象
        return render(request, 'oj/detail.html', context)

def compile_code(code_file, exe_file,output_file,language):
    if language=='c++':
        # 假设你的 C++ 文件没有依赖项，并且在一个简单的命令行中可以编译
        # 注意：这个命令是特定于 Unix-like 系统的（如 Linux 或 macOS）
        # 如果你在 Windows 上，你可能需要使用 'g++' 而不是 'g++ -o'

        command = [r'E:\devc++\Dev-Cpp\MinGW64\bin\g++.exe', code_file, '-o', exe_file]
        returncode = 0
        try:
            # 尝试编译C++文件
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            # 如果check=True且没有异常，说明编译成功
            print(f"Successfully compiled {code_file} to {exe_file}")
            # 如果需要，可以打印编译器的输出
            print(f"Stdout:\n{result.stdout}")
            print(f"Stderr:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            # 捕获CalledProcessError异常，说明编译失败
            returncode=e.returncode
            print(f"Compilation failed with error code {e.returncode}")
            # 打印编译器的错误输出
            print(f"Stderr:\n{e.stderr}")
            with open(output_file, 'w') as file:
                file.write(e.stderr)

        return returncode
    elif language=='java':
        try:
            subprocess.check_call([r'E:\jdk-17\bin\javac', "--version"])
        except subprocess.CalledProcessError:
            print("Error: javac is not installed or not in PATH.")
            return
        returncode = 0
            # 编译 Java 文件
        # try:
        #     subprocess.check_call([r'E:\jdk-17\bin\javac', code_file],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #     print(f"Successfully compiled {code_file}")
        # except subprocess.CalledProcessError as e:
        #     print(f"Error compiling {code_file}: {e}")
        #     with open(output_file, 'w') as file:
        #         file.write(e.stderr.decode())
        #     returncode=e.returncode
        # return returncode
        try:
            result = subprocess.run([r'E:\jdk-17\bin\javac', code_file],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    check=True,
                                    universal_newlines=True)  # 使用universal_newlines将输出作为字符串处理
            print(f"Successfully compiled {code_file}")
            return 0  # 返回零值表示成功
        except subprocess.CalledProcessError as e:
            print(f"Error compiling {code_file}: {e}")
            # 写入错误输出到文件
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(e.stderr)  # 因为使用了universal_newlines，e.stderr已经是字符串了
            return e.returncode  # 返回非零的错误码


def run_exe_with_redirect(exe_file, input_file, output_file,language):
    if language=='c++':
        # 确保所有文件都存在且可执行（对于exe_file）
        if not os.path.exists(exe_file) or not os.access(exe_file, os.X_OK):
            raise FileNotFoundError(f"Executable file not found or not executable: {exe_file}")
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

            # 尝试执行命令，但避免使用shell（如果可能）
        # 注意：由于我们在这里使用重定向，所以我们必须使用shell=True
        command = f'"{exe_file}" < "{input_file}" > "{output_file}"'

        try:
            subprocess.run(command, shell=True, check=True, text=True,
                           universal_newlines=True)  # universal_newlines 是 text 的旧名称
            print(f"Successfully executed {exe_file} with output redirected to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Execution failed with error code {e.returncode}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    elif language=='java':
        print(exe_file, input_file, output_file,language)
        with open(output_file, 'wb') as outfile:  # 使用'wb'模式以二进制形式写入
            # 使用Popen启动Java程序，并将stdout重定向到outfile
            java_process = subprocess.Popen(['java', exe_file], stdin=subprocess.PIPE, stdout=outfile,
                                            stderr=subprocess.PIPE)

            # 打开in.txt文件以读取内容，并通过PIPE传递给Java的stdin
            with open(input_file, 'r') as infile:
                # 将in.txt的内容传递给Java程序的stdin
                java_process.stdin.write(infile.read().encode())  # 将字符串编码为字节串
                java_process.stdin.close()  # 关闭stdin，确保所有数据都被发送

            # 等待Java程序完成并获取stderr（如果有的话）
            _, stderr = java_process.communicate()

            # 如果Java程序正常结束，stdout已经被写入到out.txt中
            # 否则，处理stderr中的错误信息
            if java_process.returncode != 0:
                print("Java error:")
                # print(stderr.decode())
    elif language=='python':
        python_interpreter = r'C:\Users\DELL\AppData\Local\Programs\Python\Python39\python.exe'  # 或者 'python3'
        with open(input_file, 'r') as input_file, open(output_file, 'w') as output_file:
            # 使用Popen来启动子进程，stdin和stdout使用管道
            process = subprocess.Popen([python_interpreter, exe_file],
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


def kill_process(proc, timeout_event):
    # 等待超时事件
    timeout_event.wait()
    if proc.poll() is None:
        # 如果进程仍在运行，则杀死它
        proc.kill()

flag=False
event=threading.Event()
def judge_process(command,event):
    global flag
    if not flag:
        try:
            subprocess.run(command, shell=True, check=True, text=True,
                           universal_newlines=True)  # universal_newlines 是 text 的旧名称
            event.set()
            # print(f"Successfully executed {exe_file} with output redirected to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Execution failed with error code {e.returncode}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("TTLE\n\n\n\n\n\n")
def terminate_process(process_name,event):
    time.sleep(3)
    # for proc in psutil.process_iter(['name']):
    #     if proc.info['name'] == process_name:
    #         proc.kill()
    global flag
    flag = True
    event.set()
    print('TLE\n\n\n\n\n\n')

    # thread.join(0)


# def run_exe_with_redirect_and_timeout(exe_file, input_file, output_file, timeout=1):
#     # 确保所有文件都存在且可执行（对于exe_file）
#     if not os.path.exists(exe_file) or not os.access(exe_file, os.X_OK):
#         raise FileNotFoundError(f"Executable file not found or not executable: {exe_file}")
#     if not os.path.exists(input_file):
#         raise FileNotFoundError(f"Input file not found: {input_file}")
#
#
#
#         # 尝试执行命令，但避免使用shell（但由于重定向，这里需要使用shell）
#     command = f'"{exe_file}" < "{input_file}" > "{output_file}"'
#     global flag
#     flag = False
#     event = threading.Event()
#     thread_1=threading.Thread(target=judge_process(command,event))
#     thread_2=threading.Thread(target=terminate_process('main.exe',event))
#
#     thread_1.start()
#     thread_2.start()
#
#     thread_1.join()
#     thread_2.join()
#     for proc in psutil.process_iter(['name']):
#         if proc.info['name'] == 'main.exe':
#             proc.kill()
#
#     # universal_newlines 是 text 的旧名称
#
#     # try:
#     #     # 使用Popen创建进程，而不是直接运行
#     #     proc = subprocess.Popen(command, shell=True, text=True, universal_newlines=True)
#     #
#     #     # 设置超时事件
#     #     timeout_event = threading.Event()
#     #     # 设置一个守护线程来监控超时
#     #     timer = threading.Timer(timeout, kill_process, args=(proc, timeout_event))
#     #     timer.start()
#     #
#     #     # 等待进程完成
#     #     proc.communicate()
#     #
#     #     # 取消超时事件，以防它在进程完成之前触发
#     #     timeout_event.set()
#     #
#     #     # 等待守护线程完成（尽管由于它是守护线程，它应该会在主线程退出时自动清理）
#     #     timer.join()
#     #
#     #     if proc.returncode == 0:
#     #         print(f"Successfully executed {exe_file} with output redirected to {output_file}")
#     #     else:
#     #         print(f"Execution failed with error code {proc.returncode}")
#     #
#     # except subprocess.CalledProcessError as e:
#     #     print(f"Execution failed with error code {e.returncode}")
#     # except Exception as e:
#     #     print(f"An unexpected error occurred: {e}")
#     # finally:
#     #     # 确保关闭timer（尽管它通常会在主线程退出时自动清理）
#     #     timer.cancel()

def compare_files(file1, file2):
    # with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
    #     # 读取两个文件的所有行到列表中
    #     lines1 = f1.readlines()
    #     lines2 = f2.readlines()
    #     print(lines1)
    #     print(lines2)
    #     # 比较两个列表是否相等（包括内容和顺序）
    #     if lines1 == lines2:
    #         return True
    #     else:
    #         return False
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        # 读取两个文件的所有行到列表中，并去除每行末尾的空格
        lines1 = [line.rstrip() for line in f1 if line.strip()]
        lines2 = [line.rstrip() for line in f2 if line.strip()]
        print(lines1)
        print(lines2)
        # 比较两个列表是否相等（包括内容和顺序，但不包括行末空格）
        if lines1 == lines2:
            return True
        else:
            return False

def submission_list(request,id):
    problem=ProblemPost.objects.get(id=id)
    submissions=Submission.objects.filter(
                Q(author=request.user) & Q(problem=problem)
            )
    context = {'submissions':submissions}
    return render(request, 'oj/submission_list.html', context)

def submission_detail(request,id):
    submission=Submission.objects.get(id=id)
    context = {'submission':submission}
    return render(request, 'oj/submission_detail.html', context)