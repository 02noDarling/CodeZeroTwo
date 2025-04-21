# 引入path
from django.urls import path
from . import views
# 正在部署的应用的名称
app_name = 'oj'

urlpatterns = [
    # path函数将url映射到视图
    path('problem-list/', views.problem_list, name='problem_list'),
    # 文章详情
    path('problem-detail/<int:id>/', views.problem_detail, name='problem_detail'),
    # 提交代码
    path('post-code/<int:id>/', views.post_code, name='post_code'),
    path('submission-list/<int:id>/', views.submission_list, name='submission_list'),
    path('submission-detail/<int:id>/', views.submission_detail, name='submission_detail'),
]