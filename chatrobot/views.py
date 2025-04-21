import json

import requests
from django.http import HttpResponse

from userprofile.models import Profile
from django.shortcuts import render,redirect
# 导入数据模型ArticlePost
from .models import ChatPost
from django.db.models import Q
import markdown
import subprocess
import os

API_KEY = "FAClUPFPOXbUeRenNHNeCV1y"
SECRET_KEY = "qhNhYWCCcphILktjbeQKziHkHcJddTI6"
# 视图函数
def chat_list(request):
    # 取出所有博客文章
    if not request.user.is_authenticated:
        chats=""
        profile=""
    else:
        chats = ChatPost.objects.filter(user=request.user)
        profile=Profile.objects.filter(user_id=request.user.id).first()
    # # 需要传递给模板（templates）的对象
    answer_id = request.session.get('answer_id', None)
    if answer_id != None:
        answer_body=ChatPost.objects.get(id=answer_id).answer
    else:
        answer_body=None
    if 'answer_id' in request.session:
        del request.session['answer_id']
    print(answer_id,answer_body)
    context = { 'chats': chats ,'profile': profile,'answer_id':answer_id,'answer_body':answer_body}
    # render函数：载入模板，并返回context对象
    return render(request, 'chatrobot/list.html',context)

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def chatbot(request):
    input=request.POST['input']
    print(input)
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + get_access_token()
    # 注意message必须是奇数条
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": input
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    res = requests.request("POST", url, headers=headers, data=payload).json()
    result=res['result']
    result=result.replace('\n', '')
    chat=ChatPost(user=request.user,problem=input,answer=result)
    chat.save()
    redirect_url = "/chatrobot/chat-list/" + '#chat_elem_' + str(chat.id)
    request.session['answer_id'] = chat.id
    return redirect(redirect_url)
    # chats = ChatPost.objects.filter(user=request.user)
    # profile = Profile.objects.filter(user_id=request.user.id).first()
    # context = {'chats': chats,'profile': profile}
    # # render函数：载入模板，并返回context对象
    # return render(request, 'chatrobot/list.html', context)

