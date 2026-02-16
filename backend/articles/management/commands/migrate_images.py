import os
from django.core.management.base import BaseCommand
from django.conf import settings
from articles.models import Article
from supabase import create_client, Client

class Command(BaseCommand):
    help = 'Migrate local images to Supabase Storage'

    def handle(self, *args, **options):
        # 1. 환경변수에서 키 가져오기
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            self.stdout.write(self.style.ERROR('❌ Error: SUPABASE_URL or SUPABASE_KEY is missing in .env'))
            self.stdout.write(self.style.WARNING('👉 Please add them to backend/.env'))
            return

        # 2. Supabase 클라이언트 연결
        try:
            supabase: Client = create_client(url, key)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Connection Failed: {e}'))
            return

        bucket_name = 'ReadMe-images'
        
        # 3. 로컬 이미지가 있는 게시글 찾기 (http로 시작하지 않는 것들)
        articles = Article.objects.exclude(image__isnull=True).exclude(image='')
        
        migrated_count = 0
        
        self.stdout.write(f"🔍 Scanning articles...")
        
        for article in articles:
            # 이미 마이그레이션 된(URL 형태) 이미지는 패스
            if str(article.image).startswith('http'):
                continue
            
            # 로컬 파일 경로 찾기
            # DB에는 'articles/2024/...' 형태로 저장되어 있음
            local_path = os.path.join(settings.MEDIA_ROOT, str(article.image))
            
            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f'⚠️ File not found (ID: {article.id}): {local_path}'))
                # 파일이 없으면 그냥 둡니다 (삭제하면 데이터 유실 위험)
                continue
                
            self.stdout.write(f"🚀 Uploading (ID: {article.id}): {article.image}...")
            
            # 4. 파일 업로드
            try:
                with open(local_path, 'rb') as f:
                    file_name = os.path.basename(local_path)
                    
                    # [Fix] 한글 파일명 호환성 문제 해결
                    # 안전하게 UUID로 변경하거나 인코딩해야 함. 여기선 UUID 사용 추천
                    import uuid
                    ext = os.path.splitext(file_name)[1]
                    safe_name = f"{uuid.uuid4()}{ext}"
                    
                    # 겹침 방지를 위해 폴더 구분
                    storage_path = f"migrated/{safe_name}" 
                    
                    # 업로드
                    supabase.storage.from_(bucket_name).upload(storage_path, f)
                    
                    # Public URL 가져오기
                    public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
                    
                    # 5. DB 업데이트
                    article.image = public_url
                    article.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ Done: {public_url}'))
                    migrated_count += 1
                    
            except Exception as e:
                # 이미 존재하는 파일일 수 있음 -> URL만 업데이트 시도하거나 에러 출력
                if 'Duplicate' in str(e) or 'already exists' in str(e):
                     storage_path = f"migrated/{os.path.basename(local_path)}"
                     public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
                     article.image = public_url
                     article.save()
                     self.stdout.write(self.style.SUCCESS(f'✅ Updated URL (File existed): {public_url}'))
                     migrated_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Failed (ID: {article.id}): {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Migration Completed! Total {migrated_count} images moved.'))
