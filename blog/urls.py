# blog/urls.py (or your project's main urls.py)
from django.urls import path
from . import views

urlpatterns = [
    # 기존 blog_list는 삭제하거나 이름을 변경해야 합니다.
    #path('', views.blog_list, name='blog_list'), # 이 줄은 이제 사용하지 않거나, 다른 이름으로 변경

    path('', views.blog_list_pending, name='blog_list_pending'), # 기본 페이지를 작성 대기 중인 글로 설정
    path('completed/', views.blog_list_completed, name='blog_list_completed'), # 작성 완료된 글 목록
    
    path('write/', views.blog_write, name='blog_write'),
    path('<int:pk>/', views.blog_detail, name='blog_detail'),
    path('<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('get_random_title_components/', views.get_random_title_components, name='get_random_title_components'),
    path('<int:pk>/complete/', views.blog_complete, name='blog_complete'), # 'mark_blog_as_written'에서 'blog_complete'로 이름 변경
]