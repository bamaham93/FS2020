from django.shortcuts import render, redirect, get_object_or_404
from media.models import Media, MediaFormat, MediaType, MediaGenre
from media.forms import AddMediaForm, BarcodeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
import requests
import os


# Create your views here.
def index(request):
    """
    """
    # Counts by type/format and latest items for a richer index page
    types = MediaType.objects.all()
    formats = MediaFormat.objects.all()
    latest = Media.objects.order_by('-id')[:6]
    total = Media.objects.count()
    context = {
        "types": types,
        "formats": formats,
        "latest": latest,
        "total": total,
    }
    return render(request, "media/index.html", context)


def movies(request):
    """
    """
    movies = Media.objects.filter(type__name="Movie")
    context = {
        "movies": movies,
        # 'genres': movies.genres,
    }
    return render(request, "media/movies.html", context)


@login_required
def add_media(request):
    """
    """
    initial = {}
    barcode = request.GET.get("barcode")
    code_type = request.GET.get("code_type")
    if barcode:
        if code_type == "isbn":
            initial["isbn_code"] = barcode
        else:
            initial["upc_code"] = barcode

    # if metadata was fetched during lookup, prefill title/description
    lookup = request.session.pop('media_lookup', None)
    if lookup:
        if lookup.get('title'):
            initial['title'] = lookup.get('title')
        if lookup.get('description'):
            initial['description'] = lookup.get('description')
        # map categories to MediaGenre instances and prefill genre field
        cats = lookup.get('categories') or []
        genre_ids = []
        for cat in cats:
            # split multi-level categories like 'Fiction / Science Fiction'
            parts = []
            if isinstance(cat, str):
                for seg in [s.strip() for s in cat.replace('\u2013', '/').split('/') if s.strip()]:
                    # further split on commas
                    for sub in [p.strip() for p in seg.split(',') if p.strip()]:
                        parts.append(sub)
            for part in parts:
                if not part:
                    continue
                name = part.title()
                genre_obj, _ = MediaGenre.objects.get_or_create(name=name)
                genre_ids.append(genre_obj.id)
        if genre_ids:
            initial['genre'] = genre_ids

    add_media_form = AddMediaForm(initial=initial)
    context = {"add_media_form": add_media_form}

    if request.method == "POST":
        # print("Posted!")
        form = AddMediaForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/media/add_media")
    elif request.method == "GET":
        # GET handled via `initial` above
        pass
    return render(request, "media/add_media.html", context)


def add_by_barcode(request):
    """Enter a barcode; if the media exists, show it; otherwise redirect to add_media prefilled."""
    form = BarcodeForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST" and form.is_valid():
        barcode = form.cleaned_data["barcode"].strip()
        code_type = form.cleaned_data["code_type"]
        lookup_field = "upc_code" if code_type == "upc" else "isbn_code"
        kwargs = {lookup_field: barcode}
        try:
            media = Media.objects.get(**kwargs)
            messages.info(request, f"Found existing media: {media.title}")
            return redirect("media:movies")
        except Media.DoesNotExist:
            # try to fetch metadata for ISBNs (Google Books)
            meta = None
            if code_type == 'isbn':
                meta = fetch_google_books_metadata(barcode)
            # If we found metadata, show it for review and allow saving.
            if meta:
                # include barcode info so the save form can persist it
                meta.update({'barcode': barcode, 'code_type': code_type})
                return render(request, "media/lookup_result.html", {"meta": meta})
            # otherwise redirect to add media with barcode prefilled
            return redirect(f"/media/add_media?barcode={barcode}&code_type={code_type}")
    return render(request, "media/add_by_barcode.html", context)


@login_required
def save_lookup(request):
    """Save a lookup result posted from the lookup_result template."""
    if request.method != 'POST':
        return redirect('media:index')

    title = request.POST.get('title')
    description = request.POST.get('description')
    barcode = request.POST.get('barcode')
    code_type = request.POST.get('code_type')
    image_url = request.POST.get('image_url')
    categories = request.POST.get('categories', '')

    if not title:
        messages.error(request, 'No title provided; cannot save.')
        return redirect('media:add_media')

    fmt, _ = MediaFormat.objects.get_or_create(name='Unknown')
    mtype = None
    if code_type == 'isbn':
        mtype, _ = MediaType.objects.get_or_create(name='Book')

    media = Media.objects.create(
        title=title,
        description=description or '',
        format=fmt,
        type=mtype,
    )

    # set barcode fields
    if code_type == 'isbn':
        media.isbn_code = barcode
    else:
        media.upc_code = barcode
    media.save()

    # attach genres
    if categories:
        # categories expected comma- or slash-separated
        parts = []
        for seg in [s.strip() for s in categories.split(',') if s.strip()]:
            for sub in [p.strip() for p in seg.replace('\u2013', '/').split('/') if p.strip()]:
                parts.append(sub)
        for part in parts:
            name = part.title()
            g, _ = MediaGenre.objects.get_or_create(name=name)
            media.genre.add(g)

    messages.success(request, f'Saved media: {media.title}')
    return redirect('media:movies')


