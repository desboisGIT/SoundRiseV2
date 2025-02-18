# middleware.py




from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware





@database_sync_to_async
def get_user_from_jwt(token):
    from jwt import decode as jwt_decode
    from django.contrib.auth.models import AnonymousUser
    from core.models import CustomUser
    from rest_framework_simplejwt.tokens import UntypedToken
    from rest_framework_simplejwt.exceptions import InvalidToken
    try:
        UntypedToken(token)  # Valider le token
        decoded_data = jwt_decode(token, options={"verify_signature": False})
        user = CustomUser.objects.get(id=decoded_data["user_id"])
        return user
    except (InvalidToken, CustomUser.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        from urllib.parse import parse_qs
        query_string = scope.get("query_string", b"").decode("utf-8")
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        if token:
            scope["user"] = await get_user_from_jwt(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
