from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import F, Case, When, Value, BooleanField # Case, When, Value, BooleanField 임포트
from datetime import date, timedelta
from django.db.models import OuterRef, Subquery, Sum
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect, ShoppingKeyword, KeywordClick, Expense, KeywordGroup
from .forms import BlogForm, SubKeywordAddForm, MainKeywordNameUpdateForm,MainKeywordInitialAddForm
import random
from datetime import datetime
from django.contrib import messages
from django.db import models

# blog_list를 completed와 pending을 함께 보여주는 대시보드 형태로 변경하거나,
# 두 개의 개별 뷰로 분리할 수 있습니다. 여기서는 두 개의 개별 뷰를 제공합니다.

@login_required
def blog_list_completed(request):
    """작성 완료된 글 + 클라이언트 필터링"""
    # URL에서 클라이언트 이름 파라미터 받기
    selected_client_name = request.GET.get('client')

    blogs_query = Blog.objects.filter(blog_write=True).select_related('client')
    
    # 선택된 클라이언트가 있다면 해당 클라이언트의 블로그 글만 필터링
    if selected_client_name:
        blogs_query = blogs_query.filter(client__name=selected_client_name)
    
    blogs_completed = blogs_query.order_by('-written_date')

    # 모든 클라이언트 이름 목록을 가져오기
    # `Client` 모델에서 `name` 필드의 고유한 값들을 가져옵니다.
    available_clients = Client.objects.values_list('name', flat=True).distinct().order_by('name')

    return render(request, 'blog/list_completed.html', {
        'blogs': blogs_completed,
        'list_title': '트래픽 용도 글',
        'available_clients': available_clients, # 추가: 모든 클라이언트 이름 전달
        'selected_client_name': selected_client_name, # 추가: 현재 선택된 클라이언트 이름 전달
    })

