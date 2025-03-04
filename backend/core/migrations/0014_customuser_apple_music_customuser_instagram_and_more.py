# Generated by Django 5.1.6 on 2025-03-02 16:47

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_notifications_draft_beat_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='apple_music',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_apple_music]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='instagram',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_instagram]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='soundcloud',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_soundcloud]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='spotify',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_spotify]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tiktok',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_tiktok]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='twitter',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_twitter]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='website',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_website]),
        ),
        migrations.AddField(
            model_name='customuser',
            name='youtube',
            field=models.URLField(blank=True, null=True, validators=[core.validators.validate_youtube]),
        ),
    ]
