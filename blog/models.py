# blog/models.py
from django.db import models
from django.utils import timezone
import random

# Client 모델 (이전과 동일)
class Client(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="고객 이름")
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
    image_url = models.CharField(max_length=200, blank=True, verbose_name="클라이언트 이미지 URL")

    def __str__(self):
        return self.name

# ContentSubhead 모델 (이전과 동일)
class ContentSubhead(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subheads', verbose_name="관련 고객")
    name = models.CharField(max_length=100, verbose_name="컨텐츠 서브헤드")

    def __str__(self):
        return f"{self.client.name} - {self.name}"

    class Meta:
        unique_together = ('client', 'name')

# 제목 구성 요소 모델들 (이전과 동일)
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

# Blog 모델 수정: place_name 필드에 blank=True, null=True 추가
class Blog(models.Model):
    title = models.CharField(max_length=200, blank=True, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    
    # write.html에서 더 이상 입력받지 않으므로 blank=True, null=True를 추가하여 필수로 만들지 않습니다.
    place_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="장소명") 

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs', verbose_name="클라이언트")
    
    written_date = models.DateField(default=timezone.now, verbose_name="작성일")
    
    def save(self, *args, **kwargs):
        if not self.title:
            subhead_part = ""
            if self.client:
                subhead_qs = ContentSubhead.objects.filter(client=self.client)
                random_subhead = subhead_qs.order_by('?').first()
                if random_subhead:
                    subhead_part = random_subhead.name

            random_character = NumberCharacter.objects.order_by('?').first()
            random_talkstyle = TalkStyle.objects.order_by('?').first()
            random_aspect = ContentAspect.objects.order_by('?').first()

            char_part = random_character.name if random_character else ""
            talk_part = random_talkstyle.name if random_talkstyle else ""
            aspect_part = random_aspect.name if random_aspect else ""

            self.title = f"{subhead_part} {char_part} {talk_part} {aspect_part}".strip()
            
            if not self.title:
                self.title = "랜덤 조합 블로그 제목"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-written_date']
        verbose_name = "블로그 게시물"
        verbose_name_plural = "블로그 게시물"

