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
    apply_filters=True,
    count_comments=True,
    base_queryset=None
):

    queryset = base_queryset or Post.objects.all()

    if apply_filters:
        filter_dict = {
            'is_published': True,
            'pub_date__lte': timezone.now(),
            'category__is_published': True
        }
        queryset = queryset.filter(**filter_dict)

    if count_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))

    return queryset.order_by('-pub_date')
