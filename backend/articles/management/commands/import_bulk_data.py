import json
import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from articles.models import Article
from questions.models import Question

User = get_user_model()

class Command(BaseCommand):
    help = 'Bulk import users and articles from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file to import')

    def handle(self, *args, **options):
        json_file_path = options['json_file']

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON format in: {json_file_path}'))
            return

        for user_data in data:
            self.process_user(user_data)

    def process_user(self, user_data):
        username = user_data.get('username')
        email = user_data.get('email', '')
        password = user_data.get('password', '1234') # Default password
        bio = user_data.get('bio', '')

        if not username:
            self.stdout.write(self.style.WARNING('Skipping user without username'))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'bio': bio
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing user: {username}'))

        articles_data = user_data.get('articles', [])
        for article_data in articles_data:
            self.process_article(user, article_data)

    def process_article(self, user, article_data):
        question_id = article_data.get('question_id')
        content = article_data.get('content')
        
        if not question_id or not content:
            self.stdout.write(self.style.WARNING(f'Skipping article for {user.username}: missing question_id or content'))
            return

        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Question not found: ID {question_id}'))
            return

        # 1. Emotion (Random if missing)
        emotion = article_data.get('emotion')
        if not emotion:
            emotion = random.choice([choice[0] for choice in Article.EMOTION_CHOICES])

        # 2. Date (Automatic based on release_date if missing)
        date_str = article_data.get('date')
        
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.WARNING(f'Invalid date format {date_str}, using release date instead'))
                target_date = question.release_date
        else:
            # Use question's release date
            # Ensure release_date is a date object (it might be a string depending on how it's fetched, but in Django model it's DateField)
            if isinstance(question.release_date, str):
                 target_date = datetime.strptime(question.release_date, '%Y-%m-%d').date()
            else:
                target_date = question.release_date

        # Set random time between 20:00 and 23:59
        random_hour = random.randint(20, 23)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        
        created_at_naive = datetime.combine(target_date, time(random_hour, random_minute, random_second))
        created_at = timezone.make_aware(created_at_naive)
        expires_at = created_at + timedelta(days=1)

        # 3. Music Logic (Based on Question Recommendation)
        # If the question has a recommendation, 50% chance to include it.
        music_title = None
        music_artist = None

        if question.rec_title and question.rec_artist:
            # 60% chance to "toggle on" the recommendation
            if random.random() < 0.6:
                music_title = question.rec_title
                music_artist = question.rec_artist

        # 4. Create or Update Article
        article, created = Article.objects.update_or_create(
            author=user,
            question=question,
            defaults={
                'content': content,
                'emotion': emotion,
                'is_public': article_data.get('is_public', True),
                'created_at': created_at,
                'expires_at': expires_at,
                'music_title': music_title,
                'music_artist': music_artist,
            }
        )
        
        action = "Created" if created else "Updated"
        music_info = f", {music_title}" if music_title else ""
        self.stdout.write(self.style.SUCCESS(f'{action} article: {user.username} - Q{question_id} ({emotion}{music_info})'))
