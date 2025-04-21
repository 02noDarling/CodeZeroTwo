
# 引入path
from django.urls import path

from chatrobot import views

# 正在部署的应用的名称
app_name = 'chatrobot'

urlpatterns = [
    path('chat-list/', views.chat_list, name='chat_list'),
    path('chatrobot/', views.chatbot, name='chatrobot'),
]