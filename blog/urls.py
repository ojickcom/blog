# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('write/', views.blog_write, name='blog_write'),
    path('<int:pk>/', views.blog_detail, name='blog_detail'),
    path('<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('<int:pk>/complete/', views.blog_complete, name='blog_complete'),  # 추가
    path('get-random-title-components/', views.get_random_title_components, name='get_random_title_components'),
]