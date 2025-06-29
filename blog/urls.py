# blog/urls.py (앱 레벨)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('write/', views.blog_write, name='blog_write'),
    path('detail/<int:pk>/', views.blog_detail, name='blog_detail'),
    # 새로운 AJAX 엔드포인트 추가
    path('api/get-random-title-components/', views.get_random_title_components, name='get_random_title_components'),
]

