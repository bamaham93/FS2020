# Prayer inbound SMS development guide

## Twilio webhook

Configure the Twilio phone number's **Messaging** setting for **A message comes
in** with:

- URL: `https://www.jacob-mcgowin.us/api/webhooks/twilio/sms/`
- Method: `POST`

The endpoint verifies `X-Twilio-Signature` with the Twilio auth token before it
accepts a request. Set `TWILIO_AUTH_TOKEN` in the production environment or in
the server-only `main_app/local_settings.py`. Never commit production Twilio
credentials.

Twilio control messages are acknowledged but are not saved to the Prayer inbox
and do not alert administrators. Matching ignores capitalization and surrounding
whitespace. The filtered keywords are `STOP`, `STOPALL`, `UNSUBSCRIBE`,
`CANCEL`, `END`, `QUIT`, `START`, `YES`, `UNSTOP`, `HELP`, and `INFO`.

Twilio's `MessageSid` is stored as a unique provider message ID. This makes
webhook retries idempotent and prevents duplicate inbox entries and alerts.

## Administrator recipients

An inbound alert is sent to the union of:

- users in the Django group named `Prayer Manager`; and
- users with Django's staff status.

An eligible user must have a linked `Person` record. That person must have a
phone number, SMS consent, and **Notify on inbound SMS** enabled. The
`Person.user` relationship is authoritative at runtime.

Migration `0014` performs a one-time rollout link for existing data. It links
only unique `Person` and `User` records whose complete first and last names
match after ignoring capitalization and repeated or surrounding whitespace.
Ambiguous matches are left unlinked for manual review in Django admin.
Messages already marked processed before the migration are initialized as read
for the Prayer Managers and staff users present during deployment.

## Inbox read state

Read state belongs to each administrator. Opening the inbox does not mark a
message read. Administrators can mark one message read or unread, or mark all
messages read. The Prayer banner and inbox unread count are calculated for the
signed-in administrator.

## Optional notification cooldown

Every inbound message sends alerts by default. To suppress alerts for messages
that arrive within a global time window, add this to the server-only
`main_app/local_settings.py`:

```python
INBOUND_SMS_ADMIN_COOLDOWN_MINUTES = 5
```

The default is `0`, which disables the cooldown. The inbound message is always
saved even when the cooldown suppresses its administrator alert.

## Tests

Run the focused inbound suite from `python_anywhere_website`:

```text
python manage.py test prayer.tests_inbound_sms
```

The suite covers signature validation, webhook retries, sender matching,
control-message filtering, recipient eligibility, notification content,
cooldown behavior, access control, and per-administrator read state.
