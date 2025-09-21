from django.shortcuts import render, get_object_or_404
from blog.models import Post, Category, Comment
from django.utils import timezone
from .const import POSTS_RELEASE_LIMIT
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, PostCreateForm, UserEditForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail


# Create your views here.

def get_paginated_posts(
        request,
        filter_kwargs,
        count_posts_on_page=POSTS_RELEASE_LIMIT,
        include_draft=False
):
    # Фильтрация и пагинация постов
    time_now = timezone.now()
    if include_draft:
        posts = Post.objects.filter(
            Q(
                is_published=True,
                pub_date__lte=time_now
            ) | Q(author=request.user),
            **filter_kwargs
        )
    else:
        posts = Post.objects.filter(
            is_published=True,
            pub_date__lte=time_now,
            category__is_published=True,
            **filter_kwargs
        )
    posts = posts.order_by('-pub_date').annotate(
        comment_count=Count('comments')
    )
    paginator = Paginator(posts, count_posts_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def redirect_to_post_detail(post_id):
    # Перенаправление на страницу с деталями поста
    return redirect(reverse('blog:post_detail', args=[post_id]))


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
    context = {'page_obj': get_published_posts()[:POSTS_RELEASE_LIMIT]}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    published_posts = get_published_posts().annotate(
        comment_count=Count('comments')
    )
    post = get_object_or_404(published_posts, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
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
        'page_obj': posts
    }
    return render(request, 'blog/category.html', selected_context)


def profile(request, username):
    # Страница профиля
    user = get_object_or_404(User, username=username)
    draft = request.user == user
    page_object = get_paginated_posts(
        request,
        {'author': user},
        include_draft=draft
    )
    context = {
        'profile': user,
        'page_obj': page_object,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
    # Редактирование профиля
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect(reverse('blog:profile', args=[user.username]))

    form = UserEditForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect(reverse('blog:profile', args=[user.username]))

    return render(request, 'blog/user.html',
                  {'form': form, 'user': user})


@login_required
def create_post(request):
    # Создание поста

    if request.method == 'POST':
        form = PostCreateForm(
            request.POST or None,
            request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            time_now = timezone.now()
            post.is_scheduled = post.pub_date > time_now

            post.save()
            # return redirect(reverse('blog:post_detail', args=[post.pk]))    # Это уже можно удалить
            # Перенаправление на профиль текущего пользователя
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostCreateForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    # Удаление поста
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect(reverse('blog:create_post'))
    context = {'post': post}
    return render(request, 'posts/create.html', context)


@login_required
def edit_post(request, post_id):
    # Редактирование поста
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect_to_post_detail(post_id)
    form = PostCreateForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect_to_post_detail(post_id)
    context = {'form': form}
    return render(request, 'posts/create.html', context)


@login_required
def add_comment(request, post_id):
    # Комментирование поста
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect_to_post_detail(post_id)
    context = {'form': form}
    return render(request, 'includes/comments.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    # Редактирование комментария
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect_to_post_detail(post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect_to_post_detail(post_id)

    context = {
        'form': form,
        'comment': comment,
        'post_id': post_id,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    # Удаление комментария
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.text
        comment.delete()
        return redirect(reverse('blog:post_detail', args=[post_id]))
    return render(request, 'blog/comment.html')


@login_required
def change_password(request, username):
    # Смена пароля

    # # Настроить отправку писем
    # send_mail(
    #     subject='Изменение пароля',          
    #     message='Изменение пароля',  
    #     from_email='from@example.com',
    #     recipient_list=['to@example.com'],
    #     fail_silently=False,
    # )

    if request.user.username != username:
        return redirect("blog:profile", username=username)

    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("blog:profile", username=request.user.username)
    context = {"form": form}
    return render(request, "registration/password_change_form.html", context)
