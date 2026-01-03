from django.shortcuts import render, redirect, get_object_or_404
from media.models import Media, MediaFormat, MediaType, MediaGenre
from media.forms import AddMediaForm, BarcodeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
import requests
import os
from django.core.files.base import ContentFile
from django.utils.text import slugify
import logging


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

    # If no metadata found, try a title-based hint via Google Books and iTunes (for music/movies)
    candidates = []
    if not meta and media.title:
        title_q = media.title
        # Google Books candidates (books)
        try:
            q = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_q}", timeout=5)
            if q.status_code == 200:
                items = q.json().get('items') or []
                for it in items[:4]:
                    vol = it.get('volumeInfo', {})
                    candidates.append({
                        'title': vol.get('title'),
                        'description': vol.get('description'),
                        'image_url': vol.get('imageLinks', {}).get('thumbnail'),
                        'categories': vol.get('categories') or [],
                        'source': 'google_books',
                        'type': 'Book',
                    })
        except Exception:
            pass

        # iTunes search: try movie and music (albums)
        try:
            import urllib.parse

            qstr = urllib.parse.quote(title_q)
            # movies
            it_movie = requests.get(f"https://itunes.apple.com/search?term={qstr}&media=movie&limit=4", timeout=5)
            if it_movie.status_code == 200:
                res = it_movie.json().get('results') or []
                for r in res[:3]:
                    candidates.append({
                        'title': r.get('trackName') or r.get('collectionName'),
                        'description': r.get('longDescription') or r.get('shortDescription') or r.get('collectionName'),
                        'image_url': r.get('artworkUrl100'),
                        'categories': [r.get('primaryGenreName')] if r.get('primaryGenreName') else [],
                        'source': 'itunes_movie',
                        'type': 'Movie',
                    })
            # music albums (CD-like)
            it_music = requests.get(f"https://itunes.apple.com/search?term={qstr}&media=music&entity=album&limit=4", timeout=5)
            if it_music.status_code == 200:
                res2 = it_music.json().get('results') or []
                for r in res2[:3]:
                    candidates.append({
                        'title': r.get('collectionName'),
                        'description': r.get('artistName'),
                        'image_url': r.get('artworkUrl100'),
                        'categories': [r.get('primaryGenreName')] if r.get('primaryGenreName') else [],
                        'source': 'itunes_album',
                        'type': 'Album',
                    })
        except Exception:
            pass

        # If candidates found, prefer the earlier Google Books meta if present
        if candidates:
            meta = candidates[0]
    # if we had an ISBN-based meta earlier, keep it as the single candidate
    if meta and not isinstance(meta, list):
        candidates = [meta]

    if not meta:
        return render(request, 'media/lookup_compare.html', {'media': media, 'meta': None})

    # Compute smart defaults for which radio should be pre-selected.
    def choose_default(current, suggested, prefer_length_delta=10, prefer_descr_len=120):
        if not current and suggested:
            return 'suggested'
        if not suggested:
            return 'current'
        # Prefer suggested if it's substantially longer (likely more complete)
        try:
            if len(suggested) > len(current or '') + prefer_length_delta:
                return 'suggested'
        except Exception:
            pass
        # otherwise keep current
        return 'current'

    # If multiple candidates, try to pick a default candidate index that best matches current type
    default_candidate = 0
    if len(candidates) > 1 and media.type:
        for i, c in enumerate(candidates):
            if c.get('type') and c.get('type').lower() == media.type.name.lower():
                default_candidate = i
                break

    # For the UI we default suggested values to the chosen candidate
    chosen = candidates[default_candidate] if candidates else meta

    default_title = choose_default(media.title, chosen.get('title') if chosen else None)
    default_subtitle = choose_default(getattr(media, 'subtitle', None), chosen.get('subtitle') if chosen else None)
    # for description, prefer suggested when our description is very short
    def descr_default(cur, sug):
        if not cur and sug:
            return 'suggested'
        if not sug:
            return 'current'
        try:
            if len(cur or '') < 80 and len(sug) > len(cur or '') + 30:
                return 'suggested'
        except Exception:
            pass
        return 'current'

    default_description = descr_default(media.description, meta.get('description'))
    default_image = 'suggested' if (not getattr(media, 'image') and meta.get('image_url')) else 'current'
    default_categories = 'suggested' if (media.genre.count() == 0 and meta.get('categories')) else 'current'

    ctx = {
        'media': media,
        'meta': meta,
        'candidates': candidates,
        'default_candidate': default_candidate,
        'default_title': default_title,
        'default_subtitle': default_subtitle,
        'default_description': default_description,
        'default_image': default_image,
        'default_categories': default_categories,
    }
    return render(request, 'media/lookup_compare.html', ctx)


@login_required
def apply_lookup(request, pk):
    """Apply selected fields from compare UI to the existing Media.

    Expects POST with choices like `choice_title=current|suggested` and
    hidden fields for suggested values.
    """
    if request.method != 'POST':
        return redirect('media:detail', pk=pk)

    # Log incoming POST for debugging selection issues
    try:
        logging.getLogger(__name__).info('apply_lookup POST payload: %s', {k: request.POST.getlist(k) for k in request.POST.keys()})
    except Exception:
        pass

    media = get_object_or_404(Media, pk=pk)

    # remember original values for diagnostics
    orig_title = media.title
    orig_subtitle = media.subtitle
    orig_description = media.description
    had_image = bool(media.image)

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

    # image handling: if user chose suggested image, download and save it into the ImageField
    suggested_image = request.POST.get('suggested_image_url')
    image_saved = False
    if request.POST.get('choice_image') == 'suggested' and suggested_image:
        try:
            resp = requests.get(suggested_image, timeout=10)
            if resp.status_code == 200:
                content = resp.content
                # try to detect image type
                try:
                    import imghdr

                    ext = imghdr.what(None, h=content)
                    if ext == 'jpeg':
                        ext = 'jpg'
                except Exception:
                    ext = None

                if not ext:
                    # fallback to extension from URL
                    from urllib.parse import urlparse

                    path = urlparse(suggested_image).path
                    ext = os.path.splitext(path)[1].lstrip('.') or 'jpg'

                filename = f"{slugify(media.title)[:50]}-{media.pk}.{ext}"
                # remove existing image file if present
                if media.image:
                    try:
                        media.image.delete(save=False)
                    except Exception:
                        pass
                media.image.save(filename, ContentFile(content), save=False)
                image_saved = True
        except Exception as e:
            image_saved = False
            logging.getLogger(__name__).exception('Image download/save failed')
            messages.warning(request, f'Image download/save failed: {e}')

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

    # diagnostics: which fields changed
    applied = []
    if orig_title != media.title:
        applied.append('title')
    if (orig_subtitle or '') != (media.subtitle or ''):
        applied.append('subtitle')
    if (orig_description or '') != (media.description or ''):
        applied.append('description')
    if image_saved:
        applied.append('image')

    if applied:
        messages.success(request, f"Updated media: {media.title} ({', '.join(applied)})")
    else:
        # nothing changed
        messages.info(request, f"No changes applied to: {media.title}")

    if image_saved:
        try:
            exists = bool(media.image and os.path.exists(media.image.path))
            if exists:
                messages.success(request, f'Image saved to {media.image.url}')
            else:
                messages.warning(request, 'Image save reported success but file not found on disk.')
        except Exception:
            messages.info(request, 'Image saved but could not verify file path.')
    elif not image_saved and request.POST.get('choice_image') == 'suggested' and suggested_image:
        messages.warning(request, 'Suggested image could not be downloaded or saved.')

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

