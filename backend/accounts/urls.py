from django.urls import path
from . import views

urlpatterns = [
    # 1. 회원가입/로그인
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    
    # 2. 로그아웃 
    path('logout/', views.logout, name='logout'),
    
    # 3. 프로필 관련 
    path('profile/my/', views.my_profile, name='my_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # <str:username>으로 변경
    path('users/<str:username>/', views.user_profile, name='user_profile'), 
    
    # [프로필 이미지 업로드용 URL 발급
    path('upload-url/', views.GetProfileUploadUrlView.as_view(), name='profile_upload_url'),
    
    # 4. 팔로우 관련
    path('users/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('users/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('users/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('users/<str:username>/following/', views.following_list, name='following_list'),
    # 5. 회원탈퇴
    path('withdraw/', views.delete_account, name='withdraw'),

    # 6. 비밀번호 변경
    path('password/change/', views.change_password, name='change_password'), 

    # 7. 사용자 검색
    path('search/', views.search_users, name='search_users'),

    # 8. 소셜 로그인
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    
    path('naver/login/', views.naver_login, name='naver_login'),
    path('naver/callback/', views.naver_callback, name='naver_callback'),

    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
]