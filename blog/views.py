# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect
from .forms import BlogForm
import random
from datetime import datetime

@login_required
def blog_list_completed(request, client_name=None): # client_name 인자 추가
    """블로그 목록 페이지 - blog_write가 True인 작성 완료된 글만 표시"""
    blogs_query = Blog.objects.filter(blog_write=True).select_related('client')
    list_title_prefix = '트래픽 용도 글'
    selected_client = None # 현재 선택된 클라이언트 이름 저장

    if client_name:
        try:
            client_obj = Client.objects.get(name=client_name)
            blogs_query = blogs_query.filter(client=client_obj)
            list_title = f"{client_name}님의 {list_title_prefix}"
            selected_client = client_name
        except Client.DoesNotExist:
            # 클라이언트가 존재하지 않으면 전체 목록을 보여주거나 에러 처리
            list_title = f"'{client_name}'에 대한 {list_title_prefix} (클라이언트 없음)"
    else:
        list_title = list_title_prefix

    blogs_completed = blogs_query.order_by('-written_date')
    clients = Client.objects.all().order_by('name') # 모든 클라이언트 목록

    return render(request, 'blog/list_completed.html', {
        'blogs': blogs_completed,
        'list_title': list_title,
        'clients': clients, # 클라이언트 목록 전달
        'selected_client': selected_client # 선택된 클라이언트 이름 전달
    })

@login_required
def blog_list_pending(request, client_name=None): # client_name 인자 추가
    """블로그 목록 페이지 - blog_write가 False인 작성 대기 중인 글만 표시"""
    blogs_query = Blog.objects.filter(blog_write=False).select_related('client')
    list_title_prefix = '포스팅용도 글'
    selected_client = None # 현재 선택된 클라이언트 이름 저장

    if client_name:
        try:
            client_obj = Client.objects.get(name=client_name)
            blogs_query = blogs_query.filter(client=client_obj)
            list_title = f"{client_name}님의 {list_title_prefix}"
            selected_client = client_name
        except Client.DoesNotExist:
            # 클라이언트가 존재하지 않으면 전체 목록을 보여주거나 에러 처리
            list_title = f"'{client_name}'에 대한 {list_title_prefix} (클라이언트 없음)"
    else:
        list_title = list_title_prefix

    blogs_pending = blogs_query.order_by('-written_date')
    clients = Client.objects.all().order_by('name') # 모든 클라이언트 목록

    return render(request, 'blog/list_pending.html', {
        'blogs': blogs_pending,
        'list_title': list_title,
        'clients': clients, # 클라이언트 목록 전달
        'selected_client': selected_client # 선택된 클라이언트 이름 전달
    })

@login_required
def blog_write(request):
    """블로그 작성 페이지"""
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            
            now = datetime.now()
            month = now.month
            day = now.day
            month_day = f"{month}월 {day}일"
            
            if blog.b_title:
                blog.b_title = f"{blog.b_title} {month_day}"
            
            blog.save()
            return redirect('blog_list_pending') 
        else:
            return render(request, 'blog/write.html', {
                'form': form,
                **_get_random_title_components_data(request.POST.get('client')) 
            })
    else: # GET 요청
        form = BlogForm()
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
            pass

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
@require_POST
def blog_delete(request, pk):
    """블로그 게시물 삭제 뷰"""
    blog = get_object_or_404(Blog, pk=pk)
    blog.delete()
    # 삭제 후 현재 보고 있던 목록 (pending 또는 completed)으로 리다이렉트
    # 이 부분은 현재 뷰가 어떤 목록이었는지 알 수 없으므로,
    # 삭제 버튼이 있는 템플릿의 URL을 기반으로 리다이렉트 URL을 동적으로 생성하거나,
    # 기본값으로 'blog_list_pending'으로 리다이렉트합니다.
    # 여기서는 'blog_list_pending'으로 기본 리다이렉트합니다.
    return redirect('blog_list_pending')

@login_required
@csrf_exempt
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