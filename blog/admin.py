# blog/admin.py
from django.contrib import admin
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect

# Client 모델 관리자 등록
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_type', 'image_url']
    list_filter = ['client_type']
    search_fields = ['name']

# ContentSubhead 모델 관리자 등록
@admin.register(ContentSubhead)
class ContentSubheadAdmin(admin.ModelAdmin):
    list_display = ['name', 'client']
    list_filter = ['client']
    search_fields = ['name']
    raw_id_fields = ['client'] # 클라이언트가 많을 경우 편리하게 선택

# 제목 구성 요소 모델들 등록
@admin.register(NumberCharacter)
class NumberCharacterAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(TalkStyle)
class TalkStyleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ContentAspect)
class ContentAspectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Blog 모델 관리자 수정
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'place_name', 'written_date'] # client 필드 추가
    list_filter = ['client', 'written_date', 'place_name'] # client 필터 추가
    search_fields = ['title', 'content', 'place_name', 'client__name'] # client 이름으로 검색 가능
    readonly_fields = ['title']  # title은 자동 생성되므로 읽기 전용

    fieldsets = (
        ('기본 정보', {
            'fields': ('client', 'content', 'place_name') # client 필드 추가, image_url은 client 모델로 이동
        }),
        # 'title' 필드는 readonly이므로 별도의 입력 필드는 필요 없음
        # 'content_title', 'content_number_character', 'content_talkstyle', 'content_aspect' 필드는 이제 폼에서 제거
        ('기타', {
            'fields': ('written_date',)
        }),
    )
    raw_id_fields = ['client'] # 클라이언트가 많을 경우 편리하게 선택
