# Generated by Django 5.0.4 on 2024-04-26 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_customuser_phone_customuser_website_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='birthday',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
