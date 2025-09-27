from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse


class AuthorTestMixin(UserPassesTestMixin):
    """Добавляет test_func - является ли пользователь автором поста."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ReverseMixin:
    """Добавляет get_success_url: перенаправление на страницу поста."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )
