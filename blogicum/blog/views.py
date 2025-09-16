from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category
from django.utils import timezone
from .const import POSTS_RELEASE_LIMIT

# Create your views here.


def get_published_posts():
    posts_query = Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )
    return posts_query


def index(request):
    context = {'posts': get_published_posts()[:POSTS_RELEASE_LIMIT]}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    published_posts = get_published_posts()
    post = get_object_or_404(published_posts, id=post_id)
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_published_posts().filter(category=category)
    selected_context = {
        'category': category,
        'posts': posts
    }
    return render(request, 'blog/category.html', selected_context)
