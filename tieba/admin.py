from django.contrib import admin
from .models import Category, Post, Comment, UserProfile, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'view_count', 'like_count', 'is_pinned', 'is_active']
    search_fields = ['title', 'content']
    list_filter = ['category', 'created_at', 'is_pinned', 'is_active']
    date_hierarchy = 'created_at'
    readonly_fields = ['view_count', 'like_count']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content', 'created_at', 'like_count', 'is_active']
    search_fields = ['content']
    list_filter = ['created_at', 'is_active']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'join_date', 'post_count', 'comment_count']
    search_fields = ['user__username', 'location']
    list_filter = ['join_date']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'comment', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'