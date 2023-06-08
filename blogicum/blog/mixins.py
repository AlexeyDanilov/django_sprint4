from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Post, Comment


class PostActionMixin:
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get('post_id'))
        if post.author != request.user:
            return redirect('blog:post_detail', post.id)
        return super().dispatch(request, *args, **kwargs)


class CommentActionMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs.get('post_id'))
        comment = get_object_or_404(
            Comment,
            pk=kwargs.get('comment_id'),
            post=post
        )

        if comment.author != request.user:
            return redirect('blog:post_detail', post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().post.id}
        )
