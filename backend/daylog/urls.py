"""
URL configuration for daylog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/questions/', include('questions.urls')),

    # ⭐ [추가됨] articles 앱 연결
    # 주의: articles/urls.py의 라우터가 이미 'articles/' 접두사를 붙이므로
    # 여기서는 'api/'까지만 적어줍니다.
    path('api/', include('articles.urls')), 
    path('api/notifications/', include('notifications.urls')),
 
]

# Media 파일 서빙 (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
