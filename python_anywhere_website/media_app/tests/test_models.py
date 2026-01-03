from django.test import TestCase

from media_app.models import (
    Media,
    MediaFormat,
    MediaType,
    MediaGenre,
    MediaLocation,
)


class MediaCRUDTests(TestCase):
    def test_media_create_read_update_delete(self):
        fmt = MediaFormat.objects.create(name="Blu-ray")
        mtype = MediaType.objects.create(name="Movie")
        g1 = MediaGenre.objects.create(name="Drama")
        g2 = MediaGenre.objects.create(name="Action")
        loc = MediaLocation.objects.create(
            description="Shelf A", shelf_unit="Unit1", shelf="S1"
        )

        media = Media.objects.create(
            title="Test Title",
            subtitle="Special",
            description="Desc",
            format=fmt,
            type=mtype,
            storage_location=loc,
            upc_code="123",
        )
        media.genre.add(g1, g2)

        # read / __str__
        self.assertIn("Test Title", str(media))

        # update
        media.title = "Changed Title"
        media.save()
        media.refresh_from_db()
        self.assertEqual(media.title, "Changed Title")

        # genres relation
        self.assertEqual(media.genre.count(), 2)

        # delete
        pk = media.pk
        media.delete()
        self.assertFalse(Media.objects.filter(pk=pk).exists())
