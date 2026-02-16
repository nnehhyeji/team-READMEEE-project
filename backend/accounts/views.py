from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import requests
import os
from django.conf import settings
from django.shortcuts import redirect
import jwt
from uuid import uuid4
from uuid import uuid4
from supabase import create_client, Client
from rest_framework import generics

# [0] Supabase Upload URL 발급 (프로필용)
class GetProfileUploadUrlView(generics.GenericAPIView):
    """
    [Security] 프로필 이미지 업로드용 Signed URL 발급 (accounts 앱용)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        filename = request.data.get('filename')
        if not filename:
            return Response({'error': 'Filename is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # .env 로드
        from dotenv import load_dotenv
        load_dotenv()
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        # [Fallback] Supabase 설정이 없으면 로컬 업로드 모드로 전환
        if not url or not key:
            return Response({'storage': 'local'})
        
        supabase: Client = create_client(url, key)
        
        # 1. 파일 확장자 추출
        ext = filename.split('.')[-1]
        
        # 2. 안전한 파일명 생성 (UUID) - 한글 파일명 등 인코딩 문제 방지
        safe_filename = f"{uuid4()}.{ext}"

        # 경로 설정: uploads/profiles/{user_id}/{safe_filename}
        storage_path = f"uploads/profiles/{request.user.id}/{safe_filename}"
        
        try:
            # Signed Upload URL 생성
            res = supabase.storage.from_('ReadMe-images').create_signed_upload_url(storage_path)
            
            return Response({
                'signedUrl': res['signed_url'],
                'path': storage_path
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import Follow
from .serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    FollowSerializer,
    PasswordChangeSerializer  
)

User = get_user_model()


# [1] 회원가입
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """회원가입"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [2] 로그인
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """로그인"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': '이메일과 비밀번호를 입력해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=email, password=password)
    if user:
        update_last_login(None, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(
        {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


# [3] 로그아웃
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response({'message': '로그아웃되었습니다.'})


# [4] 프로필 조회 (username 기반 & 비회원 허용)
@api_view(['GET'])
@permission_classes([AllowAny]) # 비회원 조회 가능
def user_profile(request, username): 
    """프로필 조회"""
    user = get_object_or_404(User, username=username) 
    serializer = UserPublicSerializer(user, context={'request': request})
    return Response(serializer.data)


# [5] 내 프로필 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# [6] 프로필 수정
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserUpdateSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [7] 팔로우 (username 기반)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username): 
    """팔로우"""
    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        return Response(
            {'error': '자기 자신을 팔로우할 수 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if Follow.objects.filter(follower=request.user, following=target_user).exists():
        return Response(
            {'error': '이미 팔로우 중입니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    Follow.objects.create(follower=request.user, following=target_user)
    return Response({'message': '팔로우했습니다.'}, status=status.HTTP_201_CREATED)


# [8] 언팔로우 (username 기반)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username): 
    """언팔로우"""
    target_user = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(follower=request.user, following=target_user).first()
    
    if not follow:
        return Response(
            {'error': '팔로우하지 않은 사용자입니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    follow.delete()
    return Response({'message': '언팔로우했습니다.'})


# [9] 팔로워 목록
@api_view(['GET'])
@permission_classes([AllowAny])
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(following=user).select_related('follower')
    # 목록 내 유저들의 팔로우 상태 확인용
    serializer = FollowSerializer(follows, many=True, context={'request': request})
    return Response(serializer.data)


# [10] 팔로잉 목록
@api_view(['GET'])
@permission_classes([AllowAny])
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(follower=user).select_related('following')
    # 💡 여기도 context 추가
    serializer = FollowSerializer(follows, many=True, context={'request': request})
    return Response(serializer.data)


# [11] 회원탈퇴
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    
    # 네이버 연동 해제 (Unlink)
    if user.provider == 'naver' and user.social_access_token:
        try:
            client_id = os.environ.get('NAVER_CLIENT_ID')
            client_secret = os.environ.get('NAVER_CLIENT_SECRET')
            access_token = user.social_access_token
            
            # 네이버 연동 해제 API 호출
            unlink_url = "https://nid.naver.com/oauth2.0/token"
            unlink_params = {
                'grant_type': 'delete',
                'client_id': client_id,
                'client_secret': client_secret,
                'access_token': access_token,
                'service_provider': 'NAVER'
            }
            res = requests.post(unlink_url, params=unlink_params)
            print(f"DEBUG: Naver Unlink Response: {res.json()}")
            
        except Exception as e:
            pass
            
    # 카카오 연동 해제 (Unlink)
    if user.provider == 'kakao' and user.social_access_token:
        try:
            unlink_url = "https://kapi.kakao.com/v1/user/unlink"
            headers = {
                "Authorization": f"Bearer {user.social_access_token}"
            }
            res = requests.post(unlink_url, headers=headers)
        except Exception:
            pass


    request.user.delete()
    return Response({'message': '회원탈퇴가 완료되었습니다.'}, status=status.HTTP_204_NO_CONTENT)


# [12] 비밀번호 변경
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        update_last_login(None, request.user)
        return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# [13] 사용자 검색
@api_view(['GET'])
@permission_classes([AllowAny])
def search_users(request):
    query = request.query_params.get('q', '')
    
    if request.user.is_authenticated:
        # 로그인 유저: 나 자신 + 내가 이미 팔로우한 사람 + 관리자 제외
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        base_qs = User.objects.exclude(id=request.user.id).exclude(id__in=following_ids).exclude(is_superuser=True)
    else:
        # 비로그인: 관리자만 제외
        base_qs = User.objects.exclude(is_superuser=True)

    if not query:
        # 검색어 없으면 랜덤 추천 (필터링된 목록에서 5명)
        users = base_qs.order_by('?')[:5]
    else:
        users = base_qs.filter(username__icontains=query)
    
    serializer = UserPublicSerializer(users, many=True, context={'request': request})
    return Response(serializer.data)


# [14] 구글 로그인
@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    """구글 로그인 페이지로 리다이렉트 (테스트용)"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    redirect_uri = os.environ.get('GOOGLE_CALLBACK_URI')
    
    


    if not client_id or not redirect_uri:
        return Response(
            {'error': '서버에 GOOGLE_CLIENT_ID 또는 GOOGLE_CALLBACK_URI 설정이 없습니다.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # scope: email, profile
    google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth"
    
    auth_url = (
        f"{google_auth_api}?client_id={client_id}&redirect_uri={redirect_uri}"
        f"&response_type=code&scope=email%20profile&prompt=select_account"
    )
    
    return redirect(auth_url)


@api_view(['POST']) 
@permission_classes([AllowAny])
def google_callback(request):
    """구글 로그인 콜백 (Code -> Token -> User Info -> JWT)"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.environ.get('GOOGLE_CALLBACK_URI')
    code = request.data.get('code')

    
    # client_secret 존재 여부 확인 (값은 로그에 찍지 않음)
    if not client_secret:

        return Response({'error': '서버 설정 오류: GOOGLE_CLIENT_SECRET가 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 1. Code 검증
    if not code:
        return Response({'error': 'Authorization code is missing.'}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Access Token 요청
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': client_id, 
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    
    token_req = requests.post(token_url, data=token_data)
    token_req_json = token_req.json()
    
  


    error = token_req_json.get('error')
    if error is not None:
        return Response({'error': error, 'detail': token_req_json.get('error_description')}, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = token_req_json.get('access_token')

    # 3. User Info 요청
    user_req = requests.get(
        f"https://www.googleapis.com/oauth2/v2/userinfo",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    user_req_json = user_req.json()
    email = user_req_json.get('email')
    
    if not email:
        return Response({'error': 'Failed to get email from Google.'}, status=status.HTTP_400_BAD_REQUEST)

    # 4. User 확인 및 생성
    try:
        user = User.objects.get(email=email)
        # 이미 가입된 이메일 (Provider 체크 여부는 정책 결정: 그냥 로그인 시킴)
        if user.provider != 'google':
            # 기존 이메일 가입자라면, 그냥 로그인 성공 처리하거나 에러 반환
            # 여기서는 편의상 로그인 허용하되, provider 정보는 유지
            pass
            
            # 혹시나 provider가 다르면 연동할지 묻는 로직이 정석이지만, 여기선 자동 연동으로 간주
            if not user.provider:
                user.provider = 'google'
                user.provider_id = user_req_json.get('id')
                user.save()
            
    except User.DoesNotExist:
        # 신규 가입
        import re
        # 이메일 앞부분 추출
        username = email.split('@')[0]
        # 정규식(영문,숫자,_)에 맞지 않는 문자 제거 (예: 점(.), 하이픈(-) 등)
        username = re.sub(r'[^a-zA-Z0-9_]', '', username)
        # 길이 제한 (30자)
        username = username[:30]
        
        # 만약 다 지워져서 없거나 중복이면 랜덤 생성
        if not username or User.objects.filter(username=username).exists():
            username = f"user_{str(uuid4())[:8]}"

        user = User.objects.create(
            email=email,
            username=username,
            provider='google',
            provider_id=user_req_json.get('id')
        )
        # 비밀번호는 설정 안함 (Unusable password)
        user.set_unusable_password()
        user.save()

    # 5. JWT 발급
    update_last_login(None, user)
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


# [16] 카카오 로그인
@api_view(['GET'])
@permission_classes([AllowAny])
def kakao_login(request):
    """카카오 로그인 (인가 코드 요청)"""
    client_id = os.environ.get('KAKAO_CLIENT_ID')
    redirect_uri = os.environ.get('KAKAO_CALLBACK_URI')
    
    if not client_id or not redirect_uri:
        return Response(
            {'error': '서버에 KAKAO_CLIENT_ID 또는 KAKAO_CALLBACK_URI 설정이 없습니다.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 카카오 로그인 URL 생성
    kakao_auth_api = "https://kauth.kakao.com/oauth/authorize"
    response = redirect(
        f"{kakao_auth_api}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&prompt=login"
    )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_callback(request):
    """카카오 로그인 콜백"""
    client_id = os.environ.get('KAKAO_CLIENT_ID')
    client_secret = os.environ.get('KAKAO_CLIENT_SECRET') 
    redirect_uri = os.environ.get('KAKAO_CALLBACK_URI')
    code = request.data.get('code')

    

    
    if not client_id:
        return Response({'error': '서버 설정 오류: KAKAO_CLIENT_ID가 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not code:
        return Response({'error': 'Authorization code is missing.'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Access Token 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': code,
    }
    
    # Client Secret이 설정
    if client_secret:
        token_data['client_secret'] = client_secret
    
    # 카카오는 Content-type: application/x-www-form-urlencoded 권장 (requests가 자동 처리)
    token_req = requests.post(token_url, data=token_data)
    token_req_json = token_req.json()
    

    
    error = token_req_json.get('error')
    if error is not None:
        return Response({'error': error, 'detail': token_req_json.get('error_description')}, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = token_req_json.get('access_token')

    # 2. User Info 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    user_req = requests.get(
        user_info_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
        }
    )
    user_req_json = user_req.json()
    
    # 3. 사용자 정보 추출
    kakao_id = str(user_req_json.get('id')) # 고유 ID
    kakao_account = user_req_json.get('kakao_account')
    
    if not kakao_account:
        return Response({'error': 'Failed to get user info from Kakao.'}, status=status.HTTP_400_BAD_REQUEST)

    email = kakao_account.get('email')
    
    # 💡 [핵심] 이메일이 없으면 가상 이메일 생성
    if not email:
        email = f"{kakao_id}@kakao.user"

    # 4. User 확인 및 생성
    try:
        user = User.objects.get(email=email)
        
        # 로그인 시마다 토큰 업데이트 (연동 해제 등 대비)
        user.provider = 'kakao'
        user.provider_id = kakao_id
        user.social_access_token = access_token
        user.save()
            
    except User.DoesNotExist:
        # 신규 가입
        import re
        
        # 닉네임 우선 사용 로직
        # kakao_account.profile.nickname 또는 properties.nickname
        profile = kakao_account.get('profile')
        nickname = profile.get('nickname') if profile else None
        
        if not nickname:
             properties = user_req_json.get('properties')
             nickname = properties.get('nickname') if properties else None

        if nickname:
            # 한글/특수문자 제거하고 영문/숫자/_만 남김
            username = re.sub(r'[^a-zA-Z0-9_]', '', nickname)
            # 만약 다 지워져서(예: 순수 한글 닉네임) 빈 문자열이면 카카오 ID 사용
            if not username:
                 username = f"user_{kakao_id}"
        else:
            username = f"user_{kakao_id}"

        # 길이 제한 (30자)
        username = username[:30]
        
        # 중복 체크 및 처리
        if User.objects.filter(username=username).exists():
            from uuid import uuid4
            # 기존 닉네임 + 랜덤 4자리
            username = f"{username}_{str(uuid4())[:4]}"

        user = User.objects.create(
            email=email,
            username=username,
            provider='kakao',
            provider_id=kakao_id,
            social_access_token=access_token
        )
        user.set_unusable_password()
        user.save()

    # 5. JWT 발급
    update_last_login(None, user)
    refresh = RefreshToken.for_user(user)
    
    # 닉네임 변경 여부 확인 (신규/기존 모두 확인 가능하지만 주로 신규 가입 시 의미 있음)
    # 간단히: 요청한 닉네임(nickname)과 실제 저장된 닉네임(user.username)이 다르면 True
    # 단, nickname이 None이었던 경우는 제외
    is_username_changed = False
    if 'nickname' in locals() and nickname:
        
        # " 사용자가 기대한 닉네임"과 "실제 닉네임"이 다른지만 체크
        if subtitle_clean_username := re.sub(r'[^a-zA-Z0-9_]', '', nickname):
             if user.username != subtitle_clean_username:
                 is_username_changed = True
        else:
             # 다 지워져서(특수문자뿐이라) 임시 아이디 된 경우
             is_username_changed = True

    return Response({
        'user': UserSerializer(user).data,
        'username_changed': is_username_changed, 
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


# [15] 네이버 로그인
@api_view(['GET'])
@permission_classes([AllowAny])
def naver_login(request):
    """네이버 로그인 페이지로 리다이렉트"""
    client_id = os.environ.get('NAVER_CLIENT_ID')
    redirect_uri = os.environ.get('NAVER_CALLBACK_URI')
    state = str(uuid4()) # CSRF 방지용 state 토큰 생성



    if not client_id or not redirect_uri:
        return Response(
            {'error': '서버에 NAVER_CLIENT_ID 또는 NAVER_CALLBACK_URI 설정이 없습니다.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 네이버는 state 필수
    naver_auth_api = "https://nid.naver.com/oauth2.0/authorize"
    
    # auth_type=reprompt 대신 prompt=login 시도 (또는 제거)
    response = redirect(
        f"{naver_auth_api}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state={state}&prompt=login"
    )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def naver_callback(request):
    """네이버 로그인 콜백"""
    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')
    code = request.data.get('code')
    state = request.data.get('state')


    
    if not client_secret:

        return Response({'error': '서버 설정 오류: NAVER_CLIENT_SECRET가 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not client_id:
        return Response({'error': '서버 설정 오류: NAVER_CLIENT_ID가 없습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not code:
        return Response({'error': 'Authorization code is missing.'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Access Token 요청
    token_url = "https://nid.naver.com/oauth2.0/token"
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': client_id, 
        'client_secret': client_secret,
        'code': code,
        'state': state,
    }
    
    token_req = requests.post(token_url, params=token_params)
    token_req_json = token_req.json()
    

    
    error = token_req_json.get('error')
    if error is not None:
        return Response({'error': error, 'detail': token_req_json.get('error_description')}, status=status.HTTP_400_BAD_REQUEST)
    
    access_token = token_req_json.get('access_token')

    # 2. User Info 요청
    user_info_url = "https://openapi.naver.com/v1/nid/me"
    user_req = requests.get(
        user_info_url,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    user_req_json = user_req.json()
    
    # 네이버는 응답 코드가 '00'이어야 성공
    if user_req_json.get('resultcode') != '00':
        return Response({'error': 'Failed to get user info from Naver.'}, status=status.HTTP_400_BAD_REQUEST)

    naver_account = user_req_json.get('response') # response 키 안에 사용자 정보 있음
    email = naver_account.get('email')
    
    if not email:
        return Response({'error': '이메일 정보가 없습니다. (정보 제공 동의 필요)'}, status=status.HTTP_400_BAD_REQUEST)

    # 3. User 확인 및 생성
    try:
        user = User.objects.get(email=email)
        
        # 로그인 할 때마다 최신 토큰 저장 (연동 해제 시 필요)
        user.provider = 'naver'
        user.provider_id = naver_account.get('id')
        user.social_access_token = access_token
        user.save()
            
    except User.DoesNotExist:
        # 신규 가입
        import re
        username = email.split('@')[0]
        # 정규식(영문,숫자,_)에 맞지 않는 문자 제거
        username = re.sub(r'[^a-zA-Z0-9_]', '', username)
        # 길이 제한 (30자)
        username = username[:30]

        if not username or User.objects.filter(username=username).exists():
            username = f"user_{str(uuid4())[:8]}"

        user = User.objects.create(
            email=email,
            username=username,
            provider='naver',
            provider_id=naver_account.get('id'),
            social_access_token=access_token # Access Token 저장
        )
        user.set_unusable_password()
        user.save()

    # 4. JWT 발급
    update_last_login(None, user)
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })