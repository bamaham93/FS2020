# Jacob McGowin Site Style Guide

This guide defines the shared visual language for Jacob-McGowin.us. It applies
to every Django app that inherits from `python_anywhere_website/templates/base.html`.

The system takes its cue from a field journal rather than a product dashboard:
warm paper, atmospheric imagery, purposeful typography, and practical tools that
remain easy to read.

## Core principles

1. **Use story before decoration.** A hero, image, or display heading should
   establish what a page is for before it adds visual drama.
2. **Keep utility work practical.** Forms, tables, calculators, and management
   workflows need strong contrast, predictable spacing, and plain language.
3. **Make the shared shell feel personal.** The site is an archive of aviation,
   photography, software, faith, and work—not a collection of unrelated apps.
4. **Let each app have a quiet accent.** Use the shared system first; introduce
   an app-specific treatment only where it helps the visitor understand context.
5. **Prefer restrained motion.** Interaction should clarify hierarchy, never
   delay reading or make a working tool feel ornamental.

## Where styles live

| Purpose | Location |
| --- | --- |
| Shared document shell, content blocks, font loading, messages | `python_anywhere_website/templates/base.html` |
| Shared navigation and site identity | `python_anywhere_website/templates/shared/navbar.html` |
| Theme tokens, components, responsive rules | `python_anywhere_website/static/css/my_style.css` |
| App-level structure | Each app's base template, such as `templates/fs2020/fs2020_base.html` |

Do not add a second CSS framework or a page-specific stylesheet for a one-off
adjustment. Add a reusable component or modifier to `my_style.css` when the
pattern belongs to more than one page.

## Foundation tokens

The source of truth is the `:root` block in `my_style.css`.

| Token | Hex value | Use |
| --- | --- | --- |
| `--paper` | `#F5F0E7` | Primary page background |
| `--paper-bright` | `#FFFDF8` | Cards, fields, and light text on images |
| `--paper-deep` | `#E8DDCB` | Secondary paper surfaces and quiet fills |
| `--ink` | `#202A32` | Primary text and dark contrast surface |
| `--ink-soft` | `#53606A` | Secondary text and metadata |
| `--sky` | `#55717C` | Aviation and photographic depth |
| `--sky-deep` | `#263E4C` | Deep aviation surface or dark secondary field |
| `--rust` | `#9A4E2C` | Primary action, brand mark, and editorial accent |
| `--rust-dark` | `#783817` | Hover state and darker link color |
| `--gold` | `#C58E44` | Small highlights and accessibility accents |
| `--success` | `#2F6B57` | Positive operational state |
| `--line` | `#2F3B41` at 17% opacity | Borders and separators |
| `--shadow` | `#2A281F` at 10% opacity | Elevated cards, menus, and modals |
| `--radius` | `0.25rem` | Shared corner treatment |

Use tokens rather than introducing a new hex value. A new color needs a named
semantic purpose, not just a visual preference.

### Graphic-production palette

Use these exact values for graphics, social imagery, slide backgrounds, photo
overlays, and other non-web assets. The intended look is warm archival paper
against deep aviation color—not a bright or saturated aviation brand.

| Role | Hex value | Recommended use |
| --- | --- | --- |
| Paper | `#F5F0E7` | Main light background, print-like texture base |
| Bright paper | `#FFFDF8` | Headline text over dark photos, cards, negative space |
| Aged paper | `#E8DDCB` | Secondary panel, image mat, subtle background variation |
| Ink | `#202A32` | Headline and body text on paper; deep overlay base |
| Soft ink | `#53606A` | Captions, supporting text, fine rules |
| Aviation blue | `#55717C` | Secondary color field, route or map detail |
| Deep aviation | `#263E4C` | Full-bleed dark field, dark secondary background |
| Rust | `#9A4E2C` | Primary callout, button, marker, or monogram color |
| Dark rust | `#783817` | Darker rust type or secondary emphasis |
| Brass | `#C58E44` | Small highlight, eyebrow rule, or restrained badge |
| Operational green | `#2F6B57` | Positive status only; do not use as a decorative accent |

For photo-led graphics, place a dark overlay behind type rather than applying
heavy filtering to the photo. Use a vertical gradient from `#141E1F` at 6%
opacity to `#182020` at 76% opacity. Set major hero type in `#FFFDF8` and the
small label or rule in `#F3D19D`.

