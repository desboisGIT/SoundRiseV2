# Generated by Django 5.1.6 on 2025-02-14 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beats', '0017_draftbeat_audio_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='license',
            name='license_file',
        ),
        migrations.AddField(
            model_name='license',
            name='license_file_type',
            field=models.CharField(blank=True, choices=[('mp3', 'MP3'), ('wav', 'WAV'), ('flac', 'FLAC'), ('stems', 'STEMS'), ('zip', 'ZIP')], max_length=10, null=True),
        ),
    ]
