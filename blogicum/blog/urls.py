from django.urls import path, include

from . import views

app_name = 'blog'

post_urls = [
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        '<int:pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:pk>/comment/',
        views.CreateComment.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.UpdateComment.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.DeleteComment.as_view(),
        name='delete_comment'
    ),
]

profile_urls = [
    path(
        'edit/',
        views.UpdateProfileView.as_view(),
        name='edit_profile'
    ),
    path('<str:username>/', views.profile_user, name='profile'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', include(post_urls)),
    path(
        'category/<slug:category_slug>/',
        views.category_posts, name='category_posts'
    ),
    path(
        'profile-edit/',
        views.UpdateProfileView.as_view(),
        name='edit_profile'
    ),
    path('profile/<str:username>/', views.profile_user, name='profile'),
]
