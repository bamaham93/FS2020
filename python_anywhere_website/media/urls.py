from django.urls import path
from . import views

app_name = "media"

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("movies", views.movies, name="movies"),
    path("books", views.books, name="books"),
    path("cds", views.cds, name="cds"),
    path("dvds", views.dvds, name="dvds"),
    path("amazon", views.amazon, name="amazon"),
    path("youtube", views.youtube, name="youtube"),
    path("digital-dl", views.digital_dl, name="digital_dl"),
    path("vhs", views.vhs, name="vhs"),
    path("add_media", views.add_media, name="add_media"),
    path("add-by-barcode", views.add_by_barcode, name="add_by_barcode"),
    path("remove-by-barcode", views.remove_by_barcode, name="remove_by_barcode"),
    path("save-lookup", views.save_lookup, name="save_lookup"),
    path("formats", views.formats_list, name="formats"),
    path("types", views.types_list, name="types"),
    path("genres", views.genres_list, name="genres"),
    path("<int:pk>/", views.media_detail, name="detail"),
    path("<int:pk>/lookup/", views.media_lookup, name="lookup"),
    path("<int:pk>/apply-lookup/", views.apply_lookup, name="apply_lookup"),
    path("sorted_by", views.sorted_by, name="sorted_by"),
]
