from django.db.models import Count
from django.utils import timezone

from .models import Post


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
