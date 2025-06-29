from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse # 이제 필요 없음
from .models import Blog # Blog 모델만 필요
from .forms import BlogForm
# import json # 이제 필요 없음

def blog_list(request):
    """블로그 목록 페이지"""
    blogs = Blog.objects.all()
    return render(request, 'blog/list.html', {'blogs': blogs})

def blog_write(request):
    """블로그 작성 페이지"""
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            return redirect('blog_list')
    else:
        form = BlogForm()

    return render(request, 'blog/write.html', {'form': form})

def blog_detail(request, pk):
    """블로그 상세 페이지"""
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/detail.html', {'blog': blog})

# generate_title_preview 뷰는 이제 제거합니다.
# def generate_title_preview(request):
#     """AJAX로 title 미리보기 생성"""
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         content_title = data.get('content_title', '')
#         content_number_character = data.get('content_number_character', '')
#         content_talkstyle = data.get('content_talkstyle', '')
#         content_aspect = data.get('content_aspect', '')
#         
#         title = f"{content_title} {content_number_character} {content_talkstyle} {content_aspect}".strip()
#         return JsonResponse({'title': title})
#     
#     return JsonResponse({'error': 'Invalid request'})