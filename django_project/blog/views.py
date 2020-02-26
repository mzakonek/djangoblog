from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseServerError
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    RedirectView
)
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json
from .models import Post, Favoritepost
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
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class UserOwnListsView(ListView):
    # TODO: check if this approach is better than having two seperated classes for Likes and Favorites
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        if self.kwargs.get('listtype') == 'favorites':
            return [favpost.post for favpost in user.favorite_posts.order_by('order')]
        return user.post_likes.order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(UserOwnListsView, self).get_context_data(**kwargs)
        context['list_type_header'] = self.kwargs.get('listtype')
        return context


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


class PostFavoriteAPIToogle(APIView):
    # TODO: I don't like the idea of having "PostLikeAPIToogle" and "PostFavoriteAPIToogle" almost the same
    #  and duplicated. It should be different

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None, format=None):
        # pk=self.kwargs.get('pk')
        obj = get_object_or_404(Post, pk=pk)
        user = self.request.user
        updated = False
        favorited = False

        if user.is_authenticated and obj.author != user:
            if user in obj.favorites.all():
                obj.favorites.remove(user)
            else:
                obj.favorites.add(user)
                favorited = True
            updated = True

        data = {
            'updated': updated,
            'favorited': favorited
        }
        return Response(data)


def about(request):
    return render(request, 'blog/about.html')


class FavoritePostsReorder(View):
    template_name = "blog/favorite_posts_reorder.html"

    # Ensure we have a CSRF cooke set
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        user_pk = self.request.user.pk
        return render(
            self.request,
            self.template_name,
            {'favoriteposts': Favoritepost.objects.filter(user_id=user_pk).order_by('order')}
        )

    # Process POST AJAX Request
    def post(self, request):
        if request.method == "POST" and request.is_ajax():
            try:
                # Parse the JSON payload
                data = json.loads(request.body)[0]
                print(json.loads(request.body))
                # Loop over our list order. The id equals the question id. Update the order and save
                for idx, favpost_repr in enumerate(data):
                    favpost = Favoritepost.objects.get(id=favpost_repr["id"])
                    favpost.order = idx + 1
                    favpost.save()

            except KeyError:
                HttpResponseServerError("Malformed data!")

            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"success": False}, status=400)

