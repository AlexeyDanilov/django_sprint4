from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm


User = get_user_model()


def get_base_queryset():
    return Post.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True
    ).prefetch_related('comments')


def index(request):
    post_list = get_base_queryset().annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request=request,
        template_name='blog/index.html',
        context={'page_obj': page_obj}
    )


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(
        request=request,
        template_name='blog/detail.html',
        context={
            'post': post,
            'form': CommentForm(),
            'comments': post.comments.all()
        }
    )


def category_posts(request, category_slug):
    context = dict()
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_base_queryset().filter(category=category).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(
        request=request,
        template_name='blog/category.html',
        context=context
    )


def profile_user(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.annotate(
        comment_count=Count('comments')).order_by('-pub_date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email', )

    def dispatch(self, request, *args: Any, **kwargs: Any):
        get_object_or_404(User, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def dispatch(self, request, *args: Any, **kwargs: Any):
        post = get_object_or_404(Post, pk=kwargs.get('pk'))
        if post.author != request.user:
            return redirect('blog:post_detail', self.get_object().pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.get_object().id}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template = 'blog/create.html'

    def dispatch(self, request, *args: Any, **kwargs: Any):
        if request.user.id:
            get_object_or_404(Post, pk=kwargs.get('pk'), author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CreateComment(LoginRequiredMixin, CreateView):
    _post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args: Any, **kwargs: Any):
        self._post = get_object_or_404(Post, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self._post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self._post.pk})


class UpdateComment(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args: Any, **kwargs: Any):
        post = get_object_or_404(Post, pk=kwargs.get('post_id'))
        comment = get_object_or_404(
            Comment,
            pk=kwargs.get('pk'),
            post=post
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', self.get_object().pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.id}
        )


class DeleteComment(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.id:
            post = get_object_or_404(Post, pk=kwargs.get('post_id'))
            get_object_or_404(
                Comment,
                pk=kwargs.get('pk'),
                author=request.user, post=post
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.id}
        )
