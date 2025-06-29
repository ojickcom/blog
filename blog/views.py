# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect
from .forms import BlogForm
import random # random 모듈 임포트

def blog_list(request):
    """블로그 목록 페이지"""
    blogs = Blog.objects.all().select_related('client')
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
        
        # GET 요청 시, 블로그 제목 구성 요소를 랜덤으로 가져와 조합
        # NOTE: 이 부분은 폼이 초기화될 때만 실행되어야 하므로 POST 블록 밖에 둡니다.
        
        # Client를 선택하지 않을 수 있으므로, 모든 ContentSubhead에서 랜덤 선택
        # 만약 특정 Client를 선택한 후에만 해당 Client의 subhead를 사용하고 싶다면,
        # 이 로직을 프론트엔드 JavaScript (AJAX)로 구현해야 더 유연합니다.
        # 현재는 모든 ContentSubhead 중에서 하나를 랜덤 선택합니다.
        random_subhead = ContentSubhead.objects.order_by('?').first()
        random_character = NumberCharacter.objects.order_by('?').first()
        random_talkstyle = TalkStyle.objects.order_by('?').first()
        random_aspect = ContentAspect.objects.order_by('?').first()

        subhead_part = random_subhead.name if random_subhead else ""
        char_part = random_character.name if random_character else ""
        talk_part = random_talkstyle.name if random_talkstyle else ""
        aspect_part = random_aspect.name if random_aspect else ""

        # 제목 조합 (content_title 대신 subhead_part 사용)
        generated_title = f"{subhead_part} {char_part} {talk_part} {aspect_part}".strip()
        
        # 템플릿으로 전달
        return render(request, 'blog/write.html', {
            'form': form,
            'generated_title': generated_title # 조합된 제목을 템플릿으로 전달
        })
    
    return render(request, 'blog/write.html', {'form': form}) # POST 실패시 폼 다시 보여줌

def blog_detail(request, pk):
    """블로그 상세 페이지"""
    blog = get_object_or_404(Blog.objects.select_related('client'), pk=pk)
    return render(request, 'blog/detail.html', {'blog': blog})

