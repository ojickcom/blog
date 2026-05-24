# blog/urls.py (or your project's main urls.py)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list_pending, name='blog_list_pending'),
    path('completed/', views.blog_list_completed, name='blog_list_completed'),
    path('completed/delete-old/', views.delete_old_completed_blogs, name='delete_old_completed_blogs'),
    path('write/', views.blog_write, name='blog_write'),
    path('<int:pk>/', views.blog_detail, name='blog_detail'),
    path('<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('clients/', views.client_list, name='client_list'),
    path('get_random_title_components/', views.get_random_title_components, name='get_random_title_components'),
    path('<int:pk>/complete/', views.blog_complete, name='blog_complete'),
    path('shopping_keywords/create_sub_keyword_ajax/', views.create_sub_keyword_ajax, name='create_sub_keyword_ajax'),
    path('shopping/keywords/', views.shopping_keyword_list, name='shopping_keyword_list'),
    path('shopping/keywords/input/', views.shopping_keyword_input, name='shopping_keyword_input'),
    path('shopping/keywords/edit/<int:pk>/', views.shopping_keyword_edit, name='shopping_keyword_edit'),
    path('shopping_keywords/click_list/', views.shopping_keyword_click_list, name='shopping_keyword_click_list'),
    path('shopping/keywords/<int:pk>/delete/', views.shopping_keyword_delete, name='shopping_keyword_delete'),
    path('shopping/keywords/click/', views.shopping_keyword_click_page, name='shopping_keyword_click'),
    path('shopping/keywords/increment_click/', views.increment_click_count, name='increment_click_count'),
    path('shopping/keywords/<int:pk>/detail/', views.shopping_keyword_detail, name='shopping_keyword_detail'),
]
