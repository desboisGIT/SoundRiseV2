from rest_framework import serializers
from core.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')

    def validate_email(self, value):
        """ Vérifie si l'email est déjà utilisé """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_username(self, value):
        """ Vérifie si le username est déjà pris """
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value

    def validate_password(self, value):
        """ Vérifie la complexité du mot de passe """
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


def generate_verification_token(user):
    """ Génère un token JWT pour la vérification d'email """
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)
