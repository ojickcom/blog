# blog/models.py
from django.db import models
from django.utils import timezone
import random

# 1. 새로운 모델 추가: 클라이언트 정보
class Client(models.Model):
    # a. client_name: 고객 이름 (Unique로 설정하여 중복 방지)
    name = models.CharField(max_length=100, unique=True, verbose_name="고객 이름")

    # b. client_type: place, shopping, web_document 중 선택 (나중에 추가 가능)
    # choices를 사용하여 제한된 선택지를 제공합니다.
    CLIENT_TYPE_CHOICES = [
        ('place', '장소'),
        ('shopping', '쇼핑'),
        ('web_document', '웹 문서'),
    ]
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='place',
        verbose_name="클라이언트 타입"
    )
    # c. image_url: 클라이언트와 연결되는 하나의 이미지 URL
    image_url = models.CharField(max_length=200, blank=True, verbose_name="클라이언트 이미지 URL") # 길이를 넉넉하게 변경

    def __str__(self):
        return self.name

# 2. 새로운 모델 추가: content_subhead (client_name에 여러 개 연결)
class ContentSubhead(models.Model):
    # d. content_subhead는 client_name에 여러 개의 값을 가집니다.
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subheads', verbose_name="관련 고객")
    name = models.CharField(max_length=100, verbose_name="컨텐츠 서브헤드")

    def __str__(self):
        return f"{self.client.name} - {self.name}"

    class Meta:
        # 특정 클라이언트 내에서 서브헤드 이름이 중복되지 않도록 (선택 사항)
        unique_together = ('client', 'name')

# 3. 새로운 모델 추가: 제목 조합을 위한 구성 요소
# content_title은 이제 이들의 조합으로 생성되므로, 이 필드들은 Blog 모델에서 제거됩니다.
# 대신 이들을 담을 새로운 모델을 만듭니다.

class NumberCharacter(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="글자 수 특성")

    def __str__(self):
        return self.name

class TalkStyle(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="말투 스타일")

    def __str__(self):
        return self.name

class ContentAspect(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="컨텐츠 관점")

    def __str__(self):
        return self.name

# 기존 Blog 모델 수정
class Blog(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name="제목") # 제목 길이 넉넉하게 조정
    content = models.TextField(verbose_name="내용")
    
    # client_type, image_url, place_name은 이제 Client 모델의 필드를 참조합니다.
    # place_name은 client와 무관하게 각 블로그에 고유하게 들어갈 수 있으므로 Blog 모델에 유지
    place_name = models.CharField(max_length=50, verbose_name="장소명") # 길이 넉넉하게 조정

    # Client 모델과의 ForeignKey 관계 추가
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs', verbose_name="클라이언트")

    # content_title, content_number_character, content_talkstyle, content_aspect 필드 제거
    # 대신 Blog.save()에서 이들 모델의 값을 가져와 title을 조합합니다.
    
    written_date = models.DateField(default=timezone.now, verbose_name="작성일")
    
    def save(self, *args, **kwargs):
        # title이 비어있을 때만 랜덤 조합으로 생성
        if not self.title:
            # 1. 클라이언트에 연결된 content_subhead에서 랜덤 선택
            subhead_part = ""
            if self.client: # 클라이언트가 선택된 경우에만 subhead 가져옴
                subhead_qs = ContentSubhead.objects.filter(client=self.client)
                random_subhead = subhead_qs.order_by('?').first()
                if random_subhead:
                    subhead_part = random_subhead.name

            # 2. 기타 제목 구성 요소에서 랜덤 선택
            random_character = NumberCharacter.objects.order_by('?').first()
            random_talkstyle = TalkStyle.objects.order_by('?').first()
            random_aspect = ContentAspect.objects.order_by('?').first()

            char_part = random_character.name if random_character else ""
            talk_part = random_talkstyle.name if random_talkstyle else ""
            aspect_part = random_aspect.name if random_aspect else ""

            # 모든 부분 조합
            # content_title 대신 content_subhead를 사용
            self.title = f"{subhead_part} {char_part} {talk_part} {aspect_part}".strip()
            
            # 모든 구성 요소가 비어있을 경우를 대비하여 기본 제목 설정
            if not self.title:
                self.title = "랜덤 조합 블로그 제목"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-written_date']
        verbose_name = "블로그 게시물"
        verbose_name_plural = "블로그 게시물"

