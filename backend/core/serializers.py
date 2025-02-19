from rest_framework import serializers
from .models import CustomUser,Report,Notifications
import urllib.parse

class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "profile_picture", "bio", "is_online"]

    def get_profile_picture(self, obj):
        request = self.context.get("request")
        profile_picture_url = obj.profile_picture.url if obj.profile_picture else ""

       

        return profile_picture_url

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["profile_picture"]



class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["reporter"]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'user', 'message', 'is_read', 'timestamp']
        read_only_fields = ['created_at']