@login_required
def blog_list_pending(request):
    """블로그 목록 페이지 - blog_write가 False인 작성 대기 중인 글만 표시 + 클라이언트 필터링"""
    # URL 쿼리 파라미터에서 선택된 클라이언트 이름 가져오기
    selected_client_name = request.GET.get('client')

    # 기본 쿼리: 작성 대기 중인 모든 블로그 글
    blogs_query = Blog.objects.filter(blog_write=False).select_related('client')
    
    # 만약 특정 클라이언트가 선택되었다면, 해당 클라이언트의 글만 필터링
    if selected_client_name:
        blogs_query = blogs_query.filter(client__name=selected_client_name)
    
    # 최종적으로 날짜순으로 정렬
    blogs_pending = blogs_query.order_by('-written_date')

    # 필터링 드롭다운을 위해 모든 클라이언트의 이름 목록 가져오기
    available_clients = Client.objects.values_list('name', flat=True).distinct().order_by('name')

    # 템플릿에 전달할 데이터
    context = {
        'blogs': blogs_pending, 
        'list_title': '포스팅용도 글',
        'available_clients': available_clients,       # 클라이언트 목록 추가
        'selected_client_name': selected_client_name, # 현재 선택된 클라이언트 이름 추가
    }
    
    return render(request, 'blog/list_pending.html', context)

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
    return redirect('blog_list_pending') # 삭제 후 대기 중인 블로그 목록 페이지로 리다이렉트

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
    selected_group_name = request.GET.get('group')
    selected_client_name = request.GET.get('client') # 클라이언트 이름 가져오기

    available_groups = KeywordGroup.objects.all().order_by('name')
    available_clients = Client.objects.all().order_by('name') # 모든 클라이언트 목록 가져오기

    keywords_query = ShoppingKeyword.objects.select_related('client', 'main_keyword').prefetch_related('sub_keywords', 'clicks', 'groups')

    # 그룹 필터링
    if selected_group_name:
        keywords_query = keywords_query.filter(groups__name=selected_group_name)

    # 클라이언트 필터링 추가
    if selected_client_name:
        keywords_query = keywords_query.filter(client__name=selected_client_name)

    keywords = keywords_query.order_by(
        'client__name',
        Case(
            When(main_keyword__isnull=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        ),
        'keyword'
    )

    today = date.today()
    date_range = [today - timedelta(days=i) for i in range(7)]
    
    all_clicks = KeywordClick.objects.filter(click_date__in=date_range).values('keyword_id', 'click_date', 'click_count')
    click_data_map = {}
    for click in all_clicks:
        click_data_map[(click['keyword_id'], click['click_date'])] = click['click_count']

    for keyword_obj in keywords:
        keyword_obj.daily_clicks_display = [
            click_data_map.get((keyword_obj.id, d), 0) for d in date_range
        ]
        keyword_obj.is_click_target = True 

    sub_keyword_add_form = SubKeywordAddForm()
    sub_keyword_add_form.fields['main_keyword'].queryset = ShoppingKeyword.objects.filter(main_keyword__isnull=True).exclude(keyword='').order_by('keyword')

    context = {
        'keywords': keywords,
        'date_range': date_range,
        'colspan_count': 6 + len(date_range),
        'sub_keyword_add_form': sub_keyword_add_form,
        'available_groups': available_groups,
        'selected_group_name': selected_group_name,
        'available_clients': available_clients, # 추가: 클라이언트 목록 전달
        'selected_client_name': selected_client_name, # 추가: 선택된 클라이언트명 전달
    }
    return render(request, 'blog/shopping_keyword_list.html', context)
@login_required
def shopping_keyword_edit(request, pk):
    keyword = get_object_or_404(ShoppingKeyword, pk=pk)

    if request.method == 'POST':
        # MainKeywordNameUpdateForm은 keyword와 groups만 수정합니다.
        form = MainKeywordNameUpdateForm(request.POST, instance=keyword)
        if form.is_valid():
            form.save() # 폼의 save() 메서드 내부에서 save_m2m()이 호출됩니다.
            messages.success(request, '키워드 이름과 그룹이 성공적으로 업데이트되었습니다.')
            return redirect('shopping_keyword_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = MainKeywordNameUpdateForm(instance=keyword)

    context = {
        'form': form,
        'keyword': keyword,
    }
    return render(request, 'blog/shopping_keyword_edit.html', context)


# --- AJAX를 통한 서브 키워드 생성 뷰 ---
@login_required
def create_sub_keyword_ajax(request):
    if request.method == 'POST':
        form = SubKeywordAddForm(request.POST)
        if form.is_valid():
            try:
                new_sub_keyword = form.save() 
                new_sub_keyword = form.save(commit=False) # 인스턴스만 생성
                new_sub_keyword.created_by = request.user # 유저 할당 (모델 필드에 맞게 조정)
                new_sub_keyword.updated_by = request.user # 유저 할당
                new_sub_keyword.save() # 인스턴스 저장
                form.save_m2m() # M2M 필드 저장

                return JsonResponse({'status': 'success', 'message': '하위 키워드가 성공적으로 추가되었습니다.'})
            except Exception as e:
                # 트랜잭션 사용은 ModelForm.save()가 내부적으로 처리하므로, 여기서는 별도로 명시할 필요는 없습니다.
                # 하지만 데이터베이스 관련 예외를 처리하는 것은 좋은 습관입니다.
                return JsonResponse({'status': 'error', 'message': f'데이터 저장 중 오류가 발생했습니다: {e}'}, status=500)
        else:
            # 폼 유효성 검사 실패 시
            return JsonResponse({
                'status': 'error',
                'message': '유효성 검사 실패',
                'errors': form.errors.as_json()
            }, status=400)
    return JsonResponse({'status': 'error', 'message': '잘못된 요청 방식'}, status=405)

@login_required
def shopping_keyword_input(request):
    if request.method == 'POST':
        form = MainKeywordInitialAddForm(request.POST)
        if form.is_valid():
            try:
                new_keyword = form.save()
                messages.success(request, '새 메인 키워드(클라이언트만 설정)가 성공적으로 생성되었습니다. 이제 키워드 이름과 그룹을 추가할 수 있습니다.')
                return redirect('shopping_keyword_edit', pk=new_keyword.pk)
            except Exception as e:
                messages.error(request, f'메인 키워드 생성 중 오류가 발생했습니다: {e}')
        else:
            # --- 이 부분을 수정합니다 ---
            # 폼 전체 오류 메시지 처리
            if '__all__' in form.errors:
                for error in form.errors['__all__']:
                    messages.error(request, f"폼 오류: {error}") # 필드 레이블 없이 "폼 오류"로 표시
            
            # 각 필드별 오류 메시지 처리
            for field, errors in form.errors.items():
                if field != '__all__': # '__all__'은 위에서 이미 처리했으므로 건너_ㅂ니다.
                    field_label = form.fields[field].label if field in form.fields else field # 필드가 없는 경우 필드 이름 자체를 사용
                    for error in errors:
                        messages.error(request, f"{field_label}: {error}")
            # --- 수정 끝 ---
    else:
        form = MainKeywordInitialAddForm()

    context = {
        'form': form,
    }
    return render(request, 'blog/shopping_keyword_input.html', context)

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
    total_expense_sum = expenses.aggregate(total=Sum('price'))['total'] or 0
    # 템플릿에 전달할 컨텍스트를 정의합니다.
    context = {
        'clients': clients,
                'completed_sum': completed_sum,
        'pending_sum': pending_sum,
        'expenses': expenses,
        'total_expense_sum': total_expense_sum,
    }
    
    # 'client_list.html' 템플릿을 렌더링하며 데이터를 전달합니다.
    return render(request, 'blog/client_list.html', context)
@login_required
@require_POST
@csrf_exempt
def create_sub_keyword_ajax(request): # 함수명 변경 (하위 키워드 추가)
    form = SubKeywordAddForm(request.POST) # SubKeywordAddForm 사용
    if form.is_valid():
        form.save() 
        return JsonResponse({'status': 'success', 'message': f"'{form.cleaned_data['keyword']}' 하위 키워드가 '{form.cleaned_data['main_keyword'].keyword}'에 성공적으로 추가되었습니다."})
    else:
        # 폼 유효성 검사 실패 시 에러 메시지 반환 (디버깅 용이하게 errors를 그대로 반환)
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
@login_required
def shopping_keyword_click_list(request):
    """
    클릭용 키워드 리스트를 표시하는 뷰.
    키워드 그룹별로 필터링 가능.
    """
    selected_group_name = request.GET.get('group') # URL 쿼리 파라미터 'group' 가져오기
    available_groups_queryset = KeywordGroup.objects.all().order_by('name')
    available_groups = [group.name for group in available_groups_queryset]
    keywords_queryset = ShoppingKeyword.objects.select_related('main_keyword').prefetch_related('groups')

    if selected_group_name:
        # 특정 그룹에 속한 키워드만 필터링
        keywords_queryset = keywords_queryset.filter(groups__name=selected_group_name)

    # 필요에 따라 정렬 순서 조정 (예: 클라이언트명, 메인 키워드명, 키워드명 순)
    keywords_queryset = keywords_queryset.order_by('client__name', 'main_keyword__keyword', 'keyword')

    context = {
        'list_title': '클릭용 키워드 리스트',
        'keywords': keywords_queryset, # 템플릿에서 'keywords'로 사용
        'available_groups': available_groups,
        'selected_group_name': selected_group_name,
    }
    return render(request, 'blog/shopping_keyword_click_list.html', context)
