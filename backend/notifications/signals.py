from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from articles.models import Like, Comment
from accounts.models import Follow
from .models import Notification

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.article.author
        # 1. 본인 글 제외 & 2. 수신자가 알림 켜야 함
        if recipient != instance.user and recipient.noti_likes:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.user,
                notification_type='like',
                article=instance.article
            )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.article.author
        # 1. 본인 글 제외 & 2. 수신자가 알림 켜야 함
        if recipient != instance.author and recipient.noti_comments:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.author,
                notification_type='comment',
                article=instance.article
            )

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.following
        # 수신자가 팔로우 알림 켜야 함
        if recipient.noti_follows:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.follower,
                notification_type='follow'
            )
