from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, Post, Comment, UserProfile, Like, Favorite


def index(request):
    """首页 - 显示所有帖子和分类"""
    # 获取所有分类，并统计每个分类的帖子数量
    categories = Category.objects.annotate(post_count=Count('post', filter=Q(post__is_active=True)))
    
    # 获取查询参数
    sort = request.GET.get('sort', 'latest')
    category_id = request.GET.get('category')
    
    # 基础查询
    posts = Post.objects.filter(is_active=True)
    
    # 按分类筛选
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    # 排序逻辑
    if sort == 'hot':
        posts = posts.order_by('-view_count', '-like_count', '-created_at')
    elif sort == 'recommend':
        # 推荐算法：高浏览数 + 高点赞数 + 近期发布
        posts = posts.order_by('-view_count', '-like_count', '-created_at')
    else:  # latest
        posts = posts.order_by('-created_at')
    
    # 分页处理
    paginator = Paginator(posts, 12)  # 每页显示12个帖子
    page = request.GET.get('page', 1)
    
    try:
        posts_paginated = paginator.page(page)
    except PageNotAnInteger:
        posts_paginated = paginator.page(1)
    except EmptyPage:
        posts_paginated = paginator.page(paginator.num_pages)
    
    # 获取热门帖子（按浏览数排序，取前5个）
    hot_posts = Post.objects.filter(is_active=True).order_by('-view_count')[:5]
    
    # 网站统计数据
    total_posts = Post.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    
    context = {
        'categories': categories,
        'posts': posts_paginated,
        'hot_posts': hot_posts,
        'total_posts': total_posts,
        'total_users': total_users,
    }
    return render(request, 'tieba/index.html', context)


def category_posts(request, category_id):
    """显示特定分类下的帖子"""
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category, is_active=True).order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'category': category,
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'tieba/category_posts.html', context)


def post_detail(request, post_id):
    """帖子详情页"""
    post = get_object_or_404(Post, id=post_id, is_active=True)
    
    # 增加浏览数
    post.view_count += 1
    post.save()
    
    # 获取帖子的评论
    comments = Comment.objects.filter(post=post, is_active=True).order_by('created_at')
    
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'tieba/post_detail.html', context)


@login_required
def create_post(request):
    """创建新帖子"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content and category_id:
            category = get_object_or_404(Category, id=category_id)
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user,
                category=category
            )
            return redirect('tieba:post_detail', post_id=post.id)
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'tieba/create_post.html', context)


@login_required
def edit_post(request, post_id):
    """编辑帖子"""
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content and category_id:
            category = get_object_or_404(Category, id=category_id)
            post.title = title
            post.content = content
            post.category = category
            post.save()
            return redirect('tieba:post_detail', post_id=post.id)
    
    categories = Category.objects.all()
    context = {'post': post, 'categories': categories}
    return render(request, 'tieba/edit_post.html', context)


@login_required
def delete_post(request, post_id):
    """删除帖子"""
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.is_active = False
        post.save()
        return redirect('tieba:index')
    
    context = {'post': post}
    return render(request, 'tieba/delete_post.html', context)


@login_required
def create_comment(request, post_id):
    """创建评论"""
    post = get_object_or_404(Post, id=post_id, is_active=True)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            
            # 处理回复评论
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment
                comment.save()
            
            return redirect('tieba:post_detail', post_id=post.id)
    
    return redirect('tieba:post_detail', post_id=post.id)


@login_required
def delete_comment(request, comment_id):
    """删除评论"""
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post_id = comment.post.id
    
    if request.method == 'POST':
        comment.is_active = False
        comment.save()
    
    return redirect('tieba:post_detail', post_id=post_id)


@login_required
def like_post(request, post_id):
    """点赞帖子"""
    post = get_object_or_404(Post, id=post_id, is_active=True)
    
    # 检查是否已经点赞
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if not created:
        # 如果已经点赞，则取消点赞
        like.delete()
        post.like_count -= 1
        liked = False
    else:
        # 新点赞
        post.like_count += 1
        liked = True
    
    post.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count
        })
    
    return redirect('tieba:post_detail', post_id=post.id)


@login_required
def like_comment(request, comment_id):
    """点赞评论"""
    comment = get_object_or_404(Comment, id=comment_id, is_active=True)
    
    # 检查是否已经点赞
    like, created = Like.objects.get_or_create(
        user=request.user,
        comment=comment
    )
    
    if not created:
        # 如果已经点赞，则取消点赞
        like.delete()
        comment.like_count -= 1
        liked = False
    else:
        # 新点赞
        comment.like_count += 1
        liked = True
    
    comment.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': comment.like_count
        })
    
    return redirect('tieba:post_detail', post_id=comment.post.id)


def user_profile(request, username):
    """用户资料页"""
    user = get_object_or_404(User, username=username)
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    
    # 获取用户的帖子和评论
    user_posts = Post.objects.filter(author=user, is_active=True).order_by('-created_at')
    user_comments = Comment.objects.filter(author=user, is_active=True).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_comments': user_comments,
    }
    return render(request, 'tieba/user_profile.html', context)


@login_required
def edit_profile(request):
    """编辑用户资料"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        
        user_profile.bio = bio
        user_profile.location = location
        
        # 处理头像上传
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']
        
        user_profile.save()
        return redirect('tieba:user_profile', username=request.user.username)
    
    context = {'user_profile': user_profile}
    return render(request, 'tieba/edit_profile.html', context)


def search_posts(request):
    """搜索帖子"""
    query = request.GET.get('q', '').strip()
    
    if query:
        # 搜索标题和内容中包含关键词的帖子
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_active=True
        ).order_by('-created_at')
    else:
        posts = Post.objects.filter(is_active=True).order_by('-created_at')
    
    # 获取所有分类
    categories = Category.objects.annotate(post_count=Count('post', filter=Q(post__is_active=True)))
    
    # 获取热门帖子（按浏览数排序，取前5个）
    hot_posts = Post.objects.filter(is_active=True).order_by('-view_count')[:5]
    
    # 分页处理
    paginator = Paginator(posts, 12)
    page = request.GET.get('page', 1)
    
    try:
        posts_paginated = paginator.page(page)
    except PageNotAnInteger:
        posts_paginated = paginator.page(1)
    except EmptyPage:
        posts_paginated = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts_paginated,
        'categories': categories,
        'hot_posts': hot_posts,
        'query': query,
        'total_results': posts.count() if query else 0,
    }
    
    return render(request, 'tieba/search_results.html', context)


@login_required
def favorite_post(request, post_id):
    """收藏帖子"""
    post = get_object_or_404(Post, id=post_id, is_active=True)
    
    # 检查是否已经收藏
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if not created:
        # 如果已经收藏，则取消收藏
        favorite.delete()
        post.favorite_count -= 1
        favorited = False
    else:
        # 新收藏
        post.favorite_count += 1
        favorited = True
    
    post.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'favorited': favorited,
            'favorite_count': post.favorite_count
        })
    
    return redirect('tieba:post_detail', post_id=post.id)


def register(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 自动登录用户
            login(request, user)
            # 创建用户资料
            UserProfile.objects.create(user=user)
            return redirect('tieba:index')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'tieba/register.html', context)