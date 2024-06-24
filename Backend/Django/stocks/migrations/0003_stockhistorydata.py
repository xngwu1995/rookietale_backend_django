# Generated by Django 4.1.7 on 2024-06-23 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0002_alter_stock_company_alter_stock_industry_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockHistoryData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open_val', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close_val', models.FloatField()),
                ('adj_close_val', models.FloatField()),
                ('volume', models.BigIntegerField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
        ),
    ]
