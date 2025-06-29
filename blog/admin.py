from django.contrib import admin
from .models import Blog, ContentTitle, ContentNumberCharacter, ContentTalkstyle, ContentAspect

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'place_name', 'client_type', 'written_date']
    list_filter = ['client_type', 'written_date', 'place_name']
    search_fields = ['title', 'content', 'place_name']
    readonly_fields = ['title']  # title은 자동 생성되므로 읽기 전용

    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'client_type', 'image_url', 'place_name')
        }),
        # 제목 구성 요소 필드는 이제 폼에서 사라지므로 admin 필드셋에서도 제거
        # ('제목 구성 요소', {
        #     'fields': ('content_title', 'content_number_character', 'content_talkstyle', 'content_aspect')
        # }),
        ('기타', {
            'fields': ('written_date',)
        }),
    )

# --- 새로운 모델 Admin 등록 시작 ---

@admin.register(ContentTitle)
class ContentTitleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ContentNumberCharacter)
class ContentNumberCharacterAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ContentTalkstyle)
class ContentTalkstyleAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ContentAspect)
class ContentAspectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
