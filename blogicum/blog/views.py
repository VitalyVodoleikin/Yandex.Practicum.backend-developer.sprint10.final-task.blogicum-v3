from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from django.conf import settings

from .const import POSTS_RELEASE_LIMIT
from .forms import CommentForm, PostCreateForm, UserEditForm
from .mixins import AuthorTestMixin, BaseUserMixin, ReverseMixin
from .models import Category, Comment, Post
from .utils import (add_default_filters, get_posts_queryset,
                    get_selection_of_posts)

User = get_user_model()


class IndexListView(ListView):
    """Главная страница сайта."""

    model = Post
    paginate_by = POSTS_RELEASE_LIMIT
    template_name = 'blog/index.html'

    def get_queryset(self):
        return get_posts_queryset()


class PostDetailView(DetailView):
    """Отдельный пост."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        obj = super().get_object()
        post_id = self.kwargs.get(self.pk_url_kwarg)

        if obj.author == self.request.user:
            return obj
        return get_object_or_404(get_posts_queryset(), id=post_id)

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
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return get_posts_queryset(
            base_queryset=category.posts.all(),
            apply_filters=True,
            count_comments=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(
    LoginRequiredMixin,
    AuthorTestMixin,
    ReverseMixin,
    UpdateView
):
    """Редактирование существующего поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(self.get_success_url())


class PostDeleteView(
    LoginRequiredMixin,
    AuthorTestMixin,
    DeleteView
):
    """Удаление текущего поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])  # Лишний ручной запрос. Есть метод get_object() родителя с этой логикой, достаточно вызвать его вместо своего запроса. 
        form = PostCreateForm(self.request.POST, instance=instance)
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
        # dispatch для других целей. Ссылка на обсуждение. Точно не для создания атрибутов. Найти пост и передать в форму можно в form_valid в строке с form.instance.post.
        self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin,
    AuthorTestMixin,
    ReverseMixin,
    UpdateView
):
    """Редактирование комментария к посту."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(
    LoginRequiredMixin,
    AuthorTestMixin,
    ReverseMixin,
    DeleteView
):
    """Удаление комментария к посту."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class UserCreateView(CreateView):
    """Создание нового пользователя."""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class UserListView(BaseUserMixin, ListView):
    """Профиль пользователя."""

    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_RELEASE_LIMIT

    def get_queryset(self):
        author = self.get_user_object()
        apply_filters = not (self.request.user.is_authenticated
                             and self.request.user == author)

        return get_posts_queryset(
            base_queryset=author.posts.all(),
            apply_filters=apply_filters,
            count_comments=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_object()
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Получение текущего пользователя"""
        return self.request.user

    def get_success_url(self):
        """URL после успешного обновления"""
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
    from_email = settings.FROM_EMAIL


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
