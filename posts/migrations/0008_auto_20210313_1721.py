# Generated by Django 2.2.6 on 2021-03-13 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_newpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newpost',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Group'),
        ),
    ]
