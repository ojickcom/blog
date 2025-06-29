from django.db import models
from django.utils import timezone
import random

# --- 새로운 모델 추가 시작 ---

class ContentTitle(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="컨텐츠 주제")

    def __str__(self):
        return self.name

class ContentNumberCharacter(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="글자 수 특성")

    def __str__(self):
        return self.name

class ContentTalkstyle(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="말투 스타일")

    def __str__(self):
        return self.name

class ContentAspect(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="컨텐츠 관점")

    def __str__(self):
        return self.name

# --- 새로운 모델 추가 끝 ---

class Blog(models.Model):
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    client_type = models.CharField(max_length=20)
    image_url = models.CharField(max_length=50)
    place_name = models.CharField(max_length=20)
    # 이제 이 필드들은 Blog 모델에 직접 저장되는 대신,
    # 위에서 정의한 별도의 모델에서 랜덤으로 가져올 것입니다.
    # 따라서 Blog 모델에서 해당 필드들은 제거합니다.
    # content_title = models.CharField(max_length=20)
    # content_number_character = models.CharField(max_length=20)
    # content_talkstyle = models.CharField(max_length=20)
    # content_aspect = models.CharField(max_length=20)
    written_date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # title을 랜덤 조합으로 생성
        if not self.title:
            # 각 모델에서 랜덤으로 하나씩 선택
            random_title = ContentTitle.objects.order_by('?').first()
            random_character = ContentNumberCharacter.objects.order_by('?').first()
            random_talkstyle = ContentTalkstyle.objects.order_by('?').first()
            random_aspect = ContentAspect.objects.order_by('?').first()

            # 선택된 값이 None일 경우를 대비하여 빈 문자열 처리
            title_part = random_title.name if random_title else ""
            char_part = random_character.name if random_character else ""
            talk_part = random_talkstyle.name if random_talkstyle else ""
            aspect_part = random_aspect.name if random_aspect else ""

            self.title = f"{title_part} {char_part} {talk_part} {aspect_part}".strip()
            # 모든 구성 요소가 비어있을 경우를 대비하여 최종 제목이 비어있지 않도록 처리
            if not self.title:
                self.title = "무제 블로그 게시물" # 또는 다른 기본 제목

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-written_date']