# Verse of the Day

## Source and local display

The Android app requests a daily Bible reference from OurManna's HTTPS API:

`https://beta.ourmanna.com/api/v1/get?format=json&order=daily`

The app reads only `verse.details.reference` and `verse.details.version` from
the response. It deliberately ignores the API's verse text. It resolves the
reference against the installed canonical structure and displays the matching
Igbo and KJV verse from the app's local edition databases. Ranges are resolved
to the first verse because the card and deep link target one verse.

OurManna documents the daily endpoint and its `order=daily` / `order=random`
options in its [Verse of the Day API reference](https://ourmanna.readme.io/reference/get-verse-of-the-day).
Its [getting started guide](https://ourmanna.readme.io/reference/getting-started-with-your-api)
describes the daily result as changing each day. The app uses the explicit
`daily` mode and never requests `random` on refresh. These pages are older
documentation; the endpoint and JSON response shape were checked during
implementation. The API documentation does not state a dependable quota or
service-level guarantee, so availability is treated as best-effort.

## Cache and offline behavior

- One resolved reference is cached in app-private preferences with the local
  date and source metadata. No API verse text is persisted.
- Home and the notification worker use the same cache and local database
  lookup path.
- The Daily Verse page attempts the API once per local date. The worker may make a separate
  retry that day if Home could not obtain a usable reference.
- If the request fails, the last cached reference is displayed with a saved
  date label, provided it still resolves to a local verse. If no saved verse
  exists, the card remains hidden.
- API references that cannot be parsed or matched to a local verse are
  discarded.

## Notifications

Notifications are off until the user turns on **Daily Verse Notifications**
on the Daily Verse page. Android 13 and newer request notification permission only after that
opt-in action. WorkManager schedules a best-effort daily job for the next local
8:00 AM window; Android may defer it under battery and background restrictions.
The notification uses the local Igbo verse, and tapping it opens the local
reader at that book, chapter, and verse. Debug builds include a one-time worker
trigger for device checks; release builds do not contain that helper.

The feature stores no account identifier, location, or other personal data.
Its only persistent values are the selected reference/cache date, request
attempt dates, and the notification opt-in setting in app-private storage.

## Android scheduling reference

The implementation uses WorkManager periodic work (minimum interval one day)
and does not use exact alarms. See the [AndroidX WorkManager release notes](https://developer.android.com/jetpack/androidx/releases/work)
for the dependency version and platform guidance.
