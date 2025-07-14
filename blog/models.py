# blog/models.py
from django.db import models
from django.utils import timezone
import random
from datetime import date

# 기존 Client 모델 (변경 없음)
class Client(models.Model):
    CLIENT_TYPES = [
        ('place', '플레이스'),
        ('shopping', '쇼핑'),
        ('auto_keyword', '자동완성'),
        ('web_rank', '네이버 웹문서'),
        ('google_rank', '구글 순위'),
    ]
    name = models.CharField(max_length=100, unique=True, verbose_name="클라이언트 이름")
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, default='personal', verbose_name="클라이언트 유형")
    image_url = models.CharField(max_length=500, blank=True, null=True)# 클라이언트 이미지 URL 추가
    payment_amount = models.IntegerField(default=0, verbose_name="결재금액")
    is_completed = models.BooleanField(default=False, verbose_name="완성여부")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "클라이언트"
        verbose_name_plural = "클라이언트"

# 제목 구성 요소 모델들 (변경 없음)
class ContentSubhead(models.Model):
    name = models.CharField(max_length=200, verbose_name="글 주제")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subheads', null=True, blank=True, verbose_name="관련 클라이언트")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "글 주제"
        verbose_name_plural = "글 주제"

class NumberCharacter(models.Model):
    name = models.CharField(max_length=100, verbose_name="글자수")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "글자수"
        verbose_name_plural = "글자수"

class TalkStyle(models.Model):
    name = models.CharField(max_length=100, verbose_name="글 어투")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "글 어투"
        verbose_name_plural = "글 어투"

class ContentAspect(models.Model):
    name = models.CharField(max_length=200, verbose_name="글의 대상")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "글의 대상"
        verbose_name_plural = "글의 대상"


