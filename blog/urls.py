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
    path('clients/', views.client_list, name='client_list'),
    path('get_random_title_components/', views.get_random_title_components, name='get_random_title_components'),
    path('<int:pk>/complete/', views.blog_complete, name='blog_complete'), # 'mark_blog_as_written'에서 'blog_complete'로 이름 변경
    path('shopping_keywords/create_sub_keyword_ajax/', views.create_sub_keyword_ajax, name='create_sub_keyword_ajax'),
    path('shopping_keywords/input/', views.shopping_keyword_input, name='shopping_keyword_input'), 


     # --- 쇼핑 키워드 관련 URL ---
    path('shopping/keywords/', views.shopping_keyword_list, name='shopping_keyword_list'),
    path('shopping/keywords/input/', views.shopping_keyword_input, name='shopping_keyword_input'),
    path('shopping/keywords/edit/<int:pk>/', views.shopping_keyword_edit, name='shopping_keyword_edit'),
    path('shopping_keywords/click_list/', views.shopping_keyword_click_list, name='shopping_keyword_click_list'),
    path('shopping/keywords/input/', views.shopping_keyword_input, name='shopping_keyword_input'),
    path('shopping/keywords/<int:pk>/delete/', views.shopping_keyword_delete, name='shopping_keyword_delete'),
    path('shopping/keywords/click/', views.shopping_keyword_click_page, name='shopping_keyword_click'),
    path('shopping/keywords/increment_click/', views.increment_click_count, name='increment_click_count'),
    # 새로 추가된 키워드 상세 페이지 URL
    path('shopping/keywords/<int:pk>/detail/', views.shopping_keyword_detail, name='shopping_keyword_detail'),
]