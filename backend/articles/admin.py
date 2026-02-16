from django.contrib import admin, messages
from .models import Article, Like, Comment, DwellTime

# Register your models here.

# Article 모델 Admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """게시글 Admin"""
    # 1. 목록에 보여줄 항목들 (expires_at 추가 추천)
    list_display = [
        'id', 'author', 'question', 'like_count', 'view_count', 
        'total_dwell_time', 'created_at', 'expires_at', 'is_public'
    ]
    
    # 2. 목록에서 바로 수정할 항목들 (expires_at 추가 추천)
    list_editable = [
        'like_count', 'view_count', 'total_dwell_time', 'created_at', 'expires_at'
    ]
    
    list_filter = ['emotion', 'is_public', 'is_visible_to_others', 'created_at']
    search_fields = ['author__username', 'content']
    ordering = ['-created_at']
    actions = ['make_published', 'make_private', 'reset_statistics']
    
    # 3. 진짜 읽기 전용인 계산된 필드만 남기기
    readonly_fields = ['avg_dwell_time']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('author', 'question', 'content', 'image', 'emotion')
        }),
        ('공개 설정', {
            'fields': ('is_public', 'is_visible_to_others')
        }),
        ('통계 설정', {
            'fields': ('view_count', 'total_dwell_time', 'like_count', 'avg_dwell_time'),
            'classes': ('collapse',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.action(description="선택된 게시글을 모두 공개로 전환")
    def make_published(self, request, queryset):
        updated_count = queryset.update(is_public=True, is_visible_to_others=True)
        self.message_user(request, f"{updated_count}개의 게시글이 공개 상태로 변경되었습니다.")

    @admin.action(description="선택된 게시글을 모두 비공개로 전환")
    def make_private(self, request, queryset):
        updated_count = queryset.update(is_public=False, is_visible_to_others=False)
        self.message_user(request, f"{updated_count}개의 게시글이 비공개 상태로 변경되었습니다.", messages.WARNING)

    @admin.action(description="선택된 게시글의 좋아요/조회수 초기화")
    def reset_statistics(self, request, queryset):
        updated_count = queryset.update(like_count=0, view_count=0, total_dwell_time=0)
        self.message_user(request, f"{updated_count}개의 게시글 통계가 초기화되었습니다.")
    
    def avg_dwell_time(self, obj):
        return f"{obj.avg_dwell_time:.2f}초"
    avg_dwell_time.short_description = '평균 체류시간'


# Like 모델 Admin
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """좋아요 Admin"""
    list_display = ['user', 'article', 'created_at']
    list_filter = ['created_at']
    list_editable = ['created_at']
    search_fields = ['user__username', 'article__id']
    ordering = ['-created_at']
    
    # readonly_fields = ['created_at']


# Comment 모델 Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """댓글 Admin"""
    list_display = ['author', 'article', 'content_preview', 'created_at']
    list_filter = ['created_at']
    list_editable = ['created_at']
    search_fields = ['author__username', 'content']
    ordering = ['-created_at']
    
    # readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = '댓글 내용'


# DwellTime 모델 Admin
@admin.register(DwellTime)
class DwellTimeAdmin(admin.ModelAdmin):
    """체류시간 Admin"""
    list_display = ['article', 'dwell_seconds', 'created_at']
    list_filter = ['created_at']
    list_editable = ['created_at']
    search_fields = ['article__id']
    ordering = ['-created_at']
    
    # readonly_fields = ['created_at']

