# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Client # Client 모델 임포트
from .forms import BlogForm
# import json # 더 이상 generate_title_preview가 필요 없으므로 제거

def blog_list(request):
    """블로그 목록 페이지"""
    blogs = Blog.objects.all().select_related('client') # Client 정보도 함께 가져옴 (성능 최적화)
    return render(request, 'blog/list.html', {'blogs': blogs})

def blog_write(request):
    """블로그 작성 페이지"""
    print("DEBUG: blog_write view called!") # 이 줄 추가
    if request.method == 'POST':
        print("DEBUG: Request method is POST.") # 이 줄 추가
        form = BlogForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid.") # 이 줄 추가
            blog = form.save()
            print(f"DEBUG: Blog saved with ID: {blog.pk}") # 이 줄 추가
            return redirect('blog_list')
        else:
            print(f"DEBUG: Form is NOT valid. Errors: {form.errors}") # 이 줄 추가
    else:
        print("DEBUG: Request method is GET. Displaying empty form.") # 이 줄 추가
        form = BlogForm()
    
    return render(request, 'blog/write.html', {'form': form})

def blog_detail(request, pk):
    """블로그 상세 페이지"""
    blog = get_object_or_404(Blog.objects.select_related('client'), pk=pk) # Client 정보도 함께 가져옴
    return render(request, 'blog/detail.html', {'blog': blog})

# generate_title_preview 뷰는 더 이상 필요 없으므로 제거합니다.
