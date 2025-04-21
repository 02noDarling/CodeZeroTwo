from django.contrib import admin

# 别忘了导入ArticlerPost
from .models import ProblemPost, Language,Submission,TestData

# 注册ArticlePost到admin中
admin.site.register(ProblemPost)
admin.site.register(Language)
admin.site.register(Submission)
admin.site.register(TestData)