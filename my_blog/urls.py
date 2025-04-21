from django.contrib import admin
# 记得引入include
from django.urls import path, include
# 新引入的模块
from django.conf import settings
from django.conf.urls.static import static

from article.views import article_list
import notifications.urls
from home import views

# 存放映射关系的列表
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', article_list, name='home'),
    # 首页
    path('',views.home,name='index'),
    path('home/',include('home.urls', namespace='home')),
    # 新增代码，配置app的url
    path('article/', include('article.urls', namespace='article')),
    # onlinejudge
    path('oj/', include('oj.urls', namespace='oj')),
    # 聊天机器人
    path('chatrobot/', include('chatrobot.urls', namespace='chatrobot')),
    # 用户管理
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),
    path('password-reset/', include('password_reset.urls')),
    # 评论
    path('comment/', include('comment.urls', namespace='comment')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # notice
    path('notice/', include('notice.urls', namespace='notice')),
    path('video/',include('article.urls',namespace='video')),
]

#添加这行
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)