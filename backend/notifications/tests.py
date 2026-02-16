from django.test import TestCase
from django.contrib.auth import get_user_model
from articles.models import Article, Like, Comment
from questions.models import Question

from notifications.models import Notification
from accounts.models import Follow
from django.utils import timezone

User = get_user_model()

class NotificationSignalTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='user_a', email='a@example.com', password='password')
        self.user_b = User.objects.create_user(username='user_b', email='b@example.com', password='password')
        
        self.question = Question.objects.create(content="Q1", category='daily', release_date=timezone.now().date())
        self.article = Article.objects.create(author=self.user_a, question=self.question, content="My Answer", emotion='happy')

    def test_like_notification(self):
        # User B likes User A's article
        Like.objects.create(user=self.user_b, article=self.article)
        
        # Check Notification
        self.assertTrue(Notification.objects.filter(recipient=self.user_a, sender=self.user_b, notification_type='like').exists())

    def test_comment_notification(self):
        # User B comments on User A's article
        Comment.objects.create(author=self.user_b, article=self.article, content="Nice!")
        
        # Check Notification
        self.assertTrue(Notification.objects.filter(recipient=self.user_a, sender=self.user_b, notification_type='comment').exists())

    def test_follow_notification(self):
        # User B follows User A
        # User B follows User A
        # Create Follow object directly

        # existing code: Follow(follower=user_b, following=user_a).save()
        Follow.objects.create(follower=self.user_b, following=self.user_a)

        # Check Notification
        self.assertTrue(Notification.objects.filter(recipient=self.user_a, sender=self.user_b, notification_type='follow').exists())
