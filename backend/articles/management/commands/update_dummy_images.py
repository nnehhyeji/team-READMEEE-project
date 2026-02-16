import os
import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from articles.models import Article
from supabase import create_client, Client

User = get_user_model()

class Command(BaseCommand):
    help = 'Bulk upload images from a folder to existing articles for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, required=True, help='Username to target')
        parser.add_argument('--folder', type=str, required=True, help='Local folder path containing images')
        parser.add_argument('--clean', action='store_true', help='Update all articles (overwrite existing images)')

    def handle(self, *args, **options):
        username = options['user']
        folder_path = options['folder']
        clean = options['clean']

        # 0. Load Env
        from dotenv import load_dotenv
        load_dotenv()

        # 1. Supabase Init
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            self.stdout.write(self.style.ERROR('❌ Error: SUPABASE_URL or SUPABASE_KEY is missing'))
            return
        
        try:
            supabase: Client = create_client(url, key)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Connection Failed: {e}'))
            return

        # 2. Get User & Articles
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User not found: {username}'))
            return

        articles = Article.objects.filter(author=user)
        if not clean:
             # Only update articles that don't have an image
             from django.db.models import Q
             articles = articles.filter(Q(image__isnull=True) | Q(image=''))
        
        if not articles.exists():
             self.stdout.write(self.style.SUCCESS(f'✨ No articles to update for {username} (Use --clean to overwrite)'))
             return

        # 3. Get Images
        if not os.path.isdir(folder_path):
             self.stdout.write(self.style.ERROR(f'❌ Folder not found: {folder_path}'))
             return
             
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
        if not image_files:
             self.stdout.write(self.style.ERROR(f'❌ No images found in {folder_path}'))
             return
        
        self.stdout.write(f"🔍 Found {len(image_files)} images for {articles.count()} articles.")

        # 4. Process
        updated_count = 0
        articles = list(articles)
        
        # 💡 Randomize images to satisfy "Randomly put photos"
        random.shuffle(image_files)
        
        bucket_name = 'ReadMe-images'
        
        # 💡 Use zip to ensure 1-to-1 mapping (No duplicates)
        # If articles > images, some articles won't get an image.
        # If images > articles, some images won't be used.
        pairs = list(zip(articles, image_files))
        
        self.stdout.write(f"🔍 Matching {len(pairs)} images to articles (preventing duplicates)...")

        for article, image_name in pairs:
            local_path = os.path.join(folder_path, image_name)

            
            self.stdout.write(f"🚀 Uploading {image_name} for Article {article.id}...")
            
            try:
                with open(local_path, 'rb') as f:
                    ext = os.path.splitext(image_name)[1]
                    # Generate unique name to avoid collision
                    safe_name = f"{uuid.uuid4()}{ext}"
                    storage_path = f"bulk_uploads/{user.id}/{safe_name}"
                    
                    # Upload
                    supabase.storage.from_(bucket_name).upload(storage_path, f)
                    
                    # Get Public URL
                    public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
                    
                    # Save
                    article.image = public_url
                    article.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Updated: {public_url}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Failed: {e}"))

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Completed! Updated {updated_count} articles for {username}.'))
