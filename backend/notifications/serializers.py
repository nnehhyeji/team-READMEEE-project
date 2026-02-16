from rest_framework import serializers
from .models import Notification
from accounts.models import User

class NotificationSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image']

class NotificationSerializer(serializers.ModelSerializer):
    sender = NotificationSenderSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'notification_type', 'article', 'is_read', 'created_at']
