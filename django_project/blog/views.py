from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    RedirectView
)
from .models import Post
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # by default it looks for <app>/<model>_<viewtype>.html
    context_object_name = 'posts'  # to behave the same as in the previous function based view (fit the template)
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # by default it looks for <app>/<model>_<viewtype>.html
    context_object_name = 'posts'  # to behave the same as in the previous function based view (fit the template)
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostLikeToogle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        print(self.kwargs.get('pk'))
        obj = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated and obj.author != user:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_


class PostLikeAPIToogle(APIView):

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None, format=None):
        # pk=self.kwargs.get('pk')
        obj = get_object_or_404(Post, pk=pk)
        url_ = obj.get_absolute_url()
        user = self.request.user
        updated = False
        liked = False

        if user.is_authenticated and obj.author != user:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
                liked = True
            updated = True

        data = {
            'updated': updated,
            'liked': liked
        }
        return Response(data)


def about(request):
    return render(request, 'blog/about.html')


# def like(request):
#     if request.method == 'GET':
#         post_id = request.GET['post_id']
#         likedpost = Post.objects.get(id=post_id)
#         m = Like(post=likedpost)
#         m.save()
#         return HttpResponse('success')
#     else:
#         return HttpResponse("unsuccesful")