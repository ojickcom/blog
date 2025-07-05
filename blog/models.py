# blog/models.py
from django.db import models
from django.utils import timezone
import random
from datetime import date

# 기존 Client 모델 (변경 없음)
class Client(models.Model):
    CLIENT_TYPES = [
        ('personal', '개인'),
        ('corporate', '기업'),
        ('government', '정부/공공기관'),
        ('startup', '스타트업'),
    ]
    name = models.CharField(max_length=100, unique=True, verbose_name="클라이언트 이름")
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, default='personal', verbose_name="클라이언트 유형")
    image_url = models.CharField(max_length=500, blank=True, null=True)# 클라이언트 이미지 URL 추가

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
            
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-written_date']
        verbose_name = "블로그 게시물"
        verbose_name_plural = "블로그 게시물"

class ShoppingKeyword(models.Model):
    # Foreign Key로 Client 모델과 연결
    client = models.ForeignKey(
        'Client', # 'Client' 문자열로 참조하여 순환 참조 방지 (Client 모델이 아래에 있어도 됨)
        on_delete=models.CASCADE, # 클라이언트 삭제 시 키워드도 삭제
        related_name='shopping_keywords', # Client 객체에서 이 키워드들을 역참조할 때 사용
        verbose_name="클라이언트"
    )
    keyword = models.CharField(max_length=255, verbose_name="키워드")
    # 키워드의 고유성을 위해 (client-keyword 쌍으로 고유하게)
    class Meta:
        unique_together = ('client', 'keyword')
        verbose_name = "쇼핑 키워드"
        verbose_name_plural = "쇼핑 키워드"

    def __str__(self):
        return f"[{self.client.name}] {self.keyword}"

class KeywordClick(models.Model):
    # ShoppingKeyword와 연결 (어떤 키워드가 클릭되었는지)
    keyword = models.ForeignKey(
        ShoppingKeyword,
        on_delete=models.CASCADE,
        related_name='clicks',
        verbose_name="쇼핑 키워드"
    )
    click_date = models.DateField(default=timezone.now, verbose_name="클릭 날짜")
    click_count = models.PositiveIntegerField(default=0, verbose_name="클릭 횟수")

    class Meta:
        # 특정 키워드가 특정 날짜에 몇 번 클릭되었는지 기록 (중복 방지)
        unique_together = ('keyword', 'click_date')
        verbose_name = "키워드 클릭 기록"
        verbose_name_plural = "키워드 클릭 기록"

    def __str__(self):
        return f"{self.keyword.keyword} - {self.click_date}: {self.click_count}회"
