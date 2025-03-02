import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_instagram(value):
    pattern = r"^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_.-]+\/?.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour Instagram n'est pas valide."))

def validate_twitter(value):
    pattern = r"^https?:\/\/(www\.)?twitter\.com\/[a-zA-Z0-9_]+\/?.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour Twitter n'est pas valide."))

def validate_youtube(value):
    pattern = r"^https?:\/\/(www\.)?(youtube\.com\/(channel|c|user|@)|youtu\.be\/)[a-zA-Z0-9_\-]+\/?.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour YouTube n'est pas valide."))

def validate_tiktok(value):
    pattern = r"^https?:\/\/(www\.)?tiktok\.com\/(@[a-zA-Z0-9_.-]+)\/?.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour TikTok n'est pas valide."))

def validate_soundcloud(value):
    pattern = r"^https?:\/\/(www\.)?soundcloud\.com\/[a-zA-Z0-9_-]+\/?.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour SoundCloud n'est pas valide."))

def validate_spotify(value):
    pattern = r"^https?:\/\/(open\.spotify\.com\/(artist|album|track)\/[a-zA-Z0-9]+).*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour Spotify n'est pas valide."))

def validate_apple_music(value):
    pattern = r"^https?:\/\/music\.apple\.com\/[a-zA-Z0-9/_-]+\/?.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour Apple Music n'est pas valide."))

def validate_website(value):
    pattern = r"^https?:\/\/(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}.*$"
    if not re.fullmatch(pattern, value):
        raise ValidationError(_("L'URL fournie pour le site web n'est pas valide."))
