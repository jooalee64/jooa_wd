# Room Designer (Web, Python/Flask)

Magazine-style curated furniture catalog (filter by budget / style / category) +
a drag-and-drop room designer personalized by a style quiz.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Structure

```
app.py          Flask routes + JSON API
catalog.py      Catalog (32 items), budget tiers, quiz questions, scoring, recommendations
templates/      Jinja pages: discover, detail, quiz, style, designer, rooms
static/app.js       Shared helpers (localStorage, card renderer)
static/designer.js  Canvas: drag (pointer events), resize, rotate, save
static/style.css
```

## How it works
- Server (Python): catalog, filtering, quiz scoring -> style profile, recommendation ranking.
- Browser: style profile, favorites and saved rooms are stored in localStorage
  (per-browser, no database or login needed).

## API
- `GET /api/catalog`  - all items
- `GET /api/recommend?primary=&secondary=&budget=` - items ranked for a style
- `GET /api/quiz`, `POST /api/quiz {"answers": [[q, option], ...]}` - returns style profile

## Next steps
- Replace emoji "photos" with real image URLs (add an `image` field to `Item`).
- Swap `_RAW` in catalog.py for a real retailer/affiliate API.
- Move rooms/favorites to a DB (SQLite + Flask-SQLAlchemy) and add login for cross-device sync.
- Deploy: `pip install gunicorn && gunicorn app:app` (Render, Fly.io, Railway).
