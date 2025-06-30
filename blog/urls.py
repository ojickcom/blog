# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 작성 대기 중인 블로그 목록
    path('pending/', views.blog_list_pending, name='blog_list_pending'),
    path('pending/client/<str:client_name>/', views.blog_list_pending, name='blog_list_pending_by_client'),

    # 작성 완료된 블로그 목록
    path('completed/', views.blog_list_completed, name='blog_list_completed'),
    path('completed/client/<str:client_name>/', views.blog_list_completed, name='blog_list_completed_by_client'),

    path('write/', views.blog_write, name='blog_write'),
    path('<int:pk>/', views.blog_detail, name='blog_detail'),
    path('<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('<int:pk>/complete/', views.blog_complete, name='blog_complete'), # blog_complete URL 추가
    
    # 메인 페이지를 'pending' 목록으로 설정 (선택 사항)
    # path('', views.blog_list_pending, name='home'),
]