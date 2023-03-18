# Generated by Django 4.1.7 on 2023-03-18 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512)),
                ('venue', models.CharField(blank=True, max_length=512, null=True)),
                ('year', models.CharField(blank=True, max_length=512, null=True)),
                ('num_citations', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('photo_url', models.CharField(blank=True, max_length=512, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('position', models.CharField(blank=True, max_length=512, null=True)),
                ('research_interest', models.CharField(blank=True, max_length=512, null=True)),
                ('email', models.CharField(blank=True, max_length=512, null=True)),
                ('phone', models.CharField(blank=True, max_length=512, null=True)),
                ('photo_url', models.CharField(blank=True, max_length=512, null=True)),
                ('university', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='academicworld.university')),
            ],
        ),
        migrations.CreateModel(
            name='PublicationKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(blank=True, null=True)),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicworld.keyword')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicworld.publication')),
            ],
            options={
                'unique_together': {('publication', 'keyword')},
            },
        ),
        migrations.CreateModel(
            name='FacultyPublication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicworld.faculty')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicworld.publication')),
            ],
            options={
                'unique_together': {('faculty', 'publication')},
            },
        ),
        migrations.CreateModel(
            name='FacultyKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(blank=True, null=True)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicworld.faculty')),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicworld.keyword')),
            ],
            options={
                'unique_together': {('faculty', 'keyword')},
            },
        ),
    ]
