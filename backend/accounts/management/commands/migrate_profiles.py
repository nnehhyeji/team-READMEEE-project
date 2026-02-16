import os
import uuid
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from supabase import create_client, Client

User = get_user_model()

class Command(BaseCommand):
    help = 'Migrate local profile images to Supabase Storage'

    def handle(self, *args, **options):
        # 1. 환경변수 확인
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            self.stdout.write(self.style.ERROR('❌ Error: SUPABASE_URL or SUPABASE_KEY is missing'))
            return

        # 2. 클라이언트 연결
        try:
            supabase: Client = create_client(url, key)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Connection Failed: {e}'))
            return

        bucket_name = 'ReadMe-images'
        
        # 3. 로컬 프로필 이미지가 있는 유저 찾기
        users = User.objects.exclude(profile_image__isnull=True).exclude(profile_image='')
        
        migrated_count = 0
        self.stdout.write(f"🔍 Scanning users...")
        
        for user in users:
            if str(user.profile_image).startswith('http'):
                continue
            
            # 로컬 경로 (settings.MEDIA_ROOT + profile_image path)
            local_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_image))
            
            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f'⚠️ File not found (User: {user.username}): {local_path}'))
                continue
                
            self.stdout.write(f"🚀 Uploading (User: {user.username})...")
            
            try:
                with open(local_path, 'rb') as f:
                    file_name = os.path.basename(local_path)
                    
                    # [Fix] 한글/특수문자 방지 -> UUID 사용
                    ext = os.path.splitext(file_name)[1]
                    safe_name = f"{uuid.uuid4()}{ext}"
                    
                    # profiles 폴더에 저장
                    storage_path = f"profiles/migrated/{safe_name}" 
                    
                    supabase.storage.from_(bucket_name).upload(storage_path, f)
                    
                    # Public URL
                    public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
                    
                    user.profile_image = public_url
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ Done: {public_url}'))
                    migrated_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed (User: {user.username}): {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Profile Migration Completed! Total {migrated_count} profiles moved.'))
