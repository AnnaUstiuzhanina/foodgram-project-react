# Generated by Django 3.0.5 on 2021-08-19 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20210819_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipefavourite',
            name='is_favorited',
        ),
    ]