def remove_by_barcode(request):
    """Enter a barcode to find and remove an item."""
    form = BarcodeForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST" and form.is_valid():
        barcode = form.cleaned_data["barcode"].strip()
        code_type = form.cleaned_data["code_type"]
        lookup_field = "upc_code" if code_type == "upc" else "isbn_code"
        kwargs = {lookup_field: barcode}
        try:
            media = Media.objects.get(**kwargs)
            title = str(media)
            media.delete()
            messages.success(request, f"Removed media: {title}")
            return redirect("media:index")
        except Media.DoesNotExist:
            messages.error(request, "No media found with that barcode")
    return render(request, "media/remove_by_barcode.html", context)


def fetch_google_books_metadata(isbn):
    """Fetch basic metadata from Google Books for an ISBN. Returns dict or None."""
    def normalize_isbn(s):
        s = (s or '').strip()
        # remove common prefixes and non-alphanumeric
        s = s.upper()
        if s.startswith('ISBN'):
            s = s[4:]
        # keep digits and X
        import re
        s = re.sub(r'[^0-9X]', '', s)
        return s

    def isbn13_to_isbn10(isbn13):
        # expects a 13-digit string starting with 978/979
        if len(isbn13) != 13 or not isbn13.isdigit():
            return None
        if not (isbn13.startswith('978') or isbn13.startswith('979')):
            return None
        core = isbn13[3:12]  # 9 digits
        total = 0
        for i, ch in enumerate(core):
            total += (i + 1) * int(ch)
        check = total % 11
        check_char = 'X' if check == 10 else str(check)
        return core + check_char

    try:
        norm = normalize_isbn(isbn)
        if not norm:
            return None

        candidates = [norm]
        # if 13-digit and possible, add ISBN10 candidate
        if len(norm) == 13:
            conv = isbn13_to_isbn10(norm)
            if conv:
                candidates.append(conv)

        for cand in candidates:
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{cand}"
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                continue
            data = resp.json()
            items = data.get('items')
            if not items:
                continue
            vol = items[0].get('volumeInfo', {})
            title = vol.get('title')
            description = vol.get('description')
            image_links = vol.get('imageLinks', {})
            thumbnail = image_links.get('thumbnail')
            categories = vol.get('categories') or []
            return {'title': title, 'description': description, 'image_url': thumbnail, 'categories': categories, 'source': 'google_books', 'queried_isbn': cand}
        return None
    except Exception:
        return None


def books(request):
    books = Media.objects.filter(type__name="Book")
    context = {"books": books}
    return render(request, "media/books.html", context)


def cds(request):
    """
    """
    cds = Media.objects.filter(format__name="CD")
    context = {"cds": cds}
    return render(request, "media/cds.html", context)


def dvds(request):
    """
    """
    dvds = Media.objects.filter(format__name="DVD")
    context = {
        "dvds": dvds,
    }
    return render(request, "media/dvds.html", context)


def amazon(request):
    """
    """
    videos = Media.objects.filter(format__name="Amazon")
    context = {"videos": videos}
    return render(request, "media/amazon.html", context)


def youtube(request):
    videos = Media.objects.filter(format__name="YouTube")
    context = {
        "videos": videos,
    }
    return render(request, "media/youtube.html", context)


def digital_dl(request):
    """
    """
    videos = Media.objects.filter(format__name="Digital Download")
    context = {"videos": videos}
    return render(request, "media/digital_dl.html", context)


def vhs(request):
    """
    """
    vhs_s = Media.objects.filter(format__name="VHS")
    context = {"videos": vhs_s}
    return render(request, "media/vhs.html", context)


def media_detail(request, pk):
    """Show details for a single Media item."""
    media = get_object_or_404(Media, pk=pk)
    context = {"media": media}
    return render(request, "media/detail.html", context)


def media_lookup(request, pk):
    """Fetch metadata for an existing Media and show side-by-side comparison.

    This view renders a modal-friendly compare template where the user can choose
    current vs suggested values and either apply them or open the admin edit.
    """
    media = get_object_or_404(Media, pk=pk)

    # Prefer ISBN lookup, fall back to UPC, else None
    barcode = media.isbn_code or media.upc_code
    code_type = 'isbn' if media.isbn_code else ('upc' if media.upc_code else None)
    meta = None
    if code_type == 'isbn' and barcode:
        meta = fetch_google_books_metadata(barcode)

    # If no metadata found, try a title-based hint via Google Books simple query
    if not meta and media.title:
        try:
            q = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=intitle:{media.title}", timeout=5)
            if q.status_code == 200:
                items = q.json().get('items')
                if items:
                    vol = items[0].get('volumeInfo', {})
                    meta = {
                        'title': vol.get('title'),
                        'description': vol.get('description'),
                        'image_url': vol.get('imageLinks', {}).get('thumbnail'),
                        'categories': vol.get('categories') or [],
                        'source': 'google_books_title'
                    }
        except Exception:
            meta = None

    if not meta:
        return render(request, 'media/lookup_compare.html', {'media': media, 'meta': None})

    return render(request, 'media/lookup_compare.html', {'media': media, 'meta': meta})


@login_required
def apply_lookup(request, pk):
    """Apply selected fields from compare UI to the existing Media.

    Expects POST with choices like `choice_title=current|suggested` and
    hidden fields for suggested values.
    """
    if request.method != 'POST':
        return redirect('media:detail', pk=pk)

    media = get_object_or_404(Media, pk=pk)

    # Determine title
    if request.POST.get('choice_title') == 'suggested':
        new_title = request.POST.get('suggested_title') or media.title
    else:
        new_title = media.title

    # subtitle not always present
    if request.POST.get('choice_subtitle') == 'suggested':
        new_subtitle = request.POST.get('suggested_subtitle') or media.subtitle
    else:
        new_subtitle = media.subtitle

    # description
    if request.POST.get('choice_description') == 'suggested':
        new_description = request.POST.get('suggested_description') or ''
    else:
        new_description = media.description or ''

    # image handling: store URL string in image_url field if model has field `image` requires download;
    suggested_image = request.POST.get('suggested_image_url')
    if request.POST.get('choice_image') == 'suggested' and suggested_image:
        # We currently store remote image URL in a helper field if present, but the Media model's `image`
        # is a FileField/ImageField; downloading is left for future work. For now, set nothing and
        # save suggested URL to a `description` note or skip. We'll attach as an external_url attribute in session.
        # (Better: enqueue a background job to download.)
        # For now, just leave media.image unchanged.
        pass

    # Categories: replace genres if suggested chosen
    if request.POST.get('choice_categories') == 'suggested':
        cats = request.POST.get('suggested_categories', '')
        # clear current genres and replace
        media.genre.clear()
        parts = []
        for seg in [s.strip() for s in cats.split(',') if s.strip()]:
            for sub in [p.strip() for p in seg.replace('\u2013', '/').split('/') if p.strip()]:
                parts.append(sub)
        for part in parts:
            name = part.title()
            g, _ = MediaGenre.objects.get_or_create(name=name)
            media.genre.add(g)

    # apply scalar fields
    media.title = new_title
    media.subtitle = new_subtitle
    media.description = new_description
    media.save()

    messages.success(request, f'Updated media: {media.title}')
    return redirect('media:detail', pk=media.pk)


def sorted_by(request):
    """
    """
    media_qs = Media.objects.all()
    fmt = request.GET.get('format')
    typ = request.GET.get('type')
    if fmt:
        media_qs = media_qs.filter(format__name=fmt)
    if typ:
        media_qs = media_qs.filter(type__name=typ)
    # support genre filter by name
    genre_name = request.GET.get('genre')
    if genre_name:
        media_qs = media_qs.filter(genre__name=genre_name)
    context = {
        "media_query": media_qs,
        "filter_format": fmt,
        "filter_type": typ,
    }
    return render(request, 'media/sorted_by.html', context)


def formats_list(request):
    """List all formats with counts and links to filtered pages."""
    formats = MediaFormat.objects.all()
    context = {"formats": formats}
    return render(request, 'media/formats.html', context)


def types_list(request):
    """List all media types with counts and links to filtered pages."""
    types = MediaType.objects.all()
    context = {"types": types}
    return render(request, 'media/types.html', context)


def genres_list(request):
    """List all genres with counts and links to filtered pages."""
    genres = MediaGenre.objects.all()
    context = {"genres": genres}
    return render(request, 'media/genres.html', context)

