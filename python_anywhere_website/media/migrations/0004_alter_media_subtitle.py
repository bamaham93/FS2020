# Generated by Django 4.0.6 on 2022-08-08 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_media_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='subtitle',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]