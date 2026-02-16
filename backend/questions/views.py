from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime

from .models import Question
from .serializers import QuestionSerializer


# [1] 오늘의 질문 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def today_question(request):
    """오늘의 질문"""
    today = timezone.localdate()
    question = get_object_or_404(Question, release_date=today)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)


# [2] 특정 날짜 질문 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def question_by_date(request, date_str):
    """특정 날짜의 질문 (YYYY-MM-DD)"""
    # 날짜 형식 검증
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    question = get_object_or_404(Question, release_date=target_date)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)