from django.db import models
import zipfile
from django.db import models
from django.core.files.storage import default_storage
from core.models import CustomUser

# Create your models here.
class Sample(models.Model):
    """Un sample audio utilisé pour une démonstration."""
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="samples/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Soundkit(models.Model):
    """Un pack de samples compressé en fichier ZIP."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    zip_file = models.FileField(upload_to="soundkits/")
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="soundkits")
    created_at = models.DateTimeField(auto_now_add=True)

    def extract_file_list(self):
        """Liste tous les fichiers présents dans le ZIP (sans extraction)."""
        file_list = []
        if self.zip_file and default_storage.exists(self.zip_file.name):
            zip_path = default_storage.open(self.zip_file.name, "rb")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                file_list = [f for f in zf.namelist() if not f.endswith('/')]  # Exclure les dossiers
        return file_list

    def __str__(self):
        return self.title