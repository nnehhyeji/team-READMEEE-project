from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.

# 사용자 모델 (FR-001, FR-003)
class User(AbstractUser):
    """
    FR-001: 이메일 기반 로그인 지원을 위해 email 필드를 unique로 설정
    FR-003: 프로필 이미지 및 바이오
    """
    # 기본 제공되는 first_name, last_name은 안 쓸 것이므로 None 처리
    first_name = None
    last_name = None
    
    # 1. 영문, 숫자, 밑줄(_)만 허용하는 검증기 생성
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message='사용자 이름은 영문, 숫자, 밑줄(_)만 포함할 수 있습니다.'
    )

    # 2. username 필드 오버라이딩 (덮어쓰기)
    username = models.CharField(
        max_length=30,               # 💡 8자 -> 30자로 확장
        unique=True,                # 💡 중복 금지
        validators=[username_validator], # 💡 영어/숫자 제한
        verbose_name='사용자 이름'
    )

    email = models.EmailField(unique=True, verbose_name='이메일')
    bio = models.TextField(max_length=200, blank=True)
    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/%d/', 
        blank=True, 
        null=True,
        max_length=500  # 💡 Supabase URL 길이를 위해 확장
    )

    # FR-031 통계를 위한 필드
    consecutive_days = models.IntegerField(default=0) # 연속 기록 일수
    max_consecutive_days = models.IntegerField(default=0) # 최장 연속 기록

    # FR-032 알림 설정 (SettingsPage 연동)
    noti_likes = models.BooleanField(default=True)    # 좋아요 알림
    noti_comments = models.BooleanField(default=True) # 댓글 알림
    noti_follows = models.BooleanField(default=True)  # 팔로우 알림 (requests)
    noti_weekly = models.BooleanField(default=True)   # 주간 리포트
    noti_daily = models.BooleanField(default=False)   # 데일리 리마인더

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 이메일 로그인을 위한 핵심 설정
    USERNAME_FIELD = 'email'  # 로그인을 이메일로 하겠다 선언
    REQUIRED_FIELDS = ['username'] # 슈퍼유저 생성 시 물어볼 필드

    # FR-001 소셜 로그인 처리를 위한 필드 추가
    PROVIDER_CHOICES = [
        ('email', '이메일'),
        ('google', '구글'),
        ('naver', '네이버'),
        ('kakao', '카카오'),
    ]
    provider = models.CharField(
        max_length=20, 
        choices=PROVIDER_CHOICES, 
        default='email', 
        verbose_name='가입 경로'
    )
    provider_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='소셜로그인 ID'
    )
    social_access_token = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='소셜 액세스 토큰'
    )

    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username
    

# 2. 팔로우 모델 (FR-020, FR-021)
class Follow(models.Model):
    """팔로우 관계"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'follows'
        unique_together = [['follower', 'following']]   # 중복 팔로우 방지
        
        # 자기 자신 팔로우 금지
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow'
            )
        ]
    
    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"