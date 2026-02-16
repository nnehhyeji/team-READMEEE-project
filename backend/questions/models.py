from django.db import models

# Create your models here.

# 질문 모델 (FR-004, FR-006)
class Question(models.Model):
    """오늘의 질문"""
    CATEGORY_CHOICES = [
        ('culture', '시사/문화'), # 30%
        ('reflection', '자기성찰'), # 25%
        ('daily', '일상 기록'), # 25%
        ('creative', '창의적'), # 20%
    ]
    
    content = models.CharField(max_length=200) # FR-004: 질문의 최대 길이
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    # AI 추천 음악
    rec_title = models.CharField(max_length=100, blank=True, null=True)
    rec_artist = models.CharField(max_length=100, blank=True, null=True)
    rec_reason = models.CharField(max_length=200, blank=True, null=True)
    rec_video_id = models.CharField(max_length=50, blank=True, null=True) 

    release_date = models.DateField(unique=True) # (질문공개일)날짜별 1개 고정
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['-release_date'] # 질문 목록 조회하면 항상 최신 질문이 맨 위에
    
    def __str__(self):
        return f"{self.release_date}: {self.content}"