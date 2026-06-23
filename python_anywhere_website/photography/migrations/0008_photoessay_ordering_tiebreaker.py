# Generated migration to make photo essay ordering deterministic.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("photography", "0007_gallery_models"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="photoessay",
            options={
                "ordering": ["-created_at", "-id"],
                "verbose_name_plural": "Photo Essays",
            },
        ),
    ]
