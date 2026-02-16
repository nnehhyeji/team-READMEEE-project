from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.today_question, name='today_question'),
    path('<str:date_str>/', views.question_by_date, name='question_by_date'),
]