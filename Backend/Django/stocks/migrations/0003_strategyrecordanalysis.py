# Generated by Django 4.1.7 on 2024-08-19 01:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_alter_stock_company_alter_stock_industry_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StrategyRecordAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('gpt_analysis', models.TextField()),
                ('strategy_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.strategydata')),
            ],
        ),
    ]
