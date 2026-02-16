
import os
import django
import requests
from pathlib import Path
from supabase import create_client, Client

# 1. Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daylog.settings')
django.setup()

from django.conf import settings
from accounts.models import User
from articles.models import Article

def download_file(url, local_path):
    """URL에서 파일을 다운로드하여 로컬에 저장합니다."""
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"❌ 다운로드 실패 ({response.status_code}): {url}")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    return False

def migrate_media():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ .env에 SUPABASE_URL 또는 SUPABASE_KEY가 없습니다.")
        return

    supabase: Client = create_client(url, key)
    bucket_name = "ReadMe-images"
    
    print("🚀 미디어 마이그레이션 시작 (Supabase -> Local Media)")

    # [1] 프로필 이미지 마이그레이션 (User 모델)
    print("\n--- [1/2] 프로필 이미지 처리 중 ---")
    for user in User.objects.exclude(profile_image='').exclude(profile_image=None):
        img_path = str(user.profile_image)
        
        # 이미 로컬 경로인 경우 스킵
        if not img_path.startswith('http') and not '/' in img_path:
             continue
        
        # Supabase 경로 추출
        storage_path = img_path
        if 'ReadMe-images/' in img_path:
            storage_path = img_path.split('ReadMe-images/')[-1]
        
        # Public URL 생성
        public_url = f"{url}/storage/v1/object/public/{bucket_name}/{storage_path}"
        
        local_rel_path = f"profiles/{os.path.basename(storage_path)}"
        local_full_path = os.path.join(settings.MEDIA_ROOT, local_rel_path)
        
        print(f"🔄 {user.username}: {storage_path} -> {local_rel_path}")
        if download_file(public_url, local_full_path):
            user.profile_image = local_rel_path
            user.save()
            print("   ✅ 완료")

    # [2] 게시글 이미지 마이그레이션 (Article 모델)
    print("\n--- [2/2] 게시글 이미지 처리 중 ---")
    for article in Article.objects.exclude(image='').exclude(image=None):
        img_path = str(article.image)
        
        # 이미 로컬 경로거나 http가 아니면 스킵
        if not img_path.startswith('http') and 'ReadMe-images' not in img_path:
            continue
            
        # Supabase 경로 추출
        storage_path = img_path
        if 'ReadMe-images/' in img_path:
            storage_path = img_path.split('ReadMe-images/')[-1]
        
        public_url = f"{url}/storage/v1/object/public/{bucket_name}/{storage_path}"
        
        # 로컬 저장 경로 설정 (articles/폴더 아래)
        local_rel_path = f"articles/{os.path.basename(storage_path)}"
        local_full_path = os.path.join(settings.MEDIA_ROOT, local_rel_path)
        
        print(f"🔄 Article {article.id}: {storage_path} -> {local_rel_path}")
        if download_file(public_url, local_full_path):
            article.image = local_rel_path
            article.save()
            print("   ✅ 완료")

    print("\n✨ 모든 미디어 마이그레이션이 완료되었습니다!")
    print(f"📍 파일 저장 위치: {settings.MEDIA_ROOT}")

if __name__ == "__main__":
    migrate_media()
