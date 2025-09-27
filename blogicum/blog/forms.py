from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post


class PostCreateForm(forms.ModelForm):
    """Создание публикаций."""

    class Meta:
        model = Post
        exclude = ['is_published', 'created_at', 'author', 'is_scheduled']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'image': forms.ClearableFileInput(
                attrs={'multiple': False}
            ),
        }


class UserEditForm(forms.ModelForm):
    """Редактирование информации о пользователе."""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs[
                'placeholder'
            ] = self.fields[field].label


class CommentForm(forms.ModelForm):
    """Комментарии."""

    class Meta:
        model = Comment
        fields = ('text',)


class CustomUserCreationForm(UserCreationForm):
    """Создание пользователя."""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Не обязательно.',
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Не обязательно.',
        label='Фамилия'
    )
    email = forms.EmailField(
        required=True,
        help_text='Введите ваш адрес электронной почты.',
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )
