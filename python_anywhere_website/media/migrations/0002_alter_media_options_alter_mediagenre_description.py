# Generated by Django 4.0.6 on 2022-08-08 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='media',
            options={'verbose_name_plural': 'media'},
        ),
        migrations.AlterField(
            model_name='mediagenre',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
