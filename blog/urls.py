from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('write/', views.blog_write, name='blog_write'),
    path('detail/<int:pk>/', views.blog_detail, name='blog_detail'),
    # path('api/generate-title/', views.generate_title_preview, name='generate_title_preview'), # 제거
]