# Generated migration to add fields to PrayerMessage
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ("prayer", "0008_add_submitted_by"),
    ]

    operations = [
        migrations.AddField(
            model_name='prayermessage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='prayermessage',
            name='is_important',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='prayermessage',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='prayermessage',
            name='answer_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prayermessage',
            name='answered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
