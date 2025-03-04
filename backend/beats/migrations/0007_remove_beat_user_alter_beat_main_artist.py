# Generated by Django 5.1.6 on 2025-02-12 10:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beats', '0006_beat_audio_file_alter_beattrack_file_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beat',
            name='user',
        ),
        migrations.AlterField(
            model_name='beat',
            name='main_artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='beats', to=settings.AUTH_USER_MODEL),
        ),
    ]
