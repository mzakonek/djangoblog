from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    PostLikeToogle,
    PostLikeAPIToogle,
    PostFavoriteAPIToogle,
    UserOwnListsView

)
from . import views



urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('user/<str:listtype>/', UserOwnListsView.as_view(), name='user-ownlists'),

    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/like', PostLikeToogle.as_view(), name='post-like_toogle'),
    path('api/post/<int:pk>/like', PostLikeAPIToogle.as_view(), name='post-like_api_toogle'),
    path('api/post/<int:pk>/favorite', PostFavoriteAPIToogle.as_view(), name='post-favorite_api_toogle'),

    path('about/', views.about, name='blog-about'),

]

