from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.About.as_view(), name='about'),
    path('rules/', views.Rules.as_view(), name='rules'),
    path('contacts/', views.Contacts.as_view(), name='contacts'),
]
