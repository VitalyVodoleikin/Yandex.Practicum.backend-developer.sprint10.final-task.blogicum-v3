from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Category, Comment, Location, Post

admin.site.unregister(Group)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'text',
        'pub_date',
        'is_published',
        'created_at',
        'author',
    )
    list_editable = (
        'is_published',
        'author',
    )
    search_fields = ('title', 'text')
    list_filter = ('category__title',)
    list_display_links = ('title',)

    @admin.display(description=_('Категория'))
    def category_title(self, obj):
        return obj.category.title if obj.category else None

    @admin.display(description=_('Местоположение'))
    def location_name(self, obj):
        return obj.location.name if obj.location else None


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('created_at',)
    list_display_links = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created_at")
    search_fields = ("post__title", "author__username", "text")
    list_filter = ("created_at",)
