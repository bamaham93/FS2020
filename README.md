
# Deployed at **www.Jacob-McGowin.us**

[![Django CI](https://github.com/bamaham93/FS2020/actions/workflows/django.yml/badge.svg)](https://github.com/bamaham93/FS2020/actions/workflows/django.yml)
![Python](https://img.shields.io/badge/python-3.14.2-blue)
[![Deploy to PythonAnywhere](https://github.com/bamaham93/FS2020/actions/workflows/deploy.yml/badge.svg)](https://github.com/bamaham93/FS2020/actions/workflows/deploy.yml)

# Resume
My resume and work history. Would you like to hire me? Use the contact form found here!

# Media
My personal media library of movies, books, music, and other media. My take on a basic example of a database-drive web
app, and also a tool for my wife's use.

## Features

* **Media Library Management**: Track movies, books, CDs, DVDs, and other media formats
* **Barcode Scanning**: 
  - **Camera Scanning** (NEW): Use your smartphone camera to scan barcodes directly in the browser
    - Supports UPC, EAN, ISBN, and other barcode formats
    - Requires HTTPS or localhost for camera access
    - Uses the html5-qrcode library for barcode detection
  - Manual entry: Type barcodes manually for UPC and ISBN codes
* **Automatic Metadata Lookup**: Automatically fetch book information from Google Books API using ISBN
* **Media Organization**: Organize media by format, type, and genre
* **Storage Location Tracking**: Keep track of where physical media is stored

# Photography

A portfolio gallery for displaying my photos and photo essays with flexible artistic layouts.

## Features

* **Photo Essays**: Organize photos into themed collections or narratives
* **Multi-Essay Photos**: Use the same photo in multiple essays with per-essay ordering
* **Client Galleries (MVP)**: Public or password-protected galleries with proofing selections
* **Proofing Selections**: Favorite photos per gallery session for client feedback
* **External Downloads**: Optional download link per gallery
* **Multiple Layout Styles**: 
  - Sequential layouts (Large, Medium, Small) for storytelling
  - Masonry grid for visual impact
  - Collage layouts for mixed-size displays
* **Local & External Hosting**: Upload photos locally or link to photos hosted elsewhere (Flickr, Google Photos, etc.) to save storage
* **Standalone Photos**: Add individual photos not part of an essay
* **Photo Detail Pages**: Individual photo pages for sharing and viewing
* **Accessibility**: Alt text support for all photos
* **Rich Descriptions**: Add titles and descriptions to essays and photos
* **Per-Essay Display Toggles**: Show or hide essay titles and photo captions

# FS2020

Displays the current status and location for each of the aircraft in my personal MSFS2020 fleet.

# Bible Data

Bible text is maintained in the SQLite database used by the Django app.
Repository artifacts for `pg10.txt` and Gutenberg-specific parsing/import have been removed.

# Prayer/Messaging

A messaging system that allows sending SMS messages to contact lists (prayer groups). Features include:

* **A2P-Compliant Signup**: Users can opt-in to receive SMS messages during signup with clear consent language
* **Message Creation**: Create and save messages through the web UI
* **Group Messaging**: Send messages to predefined groups of contacts
* **Consent Management**: Only sends messages to contacts who have explicitly consented to SMS
* **Privacy-First**: Includes consent tracking with timestamps and opt-out instructions

The messaging system uses Twilio for SMS delivery and complies with A2P (Application-to-Person) messaging regulations, including:
- Explicit opt-in consent requirement
- Clear disclosure of message frequency and rates
- Opt-out instructions (reply STOP)
- Help instructions (reply HELP)


# Contributing
Contributions should be tested and include automatic testing using the Django test suite. New features must include tests to ensure that the feature continues to work as intended over time. 

## AI Usage
For rules regarding AI, see AI_Rules.md.

# CI/CD
This app is deployed using a CI/CD workflow, dependant on tests passing. As such, tests are very important to this web app.
