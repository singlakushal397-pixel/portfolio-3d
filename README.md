# 3D Full-Stack Developer Portfolio

Single-file Python 3D developer portfolio backed by SQLite3 (`kushal_portfolio.db`), Python standard-library `ThreadingHTTPServer` REST API, and a custom pure-math 3D projection UI with zero external dependencies.

## Files

- `Portfolio.py` — Complete self-contained HTTP server, SQLite data layer, REST API, and interactive 3D frontend.
- `kushal_portfolio.db` — SQLite3 database storing guestbook entries, achievements, metrics, and GitHub cache.

## Running Locally

```bash
python3 Portfolio.py
```

Then open `http://127.0.0.1:8000` in your browser.
