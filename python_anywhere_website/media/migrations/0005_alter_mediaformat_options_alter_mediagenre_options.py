# Generated by Django 4.0.6 on 2022-09-17 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("media", "0004_alter_media_subtitle"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mediaformat",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="mediagenre",
            options={"ordering": ["name"]},
        ),
    ]