Do not use pure black, pure white, neon teal, or saturated primary blue. Use
Rust as the default accent; Brass should remain sparse so it retains emphasis.

## Typography

The shared base loads two families:

- **DM Serif Display** is for `h1` through `h6`, hero statements, and other
  editorial display copy.
- **Manrope** is for navigation, body copy, forms, tables, and metadata.

Headings should be short and specific. Use sentence case for editorial headings
and compact uppercase with letter spacing only for `.eyebrow` labels, navigation,
and utility metadata.

```html
<p class="eyebrow">Fleet status</p>
<h2>Aircraft at a glance.</h2>
<p>Supporting copy explains what the visitor can do next.</p>
```

## Shared layout

Use the default `site-main--contained` layout for reference pages, forms,
tables, and ordinary content. Pages that need an edge-to-edge opening may set
the `main_class` block to `site-main--full` and follow the hero with a
`.site-section`.

```django
{% block main_class %}site-main--full{% endblock %}

{% block section1 %}
<section class="site-hero" style="--hero-image: url('...');">
  <div class="site-hero__content">
    <p class="eyebrow">Section label</p>
    <h1>Clear page statement.</h1>
    <p class="site-hero__lede">One concise explanation.</p>
  </div>
</section>

<section class="site-section">
  <!-- Page content -->
</section>
{% endblock %}
```

Use `body_class` to opt an app into a local modifier without duplicating the
global shell.

```django
{% block body_class %}site-shell site-fs2020{% endblock %}
```

## Navigation

The navigation is intentionally compact so page content leads. Keep labels
short, use the existing dropdown structure for related tools, and preserve the
mobile collapse behavior. New top-level navigation items should represent a
durable site section, not a single task or view.

## Components

### Heroes

Use `.site-hero` for a major landing or overview page. It needs a legible image,
a concise headline, and enough contrast for white copy. Do not use it on every
utility page.

### Cards

Use Bootstrap's `.card` markup. The shared theme supplies its paper surface,
spacing, and shadow. Use a specific modifier—such as `.home-card` or
`.fs2020-aircraft-card`—only when the content has a genuine layout difference.

### Buttons and links

- `.btn-primary` is the primary page action and uses rust.
- `.btn-secondary` and `.btn-outline-secondary` are restrained actions.
- Inline links should remain underlined and use the rust palette.
- Avoid putting more than one primary button in a compact action group.

### Tables and forms

Keep Bootstrap's semantic markup. The shared theme styles `.table`, `.table-dark`,
inputs, selects, textareas, labels, alerts, and modals. Do not use decorative
textures, low-contrast background images, or animation behind operational data.

### Images

Use content-relevant imagery with meaningful `alt` text. `card-img-top` images
are cropped consistently by the shared stylesheet. A hero image should be large
enough to work at desktop and mobile widths and must retain visible contrast
behind its copy.

## App-specific direction

| Area | Direction |
| --- | --- |
| FS2020 | Dusk-blue aviation imagery, route and flight-log language, operational clarity |
| Photography | Let the image lead; use a darker gallery treatment only when it improves viewing |
| Bible, Hymns, Prayer | Warm reading surfaces, generous line length, minimal visual noise |
| Resume | Same typography and spacing, with denser information hierarchy |
| Media | Catalog-like cards and tables that prioritize scanning and filtering |

## Accessibility and responsiveness

- Keep text and controls above WCAG AA contrast requirements.
- Preserve visible keyboard focus. Do not remove outlines without a stronger
  replacement.
- Use real buttons for actions and real links for navigation.
- Keep tap targets comfortable on small screens.
- Respect `prefers-reduced-motion`; do not add auto-playing or essential motion.
- Review table behavior on mobile before shipping a page with dense data.
- Test the navigation, dropdowns, forms, modals, messages, and any embedded
  content at desktop and mobile widths.

## Before opening a theme-related PR

1. Run `python_anywhere_website/manage.py check`.
2. Compile or render affected templates.
3. Review the changed page at desktop and mobile widths.
4. Verify keyboard focus, contrast, and reduced-motion behavior.
5. Run `git diff --check`.
6. Keep framework, database, and deployment changes out of a style-only PR.
