from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone


class Category(models.Model):
    """贴吧分类模型"""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """帖子模型"""
    title = models.CharField(max_length=200, verbose_name='帖子标题')
    content = models.TextField(verbose_name='帖子内容')
    author = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='所属分类')
    tags = models.JSONField(default=list, blank=True, verbose_name='标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览数')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    favorite_count = models.PositiveIntegerField(default=0, verbose_name='收藏数')
    is_pinned = models.BooleanField(default=False, verbose_name='是否置顶')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    is_draft = models.BooleanField(default=False, verbose_name='是否为草稿')
    
    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = '帖子'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """评论模型"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='所属帖子')
    author = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, 
                              related_name='replies', verbose_name='父评论')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.author.username} - {self.content[:20]}'


class UserProfile(models.Model):
    """用户扩展信息模型"""
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, verbose_name='用户')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    location = models.CharField(max_length=100, blank=True, verbose_name='所在地')
    join_date = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    post_count = models.PositiveIntegerField(default=0, verbose_name='发帖数')
    comment_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return self.user.username


class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name='用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, verbose_name='帖子')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, verbose_name='评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        unique_together = [('user', 'post'), ('user', 'comment')]
    
    def __str__(self):
        if self.post:
            return f'{self.user.username} 点赞了帖子: {self.post.title}'
        else:
            return f'{self.user.username} 点赞了评论: {self.comment.content[:20]}'


class Favorite(models.Model):
    """收藏模型"""
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name='用户')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='帖子')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = [('user', 'post')]
    
    def __str__(self):
        return f'{self.user.username} 收藏了帖子: {self.post.title}'