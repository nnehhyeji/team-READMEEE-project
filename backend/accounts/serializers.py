from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow
import re

User = get_user_model()

# Signed URL 생성
def get_signed_image_url(image_field, request=None):
    if not image_field:
        return None
    
    image_url = str(image_field)
    
    # [Fallback] 로컬 저장소 파일인 경우 (http로 시작하지 않고 /media/ 혹은 profiles/ 등으로 시작)
    if not image_url.startswith('http'):
        from django.conf import settings
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        # 이미 media_url이 포함되어 있는지 확인
        if image_url.startswith(media_url):
            full_path = image_url
        else:
            full_path = f"{media_url}{image_url}"
        
        if request:
            return request.build_absolute_uri(full_path)
        return full_path

    return image_url

# [0] 가벼운 유저 요약 시리얼라이저 (검색 결과, 팔로우 목록에서 사용)
class UserSummarySerializer(serializers.ModelSerializer):
    """목록 조회용 요약 정보 + 팔로우 여부 포함"""
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'is_following']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 나(request.user)가 이 사람(obj)을 팔로우하고 있는지 확인
            return obj.followers.filter(follower=request.user).exists()
        return False
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_image:
            request = self.context.get('request')
            ret['profile_image'] = get_signed_image_url(instance.profile_image, request)
        return ret


# [1] 기본 유저 상세 시리얼라이저 (내 프로필용)
class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'bio', 'profile_image',
            'consecutive_days', 'max_consecutive_days',
            'follower_count', 'following_count', 'created_at',
            # 알림 설정
            'noti_likes', 'noti_comments', 'noti_follows', 
            'noti_weekly', 'noti_daily',
            'provider'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'consecutive_days']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_image:
            request = self.context.get('request')
            ret['profile_image'] = get_signed_image_url(instance.profile_image, request)
        return ret


# [2] 타인 프로필 조회용 (공개 범위 제한 + 팔로우 여부 필수)
class UserPublicSerializer(serializers.ModelSerializer):
    """타인 프로필 조회용 (is_following 필드 추가)"""
    follower_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    is_following = serializers.SerializerMethodField() # 💡 핵심: 이게 있어야 버튼이 바뀝니다.
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'bio', 'profile_image', 
            'follower_count', 'following_count', 'is_following'
        ]
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(follower=request.user).exists()
        return False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_image:
            request = self.context.get('request')
            ret['profile_image'] = get_signed_image_url(instance.profile_image, request)
        return ret


# [3] 회원가입 시리얼라이저
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm']
        extra_kwargs = {
            'username': {
                'max_length': 8,
                'error_messages': {'unique': "이미 사용 중인 아이디입니다."}
            }
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


# [4] 프로필 수정 시리얼라이저 
class UserUpdateSerializer(serializers.ModelSerializer):
    # Supabase Path(문자열)와 로컬 파일(File)을 모두 수용하기 위해 명시적인 필드 정의 제거
    # 혹은 custom field 사용. 여기서는 default ImageField가 String/File 둘 다 처리하도록 유도
    profile_image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'username', 'bio', 'profile_image',
            'noti_likes', 'noti_comments', 'noti_follows', 
            'noti_weekly', 'noti_daily'
        ]

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 아이디입니다.")
        return value


# [5] 팔로우 목록 시리얼라이저 (프론트엔드 모달 구조에 맞춤)
class FollowSerializer(serializers.ModelSerializer):
    """팔로워/팔로잉 목록 조회 (follower_info, following_info 이름 사용)"""
    follower_info = UserSummarySerializer(source='follower', read_only=True)
    following_info = UserSummarySerializer(source='following', read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower_info', 'following_info', 'created_at']


# [6] 비밀번호 변경 시리얼라이저
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 일치하지 않습니다.")
        return value