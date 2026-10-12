# Rooted — starter app

A faith community site for Christian girls: devotionals, Bible study
guides (with real scripture and study groups), Mood Help (with emoji
comfort, matching verses, and a private journal), a pseudonymous prayer
wall, a Gist chat board, friends, and notifications.

Everything lives in one flat folder, and one command runs the whole thing.

## Files

| File | What it does |
|---|---|
| `main.py` | The Flask app — starts the server, defines every API route, and serves the HTML/CSS/JS files |
| `database.py` | Creates and connects to `database.db` (SQLite) |
| `auth.py` | Password hashing and login tokens (JWT) |
| `emailer.py` | Sends password reset codes by email (or prints to terminal if SMTP isn't configured) |
| `seed.py` | Fills the database with starter content — Bible studies, mood help articles/emojis, affirmations, verse-of-day list |
| `requirements.txt` | The Python packages this needs |
| `database.db` | The actual database file — created automatically the first time you run the app |
| `index.html`, `login.html`, `signup.html`, `forgot-password.html`, `devotionals.html`, `bible-study.html`, `mood-help.html`, `prayer-wall.html`, `gist.html`, `friends.html`, `settings.html` | The pages |
| `style.css` | All the styling, shared across every page, light + dark theme |
| `script.js` | All the frontend JavaScript, organized into labeled sections |

## Running it locally

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# open .env and set JWT_SECRET to a long random string
python seed.py
python main.py                  # starts the whole site at http://localhost:4000
```

Open **http://localhost:4000**.

## Bible study — real scripture, live, with groups

Five studies: The Book of Ruth, Fruit of the Spirit, Psalms of Lament,
Sexual Purity, and Relationships (covering being "unequally yoked" and
navigating family/friend relationships) — 27 sessions total. Tapping a
study expands it into sessions, each with a scripture reference and
reflection questions. Tapping "📖 Read [reference]" fetches the actual
verse text live from **bible-api.com** (free, public domain World English
Bible translation, no API key needed) — **this needs the server to have
internet access**; everything else works fully offline.

**Studying with friends**: inside an expanded study, "+ Start a group"
creates a study group with one or more accepted friends. Everyone checks
off sessions as they finish them, and the group shows "X/Y done" per
session.

## Devotionals — affirmations, verse of the day, ACTS prayer guide

1. Six floating/bouncing affirmation bubbles (edit in `seed.py`)
2. A live verse of the day — same for everyone all day, changes at
   midnight UTC, picked deterministically by day-of-year from the
   `votd_verses` list in `seed.py`
3. A simple ACTS prayer guide (Adoration, Confession, Thanksgiving,
   Supplication) — static content, editable directly in `devotionals.html`

## Mood Help — emojis, matching verses, and a private journal

Tapping an emoji (😠😢😰😔😩😕😞😊) shows an encouraging statement plus 2-3
scripture references as tappable chips — tap one to reveal the real verse
text. "Journal about this feeling" opens a private journal entry, saved
with a diary-style look, visible only to the person who wrote it.

## Friends, Gist tagging, and reactions

Send/accept/decline friend requests on `friends.html`. Once friends, tag
each other in Gist posts and invite each other to Bible study groups. The
Gist board is a contained, scrollable iOS/WhatsApp-style chat (bubbles
left/right depending on sender) with five reactions — 👍 ❤️ 😢 🙏 👏 — tap
to react, tap again to remove, tap a different one to switch.

## Notifications

A 🔔 bell in the nav (every page) shows an unread badge and a dropdown of
recent activity — someone reacted to your Gist post, prayed for your
prayer request, or sent/accepted a friend request. Opening the panel
marks everything read. Checked once per page load, not real-time.

## Username-or-email login, and forgot password

Login accepts either an email or display name. "Forgot your password?"
walks through: enter your email → get a 6-digit code → enter the code
plus a new password. **Email sending needs SMTP configured** in `.env`
(see `.env.example`); without it, codes print to the terminal instead, so
reset still works while developing locally. Codes expire after 15 minutes,
single use.

## Light / dark mode and text size

Every page has a 🌙/☀️ toggle in the nav, saved per-browser. Settings →
Text size lets each user pick Small/Medium/Large/Extra Large (uses CSS
`zoom`, well-supported in Chrome/Edge/Safari).

## Symbols in navigation

Each nav link has an emoji for faster scanning: 📖 Devotionals, 📚 Bible
Study, 💛 Mood Help, 🙏 Prayer Wall, 💬 The Gist, 👥 Friends.

## Debugging tips

- **Backend errors**: `main.py` runs with `debug=True` — full stack traces
  in the browser, auto-reload on save.
- **Frontend errors**: browser dev tools (F12) → Console. All logic is in
  `script.js`, organized into labeled sections.
- **Database**: `database.db` is a real SQLite file — open with "DB
  Browser for SQLite" to inspect tables directly. Delete it and re-run
  `python seed.py` to reset.

## Before you launch to real users

1. **Moderation dashboard** — reports save into the `reports` table; build
   a way to review them, same-day for anything mentioning self-harm or abuse.
2. **Crisis response plan** — decide in advance what happens if someone
   posts something indicating they're in danger.
3. **Rate limiting** — add `Flask-Limiter` so no one account can spam.
4. **Production server** — use `gunicorn main:app`, not the dev server,
   once you deploy.
5. **Privacy policy + terms** — especially given the sensitive, personal
   nature of confessions and prayer requests, more so if any users are minors.
6. **Review posts before fully public** — a keyword filter or manual
   approval queue while your user base is small enough to manage by hand.

## Renaming things

The site is called "Rooted" as a placeholder — search for "rooted" and
"Rooted" across the HTML files and `script.js` to rename it everywhere.
