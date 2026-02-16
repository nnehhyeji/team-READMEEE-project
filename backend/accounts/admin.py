from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow

# Register your models here.

# User 모델 Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """커스텀 유저 Admin"""
    list_display = ['email', 'username', 'consecutive_days', 'max_consecutive_days', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'username']
    ordering = ['-created_at']
    
    # 상세 페이지 필드 구성
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('개인정보', {'fields': ('bio', 'profile_image')}),
        ('통계', {'fields': ('consecutive_days', 'max_consecutive_days')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 날짜', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 유저 생성 시 필드
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


# Follow 모델 Admin
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """팔로우 Admin"""
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    ordering = ['-created_at']
    
    # 읽기 전용 필드
    readonly_fields = ['created_at']