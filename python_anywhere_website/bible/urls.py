from django.urls import path
from . import views
from . import api_views

app_name = "bible"

urlpatterns = [
    # Reader URLs
    path("", views.book_list, name="index"),
    path("<slug:book_slug>/", views.chapter_list, name="chapter_list"),
    path("<slug:book_slug>/<int:chapter>/", views.chapter_reader, name="chapter_reader"),
]

# API URLs (separate pattern to avoid /bible/ prefix)
api_urlpatterns = [
    path("api/v1/bible/books", api_views.api_books, name="api_books"),
    path("api/v1/bible/books/<slug:book_slug>/chapters/<int:chapter>", api_views.api_chapter, name="api_chapter"),
    path("api/v1/bible/passage", api_views.api_passage, name="api_passage"),
]

