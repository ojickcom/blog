from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Blog
from .forms import BlogForm

def blog_list(request):
    """블로그 목록 페이지 - title, content, image_url, place_name, written_date 표시"""
    blogs = Blog.objects.all()
    return render(request, 'blog/list.html', {'blogs': blogs})

def blog_write(request):
    """블로그 작성 페이지 - content, client_type, image_url, place_name + 제목 구성요소 입력"""
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            messages.success(request, '블로그가 성공적으로 작성되었습니다!')
            return redirect('blog_list')
        else:
            messages.error(request, '입력 내용을 확인해주세요.')
    else:
        form = BlogForm()
    
    return render(request, 'blog/write.html', {'form': form})

def blog_detail(request, pk):
    """블로그 상세 페이지"""
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/detail.html', {'blog': blog})