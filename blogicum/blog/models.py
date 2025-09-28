from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .const import MAX_LENGTH_SELF_TITLE, MAX_LENGTH_TITLE_FIELDS

# Пользователь, эту модель описывать не нужно, она встроена в Django
User = get_user_model()


class PublishAbstractModel(models.Model):
    """Абстрактная модель с общими полями публикации."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Post(PublishAbstractModel):
    """Публикация."""

    title = models.CharField(
        max_length=MAX_LENGTH_TITLE_FIELDS,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        auto_now=False,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в '
            'будущем — можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    image = models.ImageField(
        _('Изображение'),
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

        def __str__(self):
            return f"{self.title[:MAX_LENGTH_SELF_TITLE]}"


class Category(PublishAbstractModel):
    """Тематическая категория."""

    title = models.CharField(
        max_length=MAX_LENGTH_TITLE_FIELDS,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

        def __str__(self):
            return f"{self.title[:MAX_LENGTH_SELF_TITLE]}"


class Location(PublishAbstractModel):
    """Географическая метка."""

    name = models.CharField(
        max_length=MAX_LENGTH_TITLE_FIELDS,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

        def __str__(self):
            return f"{self.name[:MAX_LENGTH_SELF_TITLE]}"


class Comment(models.Model):
    """Комментарии."""

    text = models.TextField('Ваш комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_comments',
        verbose_name='Автор комментария'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        # default_related_name = 'blogs_comment_related'

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту {self.post.pk}: {self.text[:MAX_LENGTH_SELF_TITLE]}"
