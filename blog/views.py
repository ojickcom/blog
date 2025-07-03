# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 허용하도록 데코레이터 임포트
from django.views.decorators.csrf import csrf_exempt # CSRF 보호를 임시로 비활성화 (개발용, 실제 배포 시에는 CSRF 토큰 사용 권장)
from django.contrib.auth.decorators import login_required # 로그인 인증 데코레이터 임포트
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect
from .forms import BlogForm
import random
from datetime import datetime    # 날짜 처리를 위해 추가

# blog_list를 completed와 pending을 함께 보여주는 대시보드 형태로 변경하거나,
# 두 개의 개별 뷰로 분리할 수 있습니다. 여기서는 두 개의 개별 뷰를 제공합니다.

@login_required
def blog_list_completed(request):
    """블로그 목록 페이지 - blog_write가 True인 작성 완료된 글만 표시"""
    blogs_completed = Blog.objects.filter(blog_write=True).select_related('client').order_by('-written_date')
    return render(request, 'blog/list_completed.html', {'blogs': blogs_completed, 'list_title': '트래픽 용도 글'})

@login_required
def blog_list_pending(request):
    """블로그 목록 페이지 - blog_write가 False인 작성 대기 중인 글만 표시"""
    blogs_pending = Blog.objects.filter(blog_write=False).select_related('client').order_by('-written_date')
    return render(request, 'blog/list_pending.html', {'blogs': blogs_pending, 'list_title': '포스팅용도 글 '})

@login_required
def blog_write(request):
    """블로그 작성 페이지"""
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)    # 아직 DB에 저장하지 않음
            
            # 현재 날짜에서 월과 날 추출
            now = datetime.now()
            month = now.month    # 월 (숫자)
            day = now.day        # 일 (숫자)
            month_day = f"{month}월 {day}일"    # "6월 30일" 형식
            
            # b_title 필드값에 월/날 정보 덧붙이기
            if blog.b_title:
                blog.b_title = f"{blog.b_title} {month_day}"
            
            blog.save()    # 수정된 제목으로 저장
            # blog_write는 기본값이 False이므로, 새로 생성된 글은 대기 목록으로 리다이렉트
            return redirect('blog_list_pending') 
        else:
            # POST 요청이 유효하지 않을 경우, 폼과 함께 에러 메시지를 다시 렌더링
            # 이때도 generated_title을 다시 계산하여 보여줄 수 있습니다.
            return render(request, 'blog/write.html', {
                'form': form,
                # client_id 없이 호출하여 초기값 제공 (Client가 필수 필드가 아닐 경우 대비)
                **_get_random_title_components_data(request.POST.get('client')) 
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

@login_required
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
@login_required
def get_random_title_components(request):
    if request.method == 'GET':
        client_id = request.GET.get('client_id')
        data = _get_random_title_components_data(client_id)
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@require_POST # 이 뷰는 POST 요청만 받도록 설정
def blog_delete(request, pk):
    """블로그 게시물 삭제 뷰"""
    blog = get_object_or_404(Blog, pk=pk) # 해당 PK의 블로그 게시물을 가져오거나 404 에러 발생
    blog.delete() # 게시물 삭제
    return redirect('blog_complete') # 삭제 후 대기 중인 블로그 목록 페이지로 리다이렉트

@login_required
@csrf_exempt # 개발 단계에서만 사용, 실제 배포 시에는 CSRF 토큰을 포함해야 합니다.
@require_POST
def blog_complete(request, pk):
    """블로그 글작성 완료 처리 뷰"""
    try:
        blog = get_object_or_404(Blog, pk=pk)
        blog.blog_write = True
        blog.save()
        return JsonResponse({'status': 'success', 'message': '글작성이 완료되었습니다.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)