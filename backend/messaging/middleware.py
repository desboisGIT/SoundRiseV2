from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async




class JWTAuthMiddleware(BaseMiddleware):
    
    """ Middleware d'authentification JWT pour WebSocket """

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        token = self.get_token_from_scope(scope)

        if token:
            print(f"✅ Token JWT reçu : {token}")  # Debugging
            user = await self.get_user_from_token(token)
            if user:
                print(f"✅ Utilisateur authentifié : {user.username}")
                scope["user"] = user
            else:
                print("❌ Token invalide ou utilisateur introuvable.")
                scope["user"] = AnonymousUser()
        else:
            print("❌ Aucun token trouvé dans l'URL ou les headers.")
            scope["user"] = AnonymousUser()

        try:
            return await super().__call__(scope, receive, send)
        except Exception as e:
            print(f"❌ Erreur lors de la connexion WebSocket : {e}")
            raise e  # Vous pouvez également renvoyer une erreur spécifique

    def get_token_from_scope(self, scope):
        """ Récupère le token JWT depuis l'URL ou les headers WebSocket """
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]  # ✅ Récupération via URL

        if not token:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b'authorization', b'').decode('utf-8')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]  # ✅ Récupération via Headers

        return token

    @database_sync_to_async
    def get_user_from_token(self, token):
        from core.models import CustomUser
        from rest_framework_simplejwt.tokens import AccessToken
        """ Récupère l'utilisateur à partir du token JWT """
        try:
            access_token = AccessToken(token)
            user = CustomUser.objects.get(id=access_token["user_id"])
            return user
        except CustomUser.DoesNotExist:
            print("❌ Utilisateur non trouvé avec ce token.")
        except Exception as e:
            print(f"❌ Erreur lors de l'authentification : {e}")
        return None
