from django.db import migrations


def seed_kjv_books(apps, schema_editor):
    BibleBook = apps.get_model("bible", "BibleBook")

    for book in [
        {"name": "Genesis", "slug": "genesis", "order": 1, "testament": "OT", "chapters": 50},
        {"name": "Exodus", "slug": "exodus", "order": 2, "testament": "OT", "chapters": 40},
        {"name": "Leviticus", "slug": "leviticus", "order": 3, "testament": "OT", "chapters": 27},
        {"name": "Numbers", "slug": "numbers", "order": 4, "testament": "OT", "chapters": 36},
        {"name": "Deuteronomy", "slug": "deuteronomy", "order": 5, "testament": "OT", "chapters": 34},
        {"name": "Joshua", "slug": "joshua", "order": 6, "testament": "OT", "chapters": 24},
        {"name": "Judges", "slug": "judges", "order": 7, "testament": "OT", "chapters": 21},
        {"name": "Ruth", "slug": "ruth", "order": 8, "testament": "OT", "chapters": 4},
        {"name": "1 Samuel", "slug": "1-samuel", "order": 9, "testament": "OT", "chapters": 31},
        {"name": "2 Samuel", "slug": "2-samuel", "order": 10, "testament": "OT", "chapters": 24},
        {"name": "1 Kings", "slug": "1-kings", "order": 11, "testament": "OT", "chapters": 22},
        {"name": "2 Kings", "slug": "2-kings", "order": 12, "testament": "OT", "chapters": 25},
        {"name": "1 Chronicles", "slug": "1-chronicles", "order": 13, "testament": "OT", "chapters": 29},
        {"name": "2 Chronicles", "slug": "2-chronicles", "order": 14, "testament": "OT", "chapters": 36},
        {"name": "Ezra", "slug": "ezra", "order": 15, "testament": "OT", "chapters": 10},
        {"name": "Nehemiah", "slug": "nehemiah", "order": 16, "testament": "OT", "chapters": 13},
        {"name": "Esther", "slug": "esther", "order": 17, "testament": "OT", "chapters": 10},
        {"name": "Job", "slug": "job", "order": 18, "testament": "OT", "chapters": 42},
        {"name": "Psalms", "slug": "psalms", "order": 19, "testament": "OT", "chapters": 150},
        {"name": "Proverbs", "slug": "proverbs", "order": 20, "testament": "OT", "chapters": 31},
        {"name": "Ecclesiastes", "slug": "ecclesiastes", "order": 21, "testament": "OT", "chapters": 12},
        {"name": "Song of Solomon", "slug": "song-of-solomon", "order": 22, "testament": "OT", "chapters": 8},
        {"name": "Isaiah", "slug": "isaiah", "order": 23, "testament": "OT", "chapters": 66},
        {"name": "Jeremiah", "slug": "jeremiah", "order": 24, "testament": "OT", "chapters": 52},
        {"name": "Lamentations", "slug": "lamentations", "order": 25, "testament": "OT", "chapters": 5},
        {"name": "Ezekiel", "slug": "ezekiel", "order": 26, "testament": "OT", "chapters": 48},
        {"name": "Daniel", "slug": "daniel", "order": 27, "testament": "OT", "chapters": 12},
        {"name": "Hosea", "slug": "hosea", "order": 28, "testament": "OT", "chapters": 14},
        {"name": "Joel", "slug": "joel", "order": 29, "testament": "OT", "chapters": 3},
        {"name": "Amos", "slug": "amos", "order": 30, "testament": "OT", "chapters": 9},
        {"name": "Obadiah", "slug": "obadiah", "order": 31, "testament": "OT", "chapters": 1},
        {"name": "Jonah", "slug": "jonah", "order": 32, "testament": "OT", "chapters": 4},
        {"name": "Micah", "slug": "micah", "order": 33, "testament": "OT", "chapters": 7},
        {"name": "Nahum", "slug": "nahum", "order": 34, "testament": "OT", "chapters": 3},
        {"name": "Habakkuk", "slug": "habakkuk", "order": 35, "testament": "OT", "chapters": 3},
        {"name": "Zephaniah", "slug": "zephaniah", "order": 36, "testament": "OT", "chapters": 3},
        {"name": "Haggai", "slug": "haggai", "order": 37, "testament": "OT", "chapters": 2},
        {"name": "Zechariah", "slug": "zechariah", "order": 38, "testament": "OT", "chapters": 14},
        {"name": "Malachi", "slug": "malachi", "order": 39, "testament": "OT", "chapters": 4},
        {"name": "Matthew", "slug": "matthew", "order": 40, "testament": "NT", "chapters": 28},
        {"name": "Mark", "slug": "mark", "order": 41, "testament": "NT", "chapters": 16},
        {"name": "Luke", "slug": "luke", "order": 42, "testament": "NT", "chapters": 24},
        {"name": "John", "slug": "john", "order": 43, "testament": "NT", "chapters": 21},
        {"name": "Acts", "slug": "acts", "order": 44, "testament": "NT", "chapters": 28},
        {"name": "Romans", "slug": "romans", "order": 45, "testament": "NT", "chapters": 16},
        {"name": "1 Corinthians", "slug": "1-corinthians", "order": 46, "testament": "NT", "chapters": 16},
        {"name": "2 Corinthians", "slug": "2-corinthians", "order": 47, "testament": "NT", "chapters": 13},
        {"name": "Galatians", "slug": "galatians", "order": 48, "testament": "NT", "chapters": 6},
        {"name": "Ephesians", "slug": "ephesians", "order": 49, "testament": "NT", "chapters": 6},
        {"name": "Philippians", "slug": "philippians", "order": 50, "testament": "NT", "chapters": 4},
        {"name": "Colossians", "slug": "colossians", "order": 51, "testament": "NT", "chapters": 4},
        {"name": "1 Thessalonians", "slug": "1-thessalonians", "order": 52, "testament": "NT", "chapters": 5},
        {"name": "2 Thessalonians", "slug": "2-thessalonians", "order": 53, "testament": "NT", "chapters": 3},
        {"name": "1 Timothy", "slug": "1-timothy", "order": 54, "testament": "NT", "chapters": 6},
        {"name": "2 Timothy", "slug": "2-timothy", "order": 55, "testament": "NT", "chapters": 4},
        {"name": "Titus", "slug": "titus", "order": 56, "testament": "NT", "chapters": 3},
        {"name": "Philemon", "slug": "philemon", "order": 57, "testament": "NT", "chapters": 1},
        {"name": "Hebrews", "slug": "hebrews", "order": 58, "testament": "NT", "chapters": 13},
        {"name": "James", "slug": "james", "order": 59, "testament": "NT", "chapters": 5},
        {"name": "1 Peter", "slug": "1-peter", "order": 60, "testament": "NT", "chapters": 5},
        {"name": "2 Peter", "slug": "2-peter", "order": 61, "testament": "NT", "chapters": 3},
        {"name": "1 John", "slug": "1-john", "order": 62, "testament": "NT", "chapters": 5},
        {"name": "2 John", "slug": "2-john", "order": 63, "testament": "NT", "chapters": 1},
        {"name": "3 John", "slug": "3-john", "order": 64, "testament": "NT", "chapters": 1},
        {"name": "Jude", "slug": "jude", "order": 65, "testament": "NT", "chapters": 1},
        {"name": "Revelation", "slug": "revelation", "order": 66, "testament": "NT", "chapters": 22},
    ]:
        BibleBook.objects.update_or_create(
            order=book["order"],
            defaults={
                "name": book["name"],
                "slug": book["slug"],
                "testament": book["testament"],
                "chapters": book["chapters"],
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("bible", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_kjv_books, migrations.RunPython.noop),
    ]
