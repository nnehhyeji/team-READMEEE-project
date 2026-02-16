from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ViewSet Router 설정
router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')

urlpatterns = [
    
    # 주간/월간 베스트 (ArticleViewSet의 패턴과 겹치므로 최상단 배치)
    path('articles/weekly_best/', views.WeeklyBestView.as_view(), name='weekly_best'),
    path('articles/monthly_best/', views.MonthlyBestView.as_view(), name='monthly_best'),
    
    # 보안 업로드 URL 발급
    path('articles/upload-url/', views.GetUploadUrlView.as_view(), name='get_upload_url'),
    
    # ViewSet 연결 (Router)
    path('', include(router.urls)), 
    
    # Generics View
    
    # 내 통계
    path('statistics/my/', views.MyStatisticsView.as_view(), name='my_statistics'),
    
    # 단어 빈도 분석
    path('statistics/word_frequency/', views.WordFrequencyView.as_view(), name='word_frequency'),
    
    # 댓글 삭제 (DELETE /comments/{id}/)
    path('comments/<int:id>/', views.CommentDeleteView.as_view(), name='comment_delete'),
]