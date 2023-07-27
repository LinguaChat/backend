from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from users.models import User


class UpdateLastActivityMiddleware(MiddlewareMixin):
    def __call__(self, request):
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            user.last_activity = timezone.now()
            user.save()
        response = self.get_response(request)
        return response
