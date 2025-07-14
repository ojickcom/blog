# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 허용하도록 데코레이터 임포트
from django.views.decorators.csrf import csrf_exempt # CSRF 보호를 임시로 비활성화 (개발용, 실제 배포 시에는 CSRF 토큰 사용 권장)
from django.contrib.auth.decorators import login_required # 로그인 인증 데코레이터 임포트
from django.db.models import F # 필드 값 업데이트를 위해 F 객체 임포트
from datetime import date, timedelta
from django.db.models import OuterRef, Subquery, Sum
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect,  ShoppingKeyword, KeywordClick 
from .forms import BlogForm, ShoppingKeywordForm
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
import random
from datetime import datetime    # 날짜 처리를 위해 추가


# blog_list를 completed와 pending을 함께 보여주는 대시보드 형태로 변경하거나,
# 두 개의 개별 뷰로 분리할 수 있습니다. 여기서는 두 개의 개별 뷰를 제공합니다.

@login_required
def blog_list_completed(request):
    """작성 완료된 글 + 날짜 필터링"""
    selected_date = request.GET.get('date')  # URL에서 날짜 파라미터 받기
    blogs_query = Blog.objects.filter(blog_write=True).select_related('client')
    
    if selected_date:
        blogs_query = blogs_query.filter(written_date__date=parse_date(selected_date))
    
    blogs_completed = blogs_query.order_by('-written_date')

    # 날짜 목록 생성
    available_dates = (
        Blog.objects.filter(blog_write=True)
        .annotate(date_only=TruncDate('written_date'))
        .values_list('date_only', flat=True)
        .distinct()
        .order_by('-date_only')
    )

    return render(request, 'blog/list_completed.html', {
        'blogs': blogs_completed,
        'list_title': '트래픽 용도 글',
        'available_dates': available_dates,
        'selected_date': selected_date,
    })

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
    return redirect('blog_list_completed') # 삭제 후 대기 중인 블로그 목록 페이지로 리다이렉트

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
    
@login_required
def shopping_keyword_list(request):
    """
    쇼핑 키워드 목록을 보여주는 페이지.
    지난 10일간의 클릭 횟수도 함께 표시.
    모든 키워드 (그룹 관계없이) 보여준다.
    """
    today = date.today()
    ten_days_ago = today - timedelta(days=9) # 오늘 포함 10일 전

    # 모든 쇼핑 키워드를 가져옵니다.
    all_keywords = ShoppingKeyword.objects.select_related('client').order_by('client__name', 'keyword')

    recent_clicks_data = {}
    date_range = [ten_days_ago + timedelta(days=i) for i in range(10)]

    all_recent_clicks = KeywordClick.objects.filter(
        click_date__gte=ten_days_ago,
        click_date__lte=today,
        keyword__in=all_keywords # 현재 화면에 표시될 키워드들만 대상으로
    ).values('keyword_id', 'click_date', 'click_count')

    for click_item in all_recent_clicks:
        keyword_id = click_item['keyword_id']
        click_date = click_item['click_date']
        click_count = click_item['click_count']

        if keyword_id not in recent_clicks_data:
            recent_clicks_data[keyword_id] = {}
        recent_clicks_data[keyword_id][click_date] = click_count
    
    for keyword in all_keywords:
        keyword.recent_clicks = recent_clicks_data.get(keyword.pk, {})
        keyword.daily_clicks_display = [
            keyword.recent_clicks.get(d, 0) for d in date_range
        ]
    
    # colspan_count 계산은 뷰에서 처리하여 템플릿으로 전달
    colspan_count = 4 + len(date_range) + 1 # 클라이언트, 메인, 키워드, 관리, 클릭 대상 + 날짜 수 + (새로운 '키워드 그룹' 컬럼 추가)
                                          # 4(클라이언트, 메인, 키워드, 관리) + date_range 길이 + 1(클릭 대상 컬럼) + 1(새로 추가될 그룹 컬럼)
                                          # 정확히는 컬럼이 (클라이언트, 메인 키워드, 키워드, 날짜들, 키워드 그룹, 관리) 이므로
                                          # 3 (client, main_keyword, keyword) + len(date_range) + 1 (keyword_group) + 1 (관리)
                                          # 총 5 + len(date_range)
    colspan_count = 5 + len(date_range) # 클라이언트, 메인 키워드, 키워드, 키워드 그룹, 관리 + 날짜 수

    return render(request, 'blog/shopping_keyword_list.html', {
        'keywords': all_keywords,
        'date_range': date_range,
        'colspan_count': colspan_count, # 계산된 colspan_count 전달
    })

