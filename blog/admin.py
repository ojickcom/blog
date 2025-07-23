# blog/admin.py
from django.contrib import admin
from .models import Blog, Client, ContentSubhead, NumberCharacter, TalkStyle, ContentAspect,  ShoppingKeyword, KeywordClick, Client, Expense, KeywordGroup

# Client 모델 관리자 등록 (이전과 동일)
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_type', 'image_url','is_completed', 'payment_amount']
    list_filter = ['client_type']
    list_editable = ('is_completed', 'payment_amount')
    fields = ('name', 'client_type', 'image_url', 'payment_amount', 'is_completed') # 편집 페이지에 표시할 필드 순서
    search_fields = ['name']

# ContentSubhead 모델 관리자 등록 (이전과 동일)
@admin.register(ContentSubhead)
class ContentSubheadAdmin(admin.ModelAdmin):
    list_display = ['name', 'client']
    list_filter = ['client']
    search_fields = ['name']
    raw_id_fields = ['client']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_recurring', 'date')
    list_filter = ('is_recurring',)
    search_fields = ('name',)
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
@admin.register(ShoppingKeyword)
class ShoppingKeywordAdmin(admin.ModelAdmin):
    list_display = ('client', 'keyword', 'KeywordGroup')
    list_filter = ('client',)
    search_fields = ('keyword', 'client__name')
    raw_id_fields = ('client', 'main_keyword')  # 클라이언트가 많을 때 유용
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "main_keyword":
            # 수정 중인 객체의 client 기준으로 필터링
            object_id = request.resolver_match.kwargs.get("object_id")
            if object_id:
                try:
                    current_obj = ShoppingKeyword.objects.get(pk=object_id)
                    # 같은 클라이언트의 키워드만 보여주고, 자기 자신은 제외
                    kwargs["queryset"] = ShoppingKeyword.objects.filter(client=current_obj.client).exclude(pk=current_obj.pk)
                except ShoppingKeyword.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(KeywordClick)
class KeywordClickAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'click_date', 'click_count')
    list_filter = ('click_date', 'keyword__client')
    search_fields = ('keyword__keyword',)
    date_hierarchy = 'click_date' # 날짜별 계층 구조 보기

    admin.site.register(Expense, ExpenseAdmin)
admin.site.register(KeywordGroup)