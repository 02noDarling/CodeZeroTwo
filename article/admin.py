from django.contrib import admin

from .models import ArticleColumn


# 别忘了导入ArticlerPost
from .models import ArticlePost

# 注册ArticlePost到admin中
admin.site.register(ArticlePost)

# 注册文章栏目
admin.site.register(ArticleColumn)