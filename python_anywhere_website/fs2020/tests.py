from django.test import TestCase
from django.utils import timezone

from .models import Aircraft, Flight


class AircraftCRUDTests(TestCase):
	def test_create_read_update_delete_aircraft(self):
		a = Aircraft.objects.create(
			n_num="N12345",
			make="Cessna",
			model="172",
			icao_location="KBHM",
		)
		# read / repr
		self.assertEqual(str(a), "N12345")

		# update
		a.status = "In Flight"
		a.save()
		a.refresh_from_db()
		self.assertEqual(a.status, "In Flight")

		# delete
		pk = a.pk
		a.delete()
		self.assertFalse(Aircraft.objects.filter(pk=pk).exists())


class FlightCRUDTests(TestCase):
	def test_create_update_delete_flight(self):
		aircraft = Aircraft.objects.create(
			n_num="N54321",
			make="Piper",
			model="PA-28",
			icao_location="KXYZ",
		)

		dep = timezone.now()
		f = Flight.objects.create(
			rules="VFR",
			n_num=aircraft,
			icao_origin="KBHM",
			departure_datetime=dep,
			altitude=3500,
			route="KBHM direct KXYZ",
			icao_destination="KXYZ",
		)

		self.assertEqual(str(f), "KBHM-KXYZ")

		# update altitude
		f.altitude = 4000
		f.save()
		f.refresh_from_db()
		self.assertEqual(f.altitude, 4000)

		# delete
		pk = f.pk
		f.delete()
		self.assertFalse(Flight.objects.filter(pk=pk).exists())
