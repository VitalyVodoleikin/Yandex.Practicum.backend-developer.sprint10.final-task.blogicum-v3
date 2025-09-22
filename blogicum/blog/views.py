from .const import POSTS_RELEASE_LIMIT
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView)
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from .forms import CommentForm, PostCreateForm, UserEditForm
from .mixins import AuthorTestMixin, ReverseMixin
from .models import Category, Comment, Post
from .utils import add_default_filters, get_selection_of_posts
from django.views.generic import (
    CreateView, DeleteView,
    DetailView, ListView,
    UpdateView)


User = get_user_model()


class IndexListView(ListView):
    """Главная страница сайта."""

    model = Post
    paginate_by = POSTS_RELEASE_LIMIT
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.filter(
            **add_default_filters()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    """Отдельный пост."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        obj = get_selection_of_posts('author').filter(
            id=self.kwargs['post_id']
        )
        if obj and not obj[0].author == self.request.user:
            filters = add_default_filters()
        else:
            filters = dict()
        return get_object_or_404(obj, **filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryListView(ListView):
    """Категория постов."""

    paginate_by = POSTS_RELEASE_LIMIT
    template_name = 'blog/category.html'

    def get_queryset(self):
        queryset = get_selection_of_posts('category').filter(
            category__slug=self.kwargs['category_slug'],
        ).filter(
            **add_default_filters()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorTestMixin, ReverseMixin, UpdateView):
    """Редактирование существующего поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form = PostCreateForm(self.request.POST or None, instance=instance)
        context['form'] = form
        return context

    def handle_no_permission(self):
        return redirect(self.get_success_url())


class PostDeleteView(AuthorTestMixin, DeleteView):
    """Удаление текущего поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form = PostCreateForm(self.request.POST or None, instance=instance)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, ReverseMixin, CreateView):
    """Создание комментария к посту."""

    post_obj = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)


class CommentUpdateView(AuthorTestMixin, ReverseMixin, UpdateView):
    """Редактирование комментария к посту."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment,
            id=self.kwargs['comment_id'],
        )


class CommentDeleteView(AuthorTestMixin, ReverseMixin, DeleteView):
    """Удаление комментария к посту."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class UserCreateView(CreateView):
    """Создание нового пользователя."""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class UserListView(ListView):
    """Профиль пользователя."""

    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_RELEASE_LIMIT

    def get_queryset(self):
        return Post.objects.filter(
            author=get_object_or_404(User, username=self.kwargs['username']).id
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = profile
        return context


class UserUpdateView(UserPassesTestMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    form_class = UserEditForm
    template_name = 'blog/profile_edit.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(User, id=self.request.user.id)
        form = UserEditForm(self.request.POST or None, instance=instance)
        context['profile'] = instance
        context['form'] = form
        return context

    def test_func(self):
        object = self.get_object()
        return object == self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
        
    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        return response


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    from_email = 'no-reply@yourdomain.com'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
