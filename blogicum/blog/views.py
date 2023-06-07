from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from .mixins import PostActionMixin, CommentActionMixin
from .utils import get_page_objects


User = get_user_model()


def get_base_queryset():
    return Post.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    post_list = get_base_queryset().annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    page_obj = get_page_objects(post_list, request.GET.get('page'))
    return render(
        request=request,
        template_name='blog/index.html',
        context={'page_obj': page_obj}
    )


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.pub_date > timezone.now() and post.author != request.user:
        raise Http404
    return render(
        request=request,
        template_name='blog/detail.html',
        context={
            'post': post,
            'form': CommentForm(),
            'comments': post.comments.select_related('author').all()
        }
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_base_queryset().filter(category=category).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    page_obj = get_page_objects(post_list, request.GET.get('page'))
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

    if user != request.user:
        posts = posts.filter(pub_date__lte=timezone.now())

    page_obj = get_page_objects(posts, request.GET.get('page'))
    context = {
        'profile': user,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email', )

    # нашёл в интернете решение, иначе получал ошибку:
    # detail view must be called with pk or slug
    def get_object(self, queryset=None):
        return User.objects.filter(pk=self.request.user.id).first()

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


class PostUpdateView(PostActionMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.get_object().id}
        )


class PostDeleteView(PostActionMixin, LoginRequiredMixin, DeleteView):

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


class UpdateComment(CommentActionMixin, LoginRequiredMixin, UpdateView):
    form_class = CommentForm


class DeleteComment(CommentActionMixin, LoginRequiredMixin, DeleteView):
    ...
