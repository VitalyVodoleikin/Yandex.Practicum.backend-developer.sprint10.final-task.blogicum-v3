from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/', views.CategoryListView.as_view(),
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<str:username>/', views.UserListView.as_view(),
         name='profile'),

    
	# ----------> Доделать!!!
    path('edit_profile/<str:username>/', views.UserUpdateView.as_view(),
         name='edit_profile'),
	# <----------


    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

    path('password/change/',
         views.CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('password/change/done/',
         views.CustomPasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password/reset/',
         views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password/reset/done/',
         views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password/reset/complete/',
         views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

]
