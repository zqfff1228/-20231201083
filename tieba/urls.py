from django.urls import path
from . import views

app_name = 'tieba'

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    
    # 分类相关
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    
    # 帖子相关
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
    # 评论相关
    path('post/<int:post_id>/comment/', views.create_comment, name='create_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # 点赞相关
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    
    # 收藏相关
    path('post/<int:post_id>/favorite/', views.favorite_post, name='favorite_post'),
    
    # 用户相关
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/', views.profile, name='profile'),
    
    # 搜索相关
    path('search/', views.search_posts, name='search'),
    
    # 用户注册
    path('register/', views.register, name='register'),
]