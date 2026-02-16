from django.contrib import admin
from .models import Question

# Register your models here.

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """질문 Admin"""
    list_display = ['release_date', 'content', 'category', 'created_at']
    list_filter = ['category', 'release_date']
    search_fields = ['content']
    ordering = ['-release_date']
    
    # 읽기 전용 필드
    readonly_fields = ['created_at']
    
    # 필드 그룹화
    fieldsets = (
        ('질문 정보', {
            'fields': ('content', 'category', 'release_date')
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # 접을 수 있게
        }),
    )