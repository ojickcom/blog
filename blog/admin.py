# blog/admin.py
from django.contrib import admin
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect

# Client 모델 관리자 등록 (이전과 동일)
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_type', 'image_url']
    list_filter = ['client_type']
    search_fields = ['name']

# ContentSubhead 모델 관리자 등록 (이전과 동일)
@admin.register(ContentSubhead)
class ContentSubheadAdmin(admin.ModelAdmin):
    list_display = ['name', 'client']
    list_filter = ['client']
    search_fields = ['name']
    raw_id_fields = ['client']

# 제목 구성 요소 모델들 등록 (이전과 동일)
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

# Blog 모델 관리자 수정: fieldsets에서 place_name 위치 변경
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'place_name', 'written_date']
    list_filter = ['client', 'written_date', 'place_name']
    search_fields = ['title', 'content', 'place_name', 'client__name']
    readonly_fields = ['title']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('client', 'content', 'place_name') # place_name을 기본 정보에 포함
        }),
        ('기타', {
            'fields': ('written_date',)
        }),
    )
    raw_id_fields = ['client']
