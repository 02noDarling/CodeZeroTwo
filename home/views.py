import json

import requests
from django.http import HttpResponse

from userprofile.models import Profile
from django.shortcuts import render
# 导入数据模型ArticlePost
from article.models import ArticlePost
from oj.models import ProblemPost
from django.db.models import Q
import markdown
import subprocess
import os

def home(request):
    # print(request.session.get('session_name'))
    # 新闻展报
    # newList = MyNew.objects.all().filter(~Q(
    #     newType='通知公告')).order_by('-publishDate')
    articles = ArticlePost.objects.filter(Q(file__isnull=True) | Q(file=""))
    postList = set()
    postNum = 0
    for s in articles:
        if s.avatar:
            postList.add(s)
            postNum += 1
        if postNum == 3:  # 只截取最近的3个展报
            break
    print(postList)
    # 新闻列表
    if (len(articles) > 7):
        articles = articles[0:7]
    problems=ProblemPost.objects.all()
    if (len(problems) > 7):
       problems = problems[0:7]
    # 返回结果
    return render(request, 'home/home.html', {
        'postList': postList,
        'articles': articles,
        'problems':problems,
    })