@login_required
def shopping_keyword_input(request, pk=None):
    """
    쇼핑 키워드 입력 (생성/수정) 페이지.
    pk가 있으면 수정, 없으면 생성.
    main_keyword와 keyword_group을 입력/수정 가능.
    """
    keyword_instance = None
    if pk: # 수정 모드
        keyword_instance = get_object_or_404(ShoppingKeyword, pk=pk)

    if request.method == 'POST':
        form = ShoppingKeywordForm(request.POST, instance=keyword_instance)
        if form.is_valid():
            form.save()
            return redirect('shopping_keyword_list')
    else: # GET 요청
        form = ShoppingKeywordForm(instance=keyword_instance)

    return render(request, 'blog/shopping_keyword_input.html', {
        'form': form,
        'is_edit': pk is not None,
    })

@login_required
@require_POST
def shopping_keyword_delete(request, pk):
    """쇼핑 키워드 삭제."""
    keyword = get_object_or_404(ShoppingKeyword, pk=pk)
    keyword.delete()
    return redirect('shopping_keyword_list')

@login_required
def shopping_keyword_click_page(request):
    """
    클릭용 키워드 목록 페이지.
    'keyword_group'이 'keyword_group1'인 키워드만 보여준다.
    """
    # 'keyword_group'이 'keyword_group1'인 키워드만 필터링
    keywords = ShoppingKeyword.objects.filter(keyword_group='keyword_group1').select_related('client').order_by('client__name', 'keyword')
    return render(request, 'blog/shopping_keyword_click.html', {
        'keywords': keywords,
    })

@login_required
@require_POST
@csrf_exempt
def increment_click_count(request):
    """
    AJAX 요청을 통해 키워드의 클릭 횟수를 1 증가시키는 뷰.
    매일 0시에 초기화되는 로직을 포함.
    """
    keyword_id = request.POST.get('keyword_id')
    today = date.today()

    if not keyword_id:
        return JsonResponse({'status': 'error', 'message': 'Keyword ID is required.'}, status=400)

    try:
        click_record, created = KeywordClick.objects.get_or_create(
            keyword_id=keyword_id,
            click_date=today,
            defaults={'click_count': 0}
        )
        click_record.click_count = F('click_count') + 1
        click_record.save()
        click_record.refresh_from_db()
        return JsonResponse({'status': 'success', 'new_count': click_record.click_count})
    except ShoppingKeyword.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Keyword not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def shopping_keyword_detail(request, pk):
    """
    특정 키워드의 상세 페이지.
    모든 날짜별 클릭 횟수를 보여주고, keyword_group 정보도 포함.
    """
    keyword = get_object_or_404(ShoppingKeyword.objects.select_related('client'), pk=pk)
    all_clicks = keyword.clicks.all()

    return render(request, 'blog/shopping_keyword_detail.html', {
        'keyword': keyword,
        'all_clicks': all_clicks,
    })

@login_required
def client_list(request):
    # 데이터베이스에서 모든 Client 객체를 가져옵니다.
    clients = Client.objects.all()
    expenses = Expense.objects.all()
    completed_sum = clients.filter(is_completed=True).aggregate(total=Sum('payment_amount'))['total'] or 0
    pending_sum = clients.filter(is_completed=False).aggregate(total=Sum('payment_amount'))['total'] or 0
    # 템플릿에 전달할 컨텍스트를 정의합니다.
    context = {
        'clients': clients,
                'completed_sum': completed_sum,
        'pending_sum': pending_sum,
        'expenses': expenses,
    }
    
    # 'client_list.html' 템플릿을 렌더링하며 데이터를 전달합니다.
    return render(request, 'blog/client_list.html', context)