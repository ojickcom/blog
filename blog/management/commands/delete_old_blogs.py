from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Blog


class Command(BaseCommand):
    help = '4일이 지난 완료 블로그 포스팅을 자동 삭제합니다.'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=4)
        deleted_count, _ = Blog.objects.filter(
            blog_write=True,
            written_date__lt=cutoff,
        ).delete()
        self.stdout.write(f'[{timezone.now()}] {deleted_count}건 삭제 완료.')