# Blog 모델 수정: blog_write 필드 추가
class Blog(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="클라이언트")
    
    # b_title 필드 추가
    b_title = models.CharField(max_length=500, blank=True, verbose_name="B_제목") 
    
    title = models.CharField(max_length=500, blank=True, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    place_name = models.CharField(max_length=200, default='온라인', verbose_name="장소명") # 기본값 설정
    written_date = models.DateTimeField(default=timezone.now, verbose_name="작성일")
    
    # 글작성 완료 여부를 나타내는 필드 추가
    blog_write = models.BooleanField(default=False, verbose_name="글작성 완료")

    def __str__(self):
        return self.title if self.title else f"제목 없음 ({self.pk})"

    def save(self, *args, **kwargs):
        # title이 비어있으면 랜덤으로 생성
        if not self.title:
            subhead_qs = ContentSubhead.objects.all()
            char_qs = NumberCharacter.objects.all()
            talk_qs = TalkStyle.objects.all()
            aspect_qs = ContentAspect.objects.all()

            # 클라이언트가 지정된 경우 해당 클라이언트의 subhead만 사용
            if self.client:
                client_subhead_qs = ContentSubhead.objects.filter(client=self.client)
                if client_subhead_qs.exists():
                    subhead_qs = client_subhead_qs
            
            subhead = random.choice(subhead_qs).name if subhead_qs.exists() else "랜덤 주제"
            character = random.choice(char_qs).name if char_qs.exists() else "랜덤 글자수"
            talkstyle = random.choice(talk_qs).name if talk_qs.exists() else "랜덤 어투"
            aspect = random.choice(aspect_qs).name if aspect_qs.exists() else "랜덤 대상"

            self.title = f"{subhead} {character} {talkstyle} {aspect}"
              # --- 2. b_title 중복 확인 및 저장 방지 로직 (수정된 부분) ---
        if self.b_title: # b_title 값이 있을 때만 중복 검사를 수행합니다.
            # 현재 저장하려는 객체(self)를 제외하고, b_title이 같은 다른 블로그들을 찾습니다.
            existing_duplicates = Blog.objects.filter(b_title=self.b_title)
            
            # 만약 현재 객체가 이미 DB에 있는 경우 (즉, 기존 블로그를 수정하는 경우)
            # 자기 자신은 중복 검사 대상에서 제외합니다.
            if self.pk:
                existing_duplicates = existing_duplicates.exclude(pk=self.pk)

            # 중복된 블로그가 발견되면 저장하지 않고 함수를 종료합니다.
            if existing_duplicates.exists():
                print(f"[{timezone.now()}] B_제목 '{self.b_title}'이(가) 이미 존재하여 저장을 건너뜜.")
                # 저장하지 않고 여기서 함수를 종료합니다.
                return 
        # ------------------------------------------------------------------
            
        # 3. 중복이 없거나 b_title이 비어있으면 현재 Blog 인스턴스 저장
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-written_date']
        verbose_name = "블로그 게시물"
        verbose_name_plural = "블로그 게시물"
class ShoppingKeyword(models.Model):
    # 1. client는 Client 모델을 참조하며, 'shopping' 또는 '쇼핑'과 같은 특정 값에 귀속됩니다.
    #    이는 모델 필드 자체에서 강제하기보다는, 데이터 입력 또는 폼에서 제어하는 것이 일반적입니다.
    #    여기서는 단순히 Client 모델을 ForeignKey로 참조합니다.
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='shopping_keywords',
        verbose_name="클라이언트"
    )

    # 4. keyword는 main_keyword에 귀속됩니다.
    #    이 필드는 키워드 자체의 문자열을 저장합니다.
    keyword = models.CharField(max_length=255, verbose_name="키워드")

    # 2. main_keyword: client에 귀속됩니다.
    #    'self' 참조는 이 키워드가 다른 ShoppingKeyword 객체(메인 키워드)의 서브 키워드임을 나타냅니다.
    #    main_keyword가 NULL이면 이 객체 자체가 메인 키워드입니다.
    #    on_delete=models.SET_NULL: 메인 키워드가 삭제되면 서브 키워드의 main_keyword 필드를 NULL로 설정합니다.
    #    blank=True, null=True: 이 필드는 선택 사항입니다 (메인 키워드인 경우).
    #    limit_choices_to=models.Q(): 이 부분은 admin.py에서 상세 필터링을 설정할 것임을 나타냅니다.
    main_keyword = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to=models.Q(),  # admin.py에서 필터링 설정 예정
        related_name='sub_keywords', # 메인 키워드에서 자신의 서브 키워드들을 참조할 때 사용
        verbose_name="메인 키워드"
    )

    # 3. keyword_group: 기존대로 group1~group5까지 있으며, client, main_keyword 등에 귀속되지 않습니다.
    #    default='기본'을 설정하여 값이 주어지지 않을 경우 '기본'으로 저장됩니다.
    keyword_group = models.CharField(
        max_length=50,
        default='기본', # 기본 그룹명 설정
        verbose_name="키워드 그룹"
    )

    class Meta:
        # client와 keyword 조합은 유일해야 합니다.
        # (예: 한 클라이언트가 동일한 이름의 키워드를 두 번 가질 수 없습니다.)
        unique_together = ('client', 'keyword')
        verbose_name = "쇼핑 키워드"
        verbose_name_plural = "쇼핑 키워드" # Fix: verbose_name_plural로 수정

    def __str__(self):
        # 이 키워드가 서브 키워드인 경우 (main_keyword가 존재하는 경우)
        if self.main_keyword:
            return f"[{self.client.name}] {self.main_keyword.keyword} > {self.keyword} ({self.keyword_group})"
        # 이 키워드가 메인 키워드인 경우 (main_keyword가 None인 경우)
        return f"[{self.client.name}] {self.keyword} ({self.keyword_group})"

    # 편의를 위한 속성: 이 키워드가 메인 키워드인지 확인
    @property
    def is_main_keyword(self):
        return self.main_keyword is None

class KeywordClick(models.Model):
    keyword = models.ForeignKey(
        ShoppingKeyword,
        on_delete=models.CASCADE,
        related_name='clicks',
        verbose_name="쇼핑 키워드"
    )
    click_date = models.DateField(default=timezone.now, verbose_name="클릭 날짜")
    click_count = models.PositiveIntegerField(default=0, verbose_name="클릭 횟수")

    class Meta:
        unique_together = ('keyword', 'click_date')
        verbose_name = "키워드 클릭 기록"
        # Fix: Change verbose_plural to verbose_name_plural
        verbose_name_plural = "키워드 클릭 기록" 
        ordering = ['-click_date']

    def __str__(self):
        return f"{self.keyword.keyword} - {self.click_date}: {self.click_count}회"
    
class Expense(models.Model):
    name = models.CharField(max_length=200, verbose_name="비용 이름")
    price = models.IntegerField(verbose_name="가격")
    is_recurring = models.BooleanField(default=False, verbose_name="항시(자동 반복)")
    date = models.DateField(default=timezone.now, verbose_name="지출일") # 비용이 발생한 날짜

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "비용"
        verbose_name_plural = "비용"