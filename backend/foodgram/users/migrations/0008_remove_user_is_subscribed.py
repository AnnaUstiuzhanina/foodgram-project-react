# Generated by Django 3.0.5 on 2021-08-21 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_is_subscribed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_subscribed',
        ),
    ]