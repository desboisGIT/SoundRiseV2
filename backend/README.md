SoundRise API - Authentication Guide

Login - http://127.0.0.1:8000/api/auth/login/  
 body - {
"email": ".....",
"password": "...."
}

    error - {
                "detail": "No active account found with the given credentials"
            }

    reussite - {
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczOTc5NzY4NywiaWF0IjoxNzM5MTkyODg3LCJqdGkiOiIwYjg2MDE0MTJjYTM0MzgzYjgzMjM2MTQ3NWFlMGQ3YSIsInVzZXJfaWQiOjN9.vT5E4iSrgDFttGnNgoJmG6-888QDn6E5dUZd1A2Sq9o",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MTk0Njg3LCJpYXQiOjE3MzkxOTI4ODcsImp0aSI6IjE1MTAyN2Y2ZGNlODRjZDNiMTEzZTlhNjY3N2JlOThlIiwidXNlcl9pZCI6M30.LRp9aH8P8Xtd5FDb0d11eYscj3O9uIFO4UejpG9LP0s"
                }

register - http://127.0.0.1:8000/api/auth/register/
body - {
"username": "...",
"email": "...",
"password": "..."
}

         erreur - {
                "email": [
                    "custom user with this email already exists."
                ],
                "username": [
                    "custom user with this username already exists."
                ]
            }

            {
            "password": [
                "Ensure this field has at least 8 characters."
            ]
            }
            {
            "password": [
                "Le mot de passe doit contenir au moins un chiffre."
            ]
            }
            {
            "password": [
                "Le mot de passe doit contenir au moins une majuscule."
            ]
            }
    Réussite - {
                    "message": "Inscription réussie. Vérifiez votre email pour activer votre compte."
                }

profile - http://127.0.0.1:8000/api/user

        réussite - {
                    "id": 9,
                    "username": "dev",
                    "email": "dev@gmail.com",
                    "profile_picture": null,
                    "bio": null
                }
