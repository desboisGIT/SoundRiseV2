# Generated by Django 5.1.6 on 2025-02-17 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0003_invitation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitation',
            name='conversation',
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='is_accepted',
        ),
        migrations.AddField(
            model_name='invitation',
            name='message',
            field=models.TextField(default='message'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invitation',
            name='status',
            field=models.CharField(default='pending', max_length=20),
        ),
        migrations.DeleteModel(
            name='ConversationRequest',
        ),
    ]
