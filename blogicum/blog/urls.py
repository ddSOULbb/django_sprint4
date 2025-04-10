from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Основные маршруты
    path('', views.PostListView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsView.as_view(), name='category_posts'),

    # Работа с постами
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('create/',
         views.CreatePostView.as_view(), name='create_post'),
    path('posts/<int:pk>/delete/',
         views.DeletePostView.as_view(), name='delete_post'),
    path('posts/<int:pk>/edit/',
         views.EditPostView.as_view(), name='edit_post'),

    # Комментарии
    path('posts/<int:pk>/comment/',
         views.AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/',
         views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/',
         views.DeleteCommentView.as_view(), name='delete_comment'),

    # Пользовательские маршруты
    path('profile/edit/',
         views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/',
         views.ProfileView.as_view(), name='profile'),
    path('auth/registration/',
         views.RegisterView.as_view(), name='register'),
]
