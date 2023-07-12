"""Основной файл с маршрутами проекта."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from chats.urls import chat_router
from users.urls import user_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(chat_router.urls)),
    path('api/v1/', include(user_router.urls)),
    path('api/v1/', include('users.urls')),
    # Конфигурация DRF_Spectacular для просмотра документации
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/docs/',
         SpectacularSwaggerView.as_view(url_name='schema'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
