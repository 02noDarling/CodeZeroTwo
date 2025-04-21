from django.urls import path

from home import views

# 正在部署的应用的名称
app_name = 'home'

urlpatterns = [
    # # 目前还没有urls
    path('home/', views.home, name='home'),
]