# Generated by Django 4.1.7 on 2024-07-31 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='company',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='stock',
            name='industry',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='stock',
            name='sector',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='TradeRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.DecimalField(decimal_places=5, max_digits=10)),
                ('quantity', models.DecimalField(decimal_places=5, max_digits=10)),
                ('strategy', models.CharField(max_length=50)),
                ('reason', models.CharField(max_length=50)),
                ('created_date', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('sell_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('sell_price', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True)),
                ('sell_date', models.DateField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='StrategyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('strategy', models.CharField(choices=[('VCP', 'VCP')], default='VCP', max_length=3)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='AIAnalysisData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openai', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
        ),
        migrations.AddIndex(
            model_name='traderecord',
            index=models.Index(fields=['stock'], name='stocks_trad_stock_i_2f2c88_idx'),
        ),
        migrations.AddIndex(
            model_name='traderecord',
            index=models.Index(fields=['user'], name='stocks_trad_user_id_be762e_idx'),
        ),
    ]