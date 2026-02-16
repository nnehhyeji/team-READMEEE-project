from django.core.management.base import BaseCommand
from django.utils import timezone
from articles.models import Article
import sys

class Command(BaseCommand):
    help = '만료 시간(24시간)이 지난 게시글을 비공개로 전환합니다.'

    def handle(self, *args, **kwargs):
        # 윈도우 인코딩 설정
        sys.stdout.reconfigure(encoding='utf-8')

        now = timezone.now()
        
        # 1. 만료 시간은 지났는데(lt=less than), 아직 공개 상태(True)인 글 찾기
        expired_articles = Article.objects.filter(
            expires_at__lt=now, 
            is_visible_to_others=True
        )
        
        count = expired_articles.count()
        
        if count > 0:
            # 2. 일괄 업데이트 (비공개 처리)
            expired_articles.update(is_visible_to_others=False)
            self.stdout.write(self.style.SUCCESS(f'✅ [완료] 총 {count}개의 게시글이 비공개로 전환되었습니다.'))
        else:
            self.stdout.write(self.style.SUCCESS('✨ [양호] 비공개 처리할 만료된 게시글이 없습니다.'))