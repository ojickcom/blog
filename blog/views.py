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
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save() # title은 Blog 모델의 save() 메서드에서 자동 생성됨
            return redirect('blog_list')
    else:
        form = BlogForm()
    
    return render(request, 'blog/write.html', {'form': form})

def blog_detail(request, pk):
    """블로그 상세 페이지"""
    blog = get_object_or_404(Blog.objects.select_related('client'), pk=pk) # Client 정보도 함께 가져옴
    return render(request, 'blog/detail.html', {'blog': blog})

# generate_title_preview 뷰는 더 이상 필요 없으므로 제거합니다.
