from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from chats.views import ChatViewSet

router = routers.DefaultRouter()

router.register('chats', ChatViewSet, basename='chats')

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)