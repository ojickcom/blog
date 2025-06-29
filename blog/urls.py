# blog/urls.py (앱 레벨)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('write/', views.blog_write, name='blog_write'),
    path('detail/<int:pk>/', views.blog_detail, name='blog_detail'),
    # 'api/generate-title/' URL 패턴은 더 이상 필요 없으므로 제거
]
