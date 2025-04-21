from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# 记得导入
from django.urls import reverse
from PIL import Image


class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章栏目的 “一对多” 外键
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    total_views = models.PositiveIntegerField(default=0)
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)

    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)

        if self.cover and not kwargs.get('update_fields'):
            image = Image.open(self.cover)
            (x, y) = image.size
            new_x = 400
            new_y = 225
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.cover.path)

        return article
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    # 获取文章地址
    def get_absolute_url(self):
        if self.file == None or self.file=='':
            return reverse('article:article_detail', args=[self.id])
        else:
            return reverse('video:video_detail', args=[self.id])

    file =models.FileField(upload_to='video/%Y%m%d/',max_length=255,null=True,blank=True)
    descripton=models.CharField(max_length=255,blank=True,null=True)
    classification = models.CharField(max_length=100, blank=True, null=True)
    cover = models.ImageField(upload_to='cover/%Y%m%d/', blank=True)

@property
def img_url(self):
    if self.cover and hasattr(self.img, 'url'):
        return self.cover.url
