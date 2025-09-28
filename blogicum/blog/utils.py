from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils import timezone

from .models import Post


def get_selection_of_posts(field: str) -> QuerySet:
    """Возвращает посты из связанного поля, переданого в аргумент field."""
    return Post.objects.select_related(field)


def add_default_filters() -> dict:
    """Возвращает словарь с полями для фильтрации."""
    filter_dict = dict(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )
    return filter_dict


def get_posts_queryset(
    user=None,
    author=None,
    category=None,
    apply_filters=True,
    count_comments=True,
    base_queryset=None
):

    if base_queryset is None:
        queryset = Post.objects.all()
    else:
        queryset = base_queryset

    if author:
        queryset = queryset.filter(author=author)

    if category:
        queryset = queryset.filter(category=category)

    if apply_filters:
        filter_dict = {
            'is_published': True,
            'pub_date__lte': timezone.now(),
            'category__is_published': True
        }
        if user and user.is_authenticated and user == author:
            # Если пользователь является автором, показываем все его посты
            filter_dict = {}
        queryset = queryset.filter(**filter_dict)

    if count_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset.order_by('-pub_date')
