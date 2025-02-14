import websockets
import asyncio
import ssl

async def test():
    uri = "wss://127.0.0.1:8000/ws/chat_request/"  # Utilise wss:// pour une connexion sécurisée
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5NTQ1NjI3LCJpYXQiOjE3Mzk1NDM4MjcsImp0aSI6IjVmNzY2ODViZGU2NDRmNGFiZGRiY2UxNTRlNTVkZWI4IiwidXNlcl9pZCI6OX0.dhInLgDWgxcv0K7n8bHhPthpIqYte_POaXJlDI9sEEE"  # Remplace "your_token_here" par ton token réel

    # Définir les en-têtes HTTP
    headers = {
        "Authorization": f"Bearer {token}",  # Ajouter le token dans l'en-tête Authorization
    }

    # Créer un contexte SSL
    ssl_context = ssl.create_default_context()

    # Créer une connexion WebSocket avec SSL et les en-têtes personnalisés
    async with websockets.connect(uri, headers=headers, ssl=ssl_context) as websocket:
        await websocket.send("Hello Server")  # Envoie un message au serveur
        response = await websocket.recv()     # Attends la réponse du serveur
        print(response)  # Affiche la réponse

# Exécuter la fonction de test
asyncio.run(test())
