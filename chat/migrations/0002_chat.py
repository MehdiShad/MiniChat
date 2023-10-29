# Generated by Django 4.2.6 on 2023-10-28 12:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(blank=True, max_length=75, null=True)),
                ('members', models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]