from django.db import models
from django.utils import timezone
import random

class Blog(models.Model):
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    client_type = models.CharField(max_length=20)
    image_url = models.URLField(max_length=50)
    place_name = models.CharField(max_length=20)
    content_title = models.CharField(max_length=20)
    content_number_character = models.CharField(max_length=20)
    content_talkstyle = models.CharField(max_length=20)
    content_aspect = models.CharField(max_length=20)
    written_date = models.DateField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        # title을 4개 구성요소의 랜덤 조합으로 생성
        if not self.title:
            components = [
                self.content_title,
                self.content_number_character,
                self.content_talkstyle,
                self.content_aspect
            ]
            # 빈 값이 아닌 것들만 필터링
            valid_components = [comp for comp in components if comp.strip()]
            
            if valid_components:
                # 랜덤하게 섞어서 조합
                random.shuffle(valid_components)
                self.title = ' '.join(valid_components)
            else:
                self.title = "제목 없음"
                
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-written_date']