# Generated by Django 4.1.7 on 2024-01-20 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='expo_push_token',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
