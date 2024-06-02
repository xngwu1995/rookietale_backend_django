# Generated by Django 4.1.7 on 2024-06-02 18:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=80, unique=True)),
                ('instructors', models.TextField()),
                ('analysis', models.TextField()),
                ('rank', models.CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell'), ('HOLD', 'Hold')], max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='LMT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LMT.stock')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
