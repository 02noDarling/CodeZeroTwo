from django.shortcuts import render

# 导入数据模型ArticlePost
from .models import ArticlePost
import markdown
# 引入redirect重定向模块
from django.shortcuts import render, redirect
# 引入HttpResponse
from django.http import HttpResponse
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象
from django.db.models import Q
from comment.models import Comment
from .models import ArticleColumn
# 引入评论表单
from comment.forms import CommentForm

# 重写文章列表
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    # 用户搜索逻辑
    if search:
        if order == 'total_views':
            # 用 Q对象 进行联合搜索
            article_list = ArticlePost.objects.filter(
                (Q(title__icontains=search) | Q(body__icontains=search)) &
                (Q(file__isnull=True)|Q(file=""))
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                (Q(title__icontains=search) | Q(body__icontains=search)) &
                (Q(file__isnull=True) | Q(file=""))
            )
    else:
        # 将 search 参数重置为空
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(Q(file__isnull=True)| Q(file="")).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(Q(file__isnull=True)| Q(file=""))

    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 增加 search 到 context
    context = { 'articles': articles, 'order': order, 'search': search }

    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 修改 Markdown 语法渲染
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    # 引入评论表单
    comment_form = CommentForm()
    # 新增了md.toc对象
    context = {'article': article, 'toc': md.toc, 'comments': comments,'comment_form': comment_form}

    return render(request, 'article/detail.html', context)

# 写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            # 新增的代码
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文
        # 新增及修改的代码
        columns = ArticleColumn.objects.all()
        context = { 'article_post_form': article_post_form, 'columns': columns }
        # 返回模板
        return render(request, 'article/create.html', context)

# 删文章
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")

# 安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

# 更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            # 新增的代码
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 新增及修改的代码
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
        }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)

def video_list(request):
    if request.GET.get('order') == 'total_views':
        video_list = ArticlePost.objects.filter(Q(file__isnull=False) & ~Q(file="")).order_by('-total_views')
        order = 'total_views'
    else:
        video_list = ArticlePost.objects.filter(Q(file__isnull=False)& ~Q(file=""))
        order = 'normal'
    paginator = Paginator(video_list, 12)
    page = request.GET.get('page')
    videos = paginator.get_page(page)
    context = {'videos': videos, 'order':order}
    return render(request, 'video/list.html', context)

def video_detail(request,id):
    video = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    video.total_views+=1
    video.save(update_fields=['total_views'])

    #相邻视频
    relate_video = ArticlePost.objects.filter(classification=video.classification).order_by('total_views')
    if relate_video.count() <= 1 :
        relate_video = None
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    video.body = md.convert(video.body)
    comment_form = CommentForm()
    context = {
        "video" :video,
        'relate_video' : relate_video,
        'comments' : comments,
        'comment_form': comment_form,
    }
    if relate_video:
        print(relate_video[0].title)
    return render(request, 'video/detail.html',context)

# def article_detail(request, id):
#     article = ArticlePost.objects.get(id=id)
#     # 取出文章评论
#     comments = Comment.objects.filter(article=id)
#     # 浏览量 +1
#     article.total_views += 1
#     article.save(update_fields=['total_views'])
#     # 修改 Markdown 语法渲染
#     md = markdown.Markdown(
#         extensions=[
#             'markdown.extensions.extra',
#             'markdown.extensions.codehilite',
#             'markdown.extensions.toc',
#         ]
#     )
#     article.body = md.convert(article.body)
#     # 引入评论表单
#     comment_form = CommentForm()
#     # 新增了md.toc对象
#     context = {'article': article, 'toc': md.toc, 'comments': comments,'comment_form': comment_form}
#
#     return render(request, 'article/detail.html', context)
