import os

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Language(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ProblemPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    solution = models.CharField(max_length=100,blank=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(ProblemPost, on_delete=models.CASCADE)
    code = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.author)+'·'+self.problem.title+'·'+self.status+'·'+str(self.created)


def input_file_upload_to(instance, filename):
    return os.path.join('input_file', str(instance.problem_id), filename)


def output_file_upload_to(instance, filename):
    return os.path.join('output_file', str(instance.problem_id), filename)


class TestData(models.Model):
    problem = models.ForeignKey(ProblemPost, on_delete=models.CASCADE)
    input_file = models.FileField(upload_to=input_file_upload_to, blank=True)
    output_file = models.FileField(upload_to=output_file_upload_to, blank=True)
    created = models.DateTimeField(default=timezone.now)
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.problem.title)+'·'+str(self.created)