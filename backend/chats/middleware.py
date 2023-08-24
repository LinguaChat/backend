from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import AccessToken, TokenError

User = get_user_model()


@database_sync_to_async
def get_user_by_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class WebSocketJWTAuthMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name == 'Token':
                scope['user'] = await get_user_by_token(token_key)
            else:
                try:
                    access_token = AccessToken(token_key)
                    scope["user"] = await get_user_by_id(access_token["user_id"])
                except TokenError:
                    scope["user"] = AnonymousUser()
        scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)
