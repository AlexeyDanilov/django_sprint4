from typing import Any

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Comment


class PostActionMixin:
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args: Any, **kwargs: Any):
        post = get_object_or_404(Post, pk=kwargs.get('pk'))
        if post.author != request.user:
            return redirect('blog:post_detail', self.get_object().pk)
        return super().dispatch(request, *args, **kwargs)


class CommentActionMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        pk = self.request.path.strip('/').split('/')[-1]
        return Comment.objects.filter(pk=pk).first()

    def dispatch(self, request, *args, **kwargs):
        if request.user.id:
            post = get_object_or_404(Post, pk=kwargs.get('post_id'))
            get_object_or_404(
                Comment,
                pk=kwargs.get('comment_id'),
                author=request.user, post=post
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.get_object().post.id}
        )
