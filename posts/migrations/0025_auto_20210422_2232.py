# Generated by Django 2.2.6 on 2021-04-22 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0024_auto_20210421_1847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follow',
            name='author',
        ),
        migrations.AddField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_follow', to='posts.Post', verbose_name='Автор на которого подписываются'),
        ),
        migrations.RemoveField(
            model_name='follow',
            name='user',
        ),
        migrations.AddField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписывающийся'),
        ),
    ]