from rest_framework import serializers
from .models import Question


# [1] 질문 조회 시리얼라이저
class QuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Question
        fields = ['id', 'content', 'category', 'release_date', 'created_at', 
                 'rec_title', 'rec_artist', 'rec_reason', 'rec_video_id'] 
        read_only_fields = ['id', 'created_at']


# [2] 질문 생성 시리얼라이저 (관리자/AI용)
class QuestionCreateSerializer(serializers.ModelSerializer):
    """질문 생성 (FR-004)"""
    
    class Meta:
        model = Question
        fields = ['content', 'category', 'release_date']
    
    def validate_content(self, value):
        """질문 내용 검증"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("질문 내용을 입력해주세요.")
        if len(value) > 200:
            raise serializers.ValidationError("질문은 최대 200자입니다.")
        return value
    
    def validate_release_date(self, value):
        """날짜 중복 체크"""
        if Question.objects.filter(release_date=value).exists():
            raise serializers.ValidationError("해당 날짜의 질문이 이미 존재합니다.")
        return value