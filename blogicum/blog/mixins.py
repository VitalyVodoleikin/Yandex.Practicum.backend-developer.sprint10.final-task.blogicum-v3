from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


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


class BaseMyUserMixin:
    """Миксин для работы с пользователями"""

    def get_user_object(self):
        """Получение объекта пользователя"""
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)
