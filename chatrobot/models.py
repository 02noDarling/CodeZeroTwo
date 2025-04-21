from django.db import models
# 导入内建的User模型。
from django.contrib.auth.models import User
# timezone 用于处理时间相关事务。
from django.utils import timezone

# 博客文章数据模型
class ChatPost(models.Model):
    # 文章作者。参数 on_delete 用于指定数据删除的方式
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章正文。保存大量文本使用 TextField
    problem = models.TextField()
    answer = models.TextField()
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return str(self.user)+str(self.created)