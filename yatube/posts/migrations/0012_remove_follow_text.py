# Generated by Django 2.2.16 on 2023-01-19 22:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_follow_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follow',
            name='text',
        ),
    ]
