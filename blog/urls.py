# blog/urls.py (앱 레벨)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('write/', views.blog_write, name='blog_write'),
    path('detail/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('api/get-random-title-components/', views.get_random_title_components, name='get_random_title_components'),
    path('delete/<int:pk>/', views.blog_delete, name='blog_delete'), # 새로운 삭제 URL 패턴 추가
]
