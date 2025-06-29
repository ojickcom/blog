# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse # JsonResponse는 다시 필요합니다.
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect
from .forms import BlogForm
import random # random 모듈 필요

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
            # POST 요청이 유효하지 않을 경우, 폼과 함께 에러 메시지를 다시 렌더링
            # 이때도 generated_title을 다시 계산하여 보여줄 수 있습니다.
            return render(request, 'blog/write.html', {
                'form': form,
                # POST 실패 시에도 랜덤 제목 구성 요소를 다시 로드하여 템플릿에 전달
                **_get_random_title_components_data(None) # client_id 없이 호출
            })
    else: # GET 요청
        form = BlogForm()
        # GET 요청 시, 블로그 제목 구성 요소를 랜덤으로 가져와 조합하여 템플릿으로 전달
        # 초기 로드 시 클라이언트가 선택되지 않았으므로 None을 전달합니다.
        # 이 데이터는 JS가 클라이언트 변경 시 업데이트할 초기 값으로만 사용됩니다.
        return render(request, 'blog/write.html', {
            'form': form,
            **_get_random_title_components_data(None)
        })

def blog_detail(request, pk):
    """블로그 상세 페이지"""
    blog = get_object_or_404(Blog.objects.select_related('client'), pk=pk)
    return render(request, 'blog/detail.html', {'blog': blog})

# AJAX 요청을 처리하여 랜덤 제목 구성 요소를 반환하는 헬퍼 함수
def _get_random_title_components_data(client_id):
    subhead_part = ""
    if client_id:
        try:
            client_obj = Client.objects.get(pk=client_id)
            subhead_qs = ContentSubhead.objects.filter(client=client_obj)
            random_subhead = subhead_qs.order_by('?').first()
            if random_subhead:
                subhead_part = random_subhead.name
        except Client.DoesNotExist:
            pass # 클라이언트가 존재하지 않으면 subhead_part는 빈 문자열 유지

    random_character = NumberCharacter.objects.order_by('?').first()
    random_talkstyle = TalkStyle.objects.order_by('?').first()
    random_aspect = ContentAspect.objects.order_by('?').first()

    char_part = random_character.name if random_character else ""
    talk_part = random_talkstyle.name if random_talkstyle else ""
    aspect_part = random_aspect.name if random_aspect else ""

    return {
        'generated_subhead': subhead_part,
        'generated_character': char_part,
        'generated_talkstyle': talk_part,
        'generated_aspect': aspect_part,
    }

# AJAX 요청을 처리하는 뷰 함수
def get_random_title_components(request):
    if request.method == 'GET':
        client_id = request.GET.get('client_id')
        data = _get_random_title_components_data(client_id)
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

