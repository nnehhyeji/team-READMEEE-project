from django.db import models
from django.conf import settings
from django.utils import timezone 
from datetime import timedelta

# expires_at 기본값: 생성 시점 기준 24시간 후
def default_expires_at():
    return timezone.now() + timedelta(hours=24)

# 1. 게시글 모델
class Article(models.Model):
    """게시글"""
    EMOTION_CHOICES = [
        ('happy', '😊 행복'),
        ('proud', '😎 뿌듯함'),
        ('yummy', '😋 맛있음'),
        ('tired', '😴 피곤'),
        ('angry', '😤 화남'),
    ]
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='articles'
    )
    question = models.ForeignKey(
        'questions.Question',
        on_delete=models.CASCADE,
        related_name='articles'
    )
    content = models.TextField(max_length=1000) 
    image = models.CharField(
        max_length=500,
        blank=True, 
        null=True
    )  # Supabase Storage URL 저장
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES) 

    # BGM Info
    music_title = models.CharField(max_length=100, blank=True, null=True)
    music_artist = models.CharField(max_length=100, blank=True, null=True)

    # 공개 범위 및 24시간 후 비공개 처리
    is_public = models.BooleanField(default=True)   # 전체 공개 vs 나만 보기
    is_visible_to_others = models.BooleanField(default=True)    # 24시간 후 False
    
    # 타임스탬프
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=default_expires_at)  # 24시간 후 시각
    
    # 통계 요약 필드
    view_count = models.PositiveIntegerField(default=0)           # 총 조회수
    total_dwell_time = models.FloatField(default=0)               # 총 체류시간 (초)
    like_count = models.PositiveIntegerField(default=0)           # 총 좋아요 수

    class Meta:
        db_table = 'articles'
        ordering = ['-created_at']
        # 하루 1회 게시글 제한 (유저 + 질문 조합 유니크)
        unique_together = [['author', 'question']] 
    
    @property
    def avg_dwell_time(self):
        """평균 체류시간 (초 단위)"""
        if self.view_count == 0:
            return 0
        return self.total_dwell_time / self.view_count
    
    def __str__(self):
        return f"{self.author.username} - {self.question.release_date}"


# 2. 좋아요 모델
class Like(models.Model):
    """좋아요"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'likes'
        unique_together = [['user', 'article']]  # 중복 좋아요 방지
    
    def __str__(self):
        return f"{self.user.username} ❤️ Article {self.article.id}"


# 3. 댓글 모델
class Comment(models.Model):
    """댓글"""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.CharField(max_length=300) 
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at'] 
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"


# 4. 체류시간 모델
class DwellTime(models.Model):
    """체류시간"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='dwell_times'
    )
    dwell_seconds = models.FloatField()  # 체류 시간 (초)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'dwell_times'
        indexes = [
            models.Index(fields=['article', 'created_at']),  # 조회 성능 향상
        ]
    
    def __str__(self):
        return f"Article {self.article.id}: {self.dwell_seconds}s"