# Generated by Django 5.0.4 on 2024-04-30 09:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_gammauser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='birthday',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_student',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='profilepic',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='website',
        ),
        migrations.CreateModel(
            name='BetaUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profilepic', models.ImageField(null=True, upload_to='static/profile_pics')),
                ('website', models.URLField(default='')),
                ('phone', models.CharField(default='', max_length=10)),
                ('birthday', models.CharField(max_length=20, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
