# Generated by Django 4.1.7 on 2024-11-20 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_strategyoptiondata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategyoptiondata',
            name='criteria',
            field=models.JSONField(),
        ),
    ]
