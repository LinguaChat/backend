from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

User = get_user_model()


class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            cache_key = f'last-seen-{request.user.id}'
            last_seen = cache.get(cache_key)

            if not last_seen:
                User.objects.filter(id=request.user.id).update(
                    last_activity=timezone.now()
                )
                cache.set(cache_key, timezone.now(), 300)

            request.user.refresh_from_db()
            request.user.is_user_online()

        return response
