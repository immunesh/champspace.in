# Generated by Django 5.1.2 on 2025-01-05 10:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('champapp', '0055_studentprofile_favorites_alter_profile_favorites'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='favorites',
            field=models.ManyToManyField(blank=True, related_name='studentprofile_favorites', to='champapp.course'),
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('option_1', models.CharField(max_length=255)),
                ('option_2', models.CharField(max_length=255)),
                ('option_3', models.CharField(max_length=255)),
                ('option_4', models.CharField(max_length=255)),
                ('correct_option', models.CharField(choices=[('A', 'Option 1'), ('B', 'Option 2'), ('C', 'Option 3'), ('D', 'Option 4')], max_length=1)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
