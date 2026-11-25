
#!/usr/bin/env python3
"""
KUSHAL SINGLA — Single-File 3D Full-Stack Developer Portfolio
=============================================================
Architecture:
  - Database : SQLite3 (auto-created at ./kushal_portfolio.db)
  - Backend  : Python 3 Standard Library ThreadingHTTPServer + REST API
  - Frontend : Embedded HTML5 + CSS3 3D + Pure-Math 3D Canvas Engine (0 dependencies)

Run:
  python3 portfolio.py
Then open:
  http://127.0.0.1:8000
"""

import json
import os
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# ==============================================================================
# CONFIGURATION — Update your GitHub username & links here
# ==============================================================================
HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", 8000))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kushal_portfolio.db")
GITHUB_USERNAME = "kushalsingla"  # <-- Change to your exact GitHub username
CACHE_TTL_SECONDS = 1800  # Cache GitHub API results in SQLite for 30 minutes
START_TIME = time.time()

PROFILE = {
    "name": "Kushal Singla",
    "handle": "kushal@nst",
    "role": "B.Tech CS & AI Engineer • Python Enthusiast",
    "institution": "Newton School of Technology × Rishihood University",
    "location": "Sonipat, India",
    "core_language": "Python",
    "tagline": "Writing clean Python so machines suffer less and humans smile more.",
    "intro": (
        "Hey, I'm Kushal Singla — a B.Tech Computer Science & AI student at "
        "Newton School of Technology (in collaboration with Rishihood University). "
        "Python is my home turf: I love bending ASTs, dissecting algorithms, building "
        "developer tools, and shipping full-stack systems that actually work on the first demo. "
        "This entire 3D website — SQLite database, REST API, and interactive 3D engine — lives "
        "inside one single Python file with zero external dependencies."
    ),
    "links": {
        "github": f"https://github.com/{GITHUB_USERNAME}",
        "behance": "https://www.behance.net/",
        "email": "mailto:kushal.singla@example.com",
    },
    "skills": [
        {"name": "Python (Core, AST, Automation)", "level": 95, "tag": "Core"},
        {"name": "Data Structures & Algorithms", "level": 88, "tag": "CS"},
        {"name": "AI / Local LLMs (Ollama, BM25)", "level": 86, "tag": "AI"},
        {"name": "Linux CLI, Bash & OS Internals", "level": 85, "tag": "Systems"},
        {"name": "Git, GitHub & PR Workflows", "level": 90, "tag": "DevOps"},
        {"name": "Full-Stack Web (HTML/CSS/JS/SQL)", "level": 84, "tag": "Web"},
        {"name": "UI/UX & Product Prototyping", "level": 82, "tag": "Design"},
        {"name": "Computer Networks & Java", "level": 78, "tag": "Foundations"},
    ],
}

SEED_ACHIEVEMENTS = [
    (
        "DocDrift — Automated Docs Drift Engine",
        "2026 • Hacktoberfest",
        "Project",
        "Engineered a developer tool combining Python AST static analysis, BM25 information retrieval, "
        "and local open-weight LLMs via Ollama to automatically catch stale documentation inside GitHub Pull Requests.",
        "Python,AST,BM25,Ollama,GitHub PRs",
    ),
    (
        "Eureka! 2026 — E-Cell IIT Bombay",
        "2026 • Competition",
        "Achievement",
        "Competed in Asia's largest business model challenge organized by E-Cell IIT Bombay, "
        "bridging systems engineering with viable product strategy.",
        "Entrepreneurship,Product Strategy,Pitching",
    ),
    (
        "Mini Search Engine: PageRank vs Keyword Frequency",
        "2026 • Algorithms",
        "Project",
        "Built an interactive miniature search engine comparing traditional keyword-frequency "
        "ranking head-to-head against Google's PageRank algorithm in a side-by-side tabular interface.",
        "Python,PageRank,IR,Web App",
    ),
    (
        "Full-Stack E-Commerce Architecture",
        "2026 • Full-Stack",
        "Project",
        "Designed and built an end-to-end Flipkart/Amazon-inspired e-commerce application "
        "covering frontend state, REST APIs, and relational database modeling.",
        "Full-Stack,Database,REST API,UI",
    ),
    (
        "Vael — Smart Wardrobe Ecosystem",
        "2026 • UI/UX Design",
        "Archive",
        "Conceptualized and designed an AI-assisted wardrobe ecosystem and mobile interface "
        "showcased on Behance, focusing on crisp visual hierarchy and tactile minimalism.",
        "UI/UX,Behance,Product Design",
    ),
    (
        "CS Zero-to-One Foundations & CLI Mastery",
        "2025–2026 • Archive",
        "Archive",
        "Mastered core CS building blocks from scratch: recursion, DSA problem-solving, "
        "Bash scripting, Linux CLI customization, Computer Networks, and Git internals.",
        "DSA,Linux,Bash,Git,Networks",
    ),
]

FALLBACK_REPOS = [
    {
        "name": "docdrift",
        "description": "Catch stale docs before merge using Python AST static analysis, BM25 & local Ollama LLMs.",
        "language": "Python",
        "stargazers_count": 18,
        "forks_count": 4,
        "html_url": f"https://github.com/{GITHUB_USERNAME}",
        "updated_at": "2026-11-10T10:00:00Z",
        "is_fallback": True,
    },
    {
        "name": "pagerank-vs-frequency-engine",
        "description": "Side-by-side miniature search engine pitting PageRank against classic keyword frequency.",
        "language": "Python",
        "stargazers_count": 12,
        "forks_count": 2,
        "html_url": f"https://github.com/{GITHUB_USERNAME}",
        "updated_at": "2026-11-02T14:20:00Z",
        "is_fallback": True,
    },
    {
        "name": "single-file-3d-portfolio",
        "description": "SQLite + Python HTTP Server + Custom 3D Projection Engine crammed cleanly into one file. 0 dependencies.",
        "language": "Python",
        "stargazers_count": 42,
        "forks_count": 7,
        "html_url": f"https://github.com/{GITHUB_USERNAME}",
        "updated_at": "2026-11-24T00:00:00Z",
        "is_fallback": True,
    },
    {
        "name": "ecommerce-fullstack-lab",
        "description": "Amazon/Flipkart-inspired storefront engineered for deep frontend, backend & DB mastery.",
        "language": "JavaScript",
        "stargazers_count": 9,
        "forks_count": 1,
        "html_url": f"https://github.com/{GITHUB_USERNAME}",
        "updated_at": "2026-10-28T09:15:00Z",
        "is_fallback": True,
    },
]


# ==============================================================================
# DATABASE LAYER (SQLite3)
# ==============================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                period TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                tags TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS guestbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metrics (
                key TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS github_cache (
                username TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                fetched_at REAL NOT NULL
            );
            """
        )

        # Seed metrics if missing
        for key, default_val in [("page_views", 1), ("api_hits", 1)]:
            conn.execute(
                "INSERT OR IGNORE INTO metrics (key, value) VALUES (?, ?)",
                (key, default_val),
            )

        # Seed achievements once
        ach_count = conn.execute("SELECT COUNT(*) FROM achievements").fetchone()[0]
        if ach_count == 0:
            conn.executemany(
                "INSERT INTO achievements (title, period, category, description, tags) VALUES (?, ?, ?, ?, ?)",
                SEED_ACHIEVEMENTS,
            )

        # Seed initial guestbook entries once
        gb_count = conn.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
        if gb_count == 0:
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            conn.executemany(
                "INSERT INTO guestbook (author, role, message, created_at) VALUES (?, ?, ?, ?)",
                [
                    (
                        "Guido's Ghost (Unofficial)",
                        "Indentation Inspector",
                        "Zero pip installs, SQLite + REST + 3D engine in one file, and crisp 4-space indentation. Approved.",
                        now_str,
                    ),
                    (
                        "Local Dev",
                        "Recovering React Developer",
                        "Wait... 3D graphics, a database, and an API with zero node_modules? Is this even legal?",
                        now_str,
                    ),
                ],
            )
        conn.commit()


def bump_metric(key, delta=1):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO metrics (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = value + ?",
            (key, delta, delta),
        )
        val = conn.execute("SELECT value FROM metrics WHERE key = ?", (key,)).fetchone()[0]
        conn.commit()
        return val


def get_metrics():
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM metrics").fetchall()
        data = {r["key"]: r["value"] for r in rows}
        data["achievements_count"] = conn.execute("SELECT COUNT(*) FROM achievements").fetchone()[0]
        data["guestbook_count"] = conn.execute("SELECT COUNT(*) FROM guestbook").fetchone()[0]
        data["uptime_seconds"] = int(time.time() - START_TIME)
        data["db_size_kb"] = round(os.path.getsize(DB_PATH) / 1024, 2) if os.path.exists(DB_PATH) else 0
        try:
            with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
                data["single_file_lines"] = sum(1 for _ in f)
        except OSError:
            data["single_file_lines"] = 0
        return data


def fetch_github_repos(username):
    username = (username or GITHUB_USERNAME).strip()
    if not username:
        username = GITHUB_USERNAME

    now = time.time()
    with get_db() as conn:
        row = conn.execute(
            "SELECT payload, fetched_at FROM github_cache WHERE username = ?",
            (username.lower(),),
        ).fetchone()
        if row and (now - row["fetched_at"] < CACHE_TTL_SECONDS):
            return {"source": "sqlite_cache", "username": username, "repos": json.loads(row["payload"])}

    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=12"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Kushal-Singla-SingleFile-3D-Portfolio/2.0",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            repos = [
                {
                    "name": r.get("name", "unnamed-repo"),
                    "description": r.get("description") or "No description yet — code speaks louder than READMEs.",
                    "language": r.get("language") or "Python",
                    "stargazers_count": r.get("stargazers_count", 0),
                    "forks_count": r.get("forks_count", 0),
                    "html_url": r.get("html_url", f"https://github.com/{username}"),
                    "updated_at": r.get("updated_at", ""),
                    "is_fallback": False,
                }
                for r in raw
                if isinstance(r, dict)
            ]
            if repos:
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO github_cache (username, payload, fetched_at) VALUES (?, ?, ?) "
                        "ON CONFLICT(username) DO UPDATE SET payload = excluded.payload, fetched_at = excluded.fetched_at",
                        (username.lower(), json.dumps(repos), now),
                    )
                    conn.commit()
                return {"source": "github_live", "username": username, "repos": repos}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        pass

    return {
        "source": "fallback_showcase",
        "username": username,
        "note": f"Could not reach live GitHub repos for '{username}'. Showing Kushal's featured builds (try typing your exact GitHub username above).",
        "repos": FALLBACK_REPOS,
    }


# ==============================================================================
# BACKEND LAYER (HTTP Request Handler & REST API)
# ==============================================================================
class PortfolioHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {self.address_string()} -> {fmt % args}")

    def _send_json(self, payload, status=200, extra_headers=None):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Powered-By", "Pure-Python-Stdlib-3D-Monolith")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_str, status=200):
        body = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Powered-By", "Pure-Python-Stdlib-3D-Monolith")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if length <= 0 or length > 16384:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None

    def do_GET(self):
        t0 = time.perf_counter()
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            bump_metric("page_views", 1)
            rendered = HTML_TEMPLATE.replace("__DEFAULT_GITHUB__", GITHUB_USERNAME)
            return self._send_html(rendered)

        if path == "/api/portfolio":
            bump_metric("api_hits", 1)
            with get_db() as conn:
                achievements = [
                    {
                        "id": r["id"],
                        "title": r["title"],
                        "period": r["period"],
                        "category": r["category"],
                        "description": r["description"],
                        "tags": [t.strip() for t in r["tags"].split(",") if t.strip()],
                    }
                    for r in conn.execute("SELECT * FROM achievements ORDER BY id ASC").fetchall()
                ]
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            return self._send_json(
                {
                    "profile": PROFILE,
                    "achievements": achievements,
                    "metrics": get_metrics(),
                    "latency_ms": latency_ms,
                }
            )

        if path == "/api/repos":
            bump_metric("api_hits", 1)
            qs = parse_qs(parsed.query)
            user = qs.get("user", [GITHUB_USERNAME])[0]
            data = fetch_github_repos(user)
            data["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return self._send_json(data)

        if path == "/api/guestbook":
            bump_metric("api_hits", 1)
            with get_db() as conn:
                entries = [
                    dict(r)
                    for r in conn.execute(
                        "SELECT id, author, role, message, created_at FROM guestbook ORDER BY id DESC LIMIT 30"
                    ).fetchall()
                ]
            return self._send_json({"entries": entries})

        if path == "/api/export":
            bump_metric("api_hits", 1)
            with get_db() as conn:
                achievements = [dict(r) for r in conn.execute("SELECT * FROM achievements").fetchall()]
                guestbook = [dict(r) for r in conn.execute("SELECT * FROM guestbook ORDER BY id DESC").fetchall()]
                tables = [
                    r["name"]
                    for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                ]
            dossier = {
                "exported_at_utc": datetime.now(timezone.utc).isoformat(),
                "architecture_proof": {
                    "pattern": "Single-File 3D Full-Stack Monolith",
                    "external_dependencies": 0,
                    "backend": "Python 3 http.server.ThreadingHTTPServer",
                    "database": "SQLite3",
                    "graphics": "Custom Pure-JS 3D Projection + CSS3 Preserve-3D",
                    "sqlite_tables": tables,
                    "verdict": "Certified Extraordinary by Zero-Dependency Gang",
                },
                "profile": PROFILE,
                "metrics": get_metrics(),
                "achievements": achievements,
                "guestbook": guestbook,
            }
            return self._send_json(
                dossier,
                extra_headers={
                    "Content-Disposition": 'attachment; filename="kushal_singla_dev_dossier.json"'
                },
            )

        return self._send_json(
            {
                "error": "404 Not Found",
                "hint": "Even Python's traceback couldn't find this route. Try '/' or '/api/export'.",
            },
            status=404,
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/guestbook":
            bump_metric("api_hits", 1)
            data = self._read_json_body()
            if not data:
                return self._send_json({"error": "Invalid JSON payload"}, status=400)

            author = str(data.get("author", "")).strip()[:60]
            role = str(data.get("role", "Fellow Developer")).strip()[:60] or "Fellow Developer"
            message = str(data.get("message", "")).strip()[:400]

            if not author or not message:
                return self._send_json(
                    {"error": "Both 'author' and 'message' are required to merge this PR."},
                    status=400,
                )

            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            with get_db() as conn:
                cur = conn.execute(
                    "INSERT INTO guestbook (author, role, message, created_at) VALUES (?, ?, ?, ?)",
                    (author, role, message, now_str),
                )
                conn.commit()
                new_id = cur.lastrowid

            return self._send_json(
                {
                    "status": "merged",
                    "entry": {
                        "id": new_id,
                        "author": author,
                        "role": role,
                        "message": message,
                        "created_at": now_str,
                    },
                },
                status=201,
            )

        return self._send_json({"error": "Endpoint not found"}, status=404)


# ==============================================================================
# FRONTEND LAYER (Embedded 3D HTML5 + CSS3 + Custom 3D Engine)
# ==============================================================================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Kushal Singla // 3D Single-File Full-Stack Monolith</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #050811;
      --surface: rgba(13, 19, 35, 0.72);
      --border: rgba(0, 245, 160, 0.22);
      --border-hover: rgba(0, 245, 160, 0.72);
      --mint: #00f5a0;
      --cyan: #38bdf8;
      --amber: #fbbf24;
      --coral: #fb7185;
      --purple: #a78bfa;
      --text: #f1f5f9;
      --muted: #94a3b8;
      --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
      --sans: 'Space Grotesk', system-ui, -apple-system, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }

    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      line-height: 1.6;
      min-height: 100vh;
      overflow-x: hidden;
      perspective: 1400px;
    }

    /* Full-Screen 3D Space & Cyber Floor Canvas */
    #bg-3d {
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      z-index: 0;
      pointer-events: none;
    }

    a { color: var(--cyan); text-decoration: none; }
    a:hover { color: var(--mint); }

    .container {
      position: relative;
      z-index: 2;
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 20px 88px;
      transform-style: preserve-3d;
    }

    /* True 3D Tiltable Surface */
    .tilt-3d {
      position: relative;
      transform-style: preserve-3d;
      will-change: transform;
      transition: transform 0.16s cubic-bezier(0.2, 0.8, 0.2, 1), border-color 0.25s ease, box-shadow 0.25s ease;
    }

    .tilt-3d::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      background: radial-gradient(
        420px circle at var(--mx, 50%) var(--my, 50%),
        rgba(0, 245, 160, 0.16),
        rgba(56, 189, 248, 0.06) 35%,
        transparent 70%
      );
      opacity: 0;
      transition: opacity 0.25s ease;
      pointer-events: none;
      z-index: 0;
    }

    .tilt-3d:hover::before { opacity: 1; }
    .tilt-3d:hover {
      border-color: var(--border-hover);
      box-shadow:
        0 24px 54px -18px rgba(0, 0, 0, 0.85),
        0 0 28px -6px rgba(0, 245, 160, 0.25);
    }

    .tilt-3d > * { position: relative; z-index: 1; }
    .z-pop-1 { transform: translateZ(18px); }
    .z-pop-2 { transform: translateZ(34px); }

    /* Top Nav */
    .topbar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 13px 20px;
      background: rgba(10, 16, 30, 0.78);
      border: 1px solid var(--border);
      border-radius: 16px;
      backdrop-filter: blur(16px);
      margin-bottom: 28px;
      font-family: var(--mono);
      font-size: 0.82rem;
      box-shadow: 0 14px 36px rgba(0, 0, 0, 0.55);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
      color: var(--mint);
    }

    .pulse-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--mint);
      box-shadow: 0 0 14px var(--mint);
      animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.45; transform: scale(0.8); }
    }

    .nav-links {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
    }

    .nav-links a { color: var(--muted); transition: color 0.2s; }
    .nav-links a:hover { color: var(--mint); }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: var(--mono);
      font-size: 0.82rem;
      font-weight: 600;
      padding: 9px 15px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: rgba(0, 245, 160, 0.09);
      color: var(--mint);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .btn:hover {
      border-color: var(--mint);
      background: rgba(0, 245, 160, 0.2);
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0, 245, 160, 0.2);
    }

    .btn-cyan {
      color: var(--cyan);
      border-color: rgba(56, 189, 248, 0.35);
      background: rgba(56, 189, 248, 0.11);
    }

    .btn-cyan:hover {
      border-color: var(--cyan);
      background: rgba(56, 189, 248, 0.22);
      box-shadow: 0 8px 20px rgba(56, 189, 248, 0.22);
    }

    /* Hero 3D Stage */
    .hero {
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 24px;
      margin-bottom: 26px;
      perspective: 1200px;
    }

    @media (max-width: 920px) {
      .hero { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 26px;
      backdrop-filter: blur(14px);
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: var(--mono);
      font-size: 0.76rem;
      color: var(--amber);
      background: rgba(251, 191, 36, 0.1);
      border: 1px solid rgba(251, 191, 36, 0.35);
      padding: 5px 11px;
      border-radius: 999px;
      margin-bottom: 16px;
    }

    h1 {
      font-size: clamp(2.1rem, 4.2vw, 3.3rem);
      line-height: 1.08;
      letter-spacing: -0.03em;
      margin-bottom: 12px;
      text-shadow: 0 10px 30px rgba(0, 245, 160, 0.16);
    }

    .gradient-name {
      background: linear-gradient(95deg, var(--mint), var(--cyan), var(--purple));
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }

    .subtitle {
      font-family: var(--mono);
      font-size: 0.9rem;
      color: var(--cyan);
      margin-bottom: 16px;
    }

    .intro-text {
      color: #cbd5e1;
      font-size: 0.98rem;
      margin-bottom: 22px;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }

    /* Interactive 3D Hologram Viewport */
    .holo-stage {
      background: radial-gradient(circle at 50% 45%, rgba(0, 245, 160, 0.10), rgba(5, 8, 17, 0.88) 72%);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 20px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 390px;
      backdrop-filter: blur(14px);
      overflow: hidden;
    }

    .holo-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--mono);
      font-size: 0.74rem;
      color: var(--cyan);
    }

    .holo-badge {
      padding: 3px 9px;
      border-radius: 999px;
      border: 1px solid rgba(0, 245, 160, 0.35);
      background: rgba(0, 245, 160, 0.1);
      color: var(--mint);
    }

    #holo-canvas {
      width: 100%;
      height: 270px;
      display: block;
      cursor: grab;
      touch-action: none;
    }

    #holo-canvas:active { cursor: grabbing; }

    .holo-controls {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      padding-top: 8px;
      border-top: 1px solid rgba(148, 163, 184, 0.15);
    }

    .shape-btns { display: flex; flex-wrap: wrap; gap: 6px; }

    .shape-btn {
      font-family: var(--mono);
      font-size: 0.72rem;
      padding: 5px 10px;
      border-radius: 8px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      background: rgba(15, 23, 42, 0.65);
      color: var(--muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .shape-btn.active, .shape-btn:hover {
      color: var(--mint);
      border-color: var(--mint);
      background: rgba(0, 245, 160, 0.12);
    }

    /* Interactive 3D Terminal Deck */
    .terminal {
      display: flex;
      flex-direction: column;
      background: rgba(5, 9, 19, 0.86);
      border: 1px solid rgba(56, 189, 248, 0.34);
      border-radius: 20px;
      overflow: hidden;
      margin-bottom: 28px;
      backdrop-filter: blur(14px);
      box-shadow: 0 22px 50px rgba(0, 0, 0, 0.6);
    }

    .term-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 11px 16px;
      background: rgba(15, 23, 42, 0.9);
      border-bottom: 1px solid rgba(148, 163, 184, 0.16);
      font-family: var(--mono);
      font-size: 0.76rem;
      color: var(--muted);
    }

    .term-dots { display: flex; gap: 7px; }
    .dot { width: 11px; height: 11px; border-radius: 50%; }
    .dot.r { background: #ef4444; }
    .dot.y { background: #f59e0b; }
    .dot.g { background: #10b981; }

    .term-body {
      padding: 16px 18px;
      font-family: var(--mono);
      font-size: 0.83rem;
      overflow-y: auto;
      height: 215px;
      color: #cbd5e1;
      white-space: pre-wrap;
    }

    .term-line { margin-bottom: 7px; }
    .term-cmd { color: var(--mint); }
    .term-warn { color: var(--amber); }
    .term-cyan { color: var(--cyan); }
    .term-coral { color: var(--coral); }

    .term-input-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 11px 16px;
      border-top: 1px solid rgba(148, 163, 184, 0.16);
      background: rgba(9, 14, 28, 0.95);
      font-family: var(--mono);
      font-size: 0.84rem;
    }

    .term-prompt { color: var(--mint); font-weight: 700; }

    .term-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text);
      font-family: var(--mono);
      font-size: 0.84rem;
    }

    /* Telemetry Strip */
    .telemetry {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
      gap: 14px;
      margin-bottom: 42px;
      perspective: 1000px;
    }

    .stat-box {
      background: var(--surface);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 16px;
      padding: 15px 18px;
      font-family: var(--mono);
      backdrop-filter: blur(12px);
    }

    .stat-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
    .stat-val { font-size: 1.38rem; font-weight: 700; color: var(--mint); margin-top: 4px; }

    /* Section Headings */
    .section-head {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-end;
      gap: 14px;
      margin: 46px 0 20px;
    }

    .section-title {
      font-size: 1.6rem;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .section-title span {
      font-family: var(--mono);
      color: var(--mint);
      font-size: 1rem;
    }

    /* Skills */
    .skills-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(255px, 1fr));
      gap: 15px;
      perspective: 1000px;
    }

    .skill-item {
      background: var(--surface);
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 16px;
      padding: 16px 18px;
      backdrop-filter: blur(12px);
    }

    .skill-top {
      display: flex;
      justify-content: space-between;
      font-size: 0.88rem;
      margin-bottom: 10px;
    }

    .skill-tag { font-family: var(--mono); font-size: 0.72rem; color: var(--cyan); }

    .bar-track {
      height: 8px;
      background: rgba(148, 163, 184, 0.16);
      border-radius: 999px;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--mint), var(--cyan));
      border-radius: 999px;
      box-shadow: 0 0 12px rgba(0, 245, 160, 0.5);
    }

    /* Repos & Achievements */
    .repo-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }

    .input {
      background: rgba(9, 14, 28, 0.9);
      border: 1px solid rgba(148, 163, 184, 0.28);
      border-radius: 10px;
      padding: 8px 12px;
      color: var(--text);
      font-family: var(--mono);
      font-size: 0.82rem;
      outline: none;
    }

    .input:focus { border-color: var(--mint); }

    .grid-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(295px, 1fr));
      gap: 18px;
      perspective: 1200px;
    }

    .repo-card, .ach-card {
      background: var(--surface);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 18px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 14px;
      backdrop-filter: blur(12px);
    }

    .repo-name {
      font-family: var(--mono);
      font-size: 1.02rem;
      font-weight: 700;
      color: var(--mint);
    }

    .repo-desc, .ach-desc { color: var(--muted); font-size: 0.9rem; }

    .meta-row {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      font-family: var(--mono);
      font-size: 0.76rem;
      color: var(--muted);
    }

    .pill {
      display: inline-block;
      font-family: var(--mono);
      font-size: 0.72rem;
      padding: 3px 9px;
      border-radius: 999px;
      background: rgba(56, 189, 248, 0.12);
      color: var(--cyan);
      border: 1px solid rgba(56, 189, 248, 0.28);
    }

    .pill.mint {
      background: rgba(0, 245, 160, 0.12);
      color: var(--mint);
      border-color: rgba(0, 245, 160, 0.3);
    }

    .pill.amber {
      background: rgba(251, 191, 36, 0.12);
      color: var(--amber);
      border-color: rgba(251, 191, 36, 0.3);
    }

    .filter-tabs { display: flex; gap: 8px; flex-wrap: wrap; }
    .tab-btn {
      font-family: var(--mono);
      font-size: 0.78rem;
      padding: 6px 12px;
      border-radius: 8px;
      border: 1px solid rgba(148, 163, 184, 0.25);
      background: rgba(13, 19, 35, 0.6);
      color: var(--muted);
      cursor: pointer;
      transition: all 0.2s;
    }

    .tab-btn.active, .tab-btn:hover {
      color: var(--mint);
      border-color: var(--mint);
      background: rgba(0, 245, 160, 0.12);
    }

    /* Guestbook */
    .guestbook-wrap {
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 20px;
      perspective: 1200px;
    }

    @media (max-width: 850px) {
      .guestbook-wrap { grid-template-columns: 1fr; }
    }

    .form-group { margin-bottom: 12px; }
    .form-group label {
      display: block;
      font-family: var(--mono);
      font-size: 0.76rem;
      color: var(--muted);
      margin-bottom: 5px;
    }

    .form-group input, .form-group textarea {
      width: 100%;
      background: rgba(7, 11, 22, 0.9);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 10px;
      padding: 10px 12px;
      color: var(--text);
      font-family: var(--sans);
      font-size: 0.9rem;
      outline: none;
    }

    .form-group textarea { min-height: 92px; resize: vertical; }
    .form-group input:focus, .form-group textarea:focus { border-color: var(--mint); }

    .gb-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: 360px;
      overflow-y: auto;
      padding-right: 4px;
    }

    .gb-item {
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.16);
      border-radius: 12px;
      padding: 14px;
    }

    .gb-head {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-family: var(--mono);
      font-size: 0.78rem;
      margin-bottom: 6px;
    }

    .gb-author { color: var(--mint); font-weight: 700; }
    .gb-time { color: var(--muted); font-size: 0.72rem; }

    .footer {
      margin-top: 56px;
      padding-top: 22px;
      border-top: 1px solid rgba(148, 163, 184, 0.18);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 12px;
      font-family: var(--mono);
      font-size: 0.78rem;
      color: var(--muted);
    }

    .notice {
      font-family: var(--mono);
      font-size: 0.78rem;
      color: var(--amber);
      margin-bottom: 12px;
    }
  </style>
</head>
<body>
  <!-- 3D Background Starfield + Perspective Grid -->
  <canvas id="bg-3d" aria-hidden="true"></canvas>

  <div class="container">
    <!-- TOP NAV -->
    <header class="topbar">
      <div class="brand">
        <span class="pulse-dot"></span>
        <span>import kushal as engineer_3d</span>
      </div>
      <nav class="nav-links">
        <a href="#terminal-deck">./terminal</a>
        <a href="#skills">./skills</a>
        <a href="#repos">./git-repos</a>
        <a href="#achievements">./changelog</a>
        <a href="#guestbook">./guestbook</a>
        <a class="btn btn-cyan" href="/api/export" download>Export Dev Dossier (.json)</a>
      </nav>
    </header>

    <!-- 3D HERO STAGE -->
    <section class="hero">
      <div class="card tilt-3d">
        <div class="eyebrow z-pop-1">3D Projection Engine • SQLite + Python Stdlib • 0 node_modules</div>
        <h1 class="z-pop-2">Hi, I'm <span class="gradient-name" id="dev-name">Kushal Singla</span></h1>
        <div class="subtitle z-pop-1" id="dev-role">B.Tech CS &amp; AI • Newton School of Technology × Rishihood University</div>
        <p class="intro-text z-pop-1" id="dev-intro">Loading developer runtime...</p>
        <div class="hero-actions z-pop-2">
          <a class="btn btn-cyan" id="gh-profile-link" href="https://github.com/__DEFAULT_GITHUB__" target="_blank" rel="noopener">GitHub Profile ↗</a>
          <button class="btn" id="audit-btn">⚡ Run 3D Dev Audit</button>
          <a class="btn" href="#repos">Explore Builds ↓</a>
        </div>
      </div>

      <!-- INTERACTIVE DRAGGABLE 3D HOLOGRAM CORE -->
      <div class="holo-stage tilt-3d">
        <div class="holo-top z-pop-1">
          <span>3D HOLOGRAM CORE // DRAG TO ROTATE</span>
          <span class="holo-badge" id="holo-mode-label">TESSERACT</span>
        </div>
        <canvas id="holo-canvas" title="Drag to spin in 3D space"></canvas>
        <div class="holo-controls z-pop-1">
          <div class="shape-btns" id="shape-btns">
            <button class="shape-btn active" data-shape="cube">Tesseract</button>
            <button class="shape-btn" data-shape="ico">Icosahedron</button>
            <button class="shape-btn" data-shape="torus">Torus</button>
            <button class="shape-btn" data-shape="helix">Python Helix</button>
          </div>
          <span style="font-family:var(--mono);font-size:0.7rem;color:var(--muted);">60 FPS Pure Math</span>
        </div>
      </div>
    </section>

    <!-- INTERACTIVE TERMINAL -->
    <section class="terminal" id="terminal-deck">
      <div class="term-header">
        <div class="term-dots">
          <span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
        </div>
        <span>kushal@nst — python3 portfolio.py (3D Engine Active)</span>
        <span>SQLite3 LIVE</span>
      </div>
      <div class="term-body" id="term-output"></div>
      <form class="term-input-row" id="term-form">
        <span class="term-prompt">kushal@nst:~$</span>
        <input class="term-input" id="term-input" type="text" placeholder="Type 'help', '3d torus', 'whoami', 'python', 'joke', 'sudo hire'..." autocomplete="off" />
      </form>
    </section>

    <!-- LIVE SQLITE + BACKEND TELEMETRY -->
    <section class="telemetry" aria-label="Live Monolith Telemetry">
      <div class="stat-box tilt-3d">
        <div class="stat-label z-pop-1">External Dependencies</div>
        <div class="stat-val z-pop-2">0 packages</div>
      </div>
      <div class="stat-box tilt-3d">
        <div class="stat-label z-pop-1">Single-File Size</div>
        <div class="stat-val z-pop-2" id="stat-lines">-- lines</div>
      </div>
      <div class="stat-box tilt-3d">
        <div class="stat-label z-pop-1">SQLite DB Footprints</div>
        <div class="stat-val z-pop-2" id="stat-db">-- KB</div>
      </div>
      <div class="stat-box tilt-3d">
        <div class="stat-label z-pop-1">API Latency</div>
        <div class="stat-val z-pop-2" id="stat-latency">-- ms</div>
      </div>
      <div class="stat-box tilt-3d">
        <div class="stat-label z-pop-1">Persistent Views</div>
        <div class="stat-val z-pop-2" id="stat-views">--</div>
      </div>
    </section>

    <!-- SKILLS -->
    <section id="skills">
      <div class="section-head">
        <h2 class="section-title"><span>01.</span> Core Stack &amp; Python Obsession</h2>
      </div>
      <div class="skills-grid" id="skills-grid"></div>
    </section>

    <!-- LIVE GITHUB REPOS -->
    <section id="repos">
      <div class="section-head">
        <h2 class="section-title"><span>02.</span> Git Repositories <span class="pill mint" id="repo-source-badge">syncing...</span></h2>
        <form class="repo-controls" id="repo-form">
          <input class="input" id="gh-user-input" value="__DEFAULT_GITHUB__" placeholder="GitHub username" />
          <button class="btn" type="submit">Fetch Live Repos</button>
        </form>
      </div>
      <div id="repo-notice" class="notice" style="display:none;"></div>
      <div class="grid-cards" id="repos-grid"></div>
    </section>

    <!-- ACHIEVEMENTS & OLD THINGS ARCHIVE -->
    <section id="achievements">
      <div class="section-head">
        <h2 class="section-title"><span>03.</span> Achievements, Builds &amp; The Archive</h2>
        <div class="filter-tabs" id="ach-filters">
          <button class="tab-btn active" data-filter="All">All</button>
          <button class="tab-btn" data-filter="Project">Projects</button>
          <button class="tab-btn" data-filter="Achievement">Achievements</button>
          <button class="tab-btn" data-filter="Archive">Archive / Old Things</button>
        </div>
      </div>
      <div class="grid-cards" id="ach-grid"></div>
    </section>

    <!-- LIVE SQLITE GUESTBOOK -->
    <section id="guestbook">
      <div class="section-head">
        <h2 class="section-title"><span>04.</span> Leave a Pull Request on My Wall (Live SQLite)</h2>
      </div>
      <div class="guestbook-wrap">
        <form class="card tilt-3d" id="gb-form">
          <div class="form-group z-pop-1">
            <label for="gb-author">Your Name / Handle</label>
            <input id="gb-author" required placeholder="e.g., Ada Lovelace" maxlength="60" />
          </div>
          <div class="form-group z-pop-1">
            <label for="gb-role">Title / Dev Class</label>
            <input id="gb-role" placeholder="e.g., Senior Bug Creator" maxlength="60" />
          </div>
          <div class="form-group z-pop-1">
            <label for="gb-msg">Commit Message</label>
            <textarea id="gb-msg" required placeholder="Drop a review, roast my code, or say hi..." maxlength="400"></textarea>
          </div>
          <button class="btn z-pop-2" type="submit">git push origin guestbook</button>
          <div id="gb-status" style="margin-top:10px;font-family:var(--mono);font-size:0.78rem;color:var(--mint);"></div>
        </form>

        <div class="card tilt-3d">
          <div class="gb-list z-pop-1" id="gb-list"></div>
        </div>
      </div>
    </section>

    <footer class="footer">
      <div>Built in 3D with pure Python, SQLite3 &amp; zero dependencies — Kushal Singla.</div>
      <div>Inspect live backend: <a href="/api/portfolio" target="_blank">/api/portfolio</a> • <a href="/api/export" target="_blank">/api/export</a></div>
    </footer>
  </div>

  <script>
    const state = {
      portfolio: null,
      filter: "All",
      mouseX: 0,
      mouseY: 0,
    };

    const JOKES = [
      "Why do Python programmers prefer dark mode? Because light attracts bugs (and ruins the 3D neon contrast).",
      "A SQL query walks into a bar, approaches two tables, and asks: 'Can I JOIN you?'",
      "I put SQLite, a backend server, and a 3D engine in one Python file. Microservices architects are currently shaking.",
      "My code doesn't have bugs; it just develops unexpected spontaneous 3D features in production.",
      "Python: the only language where forgetting 4 spaces feels like a personal betrayal."
    ];

    function esc(str) {
      return String(str ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    // =========================================================================
    // 1. TRUE CSS 3D CARD TILT & SPECULAR LIGHT TRACKING
    // =========================================================================
    function attachTilt3D(root = document) {
      const els = root.querySelectorAll(".tilt-3d");
      els.forEach((el) => {
        if (el.dataset.tiltBound) return;
        el.dataset.tiltBound = "1";
        el.addEventListener("mousemove", (e) => {
          const rect = el.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          const px = x / rect.width - 0.5;
          const py = y / rect.height - 0.5;
          const rotY = px * 14;
          const rotX = -py * 14;
          el.style.setProperty("--mx", `${x}px`);
          el.style.setProperty("--my", `${y}px`);
          el.style.transform = `perspective(1000px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) translateZ(8px)`;
        });
        el.addEventListener("mouseleave", () => {
          el.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)";
        });
      });
    }

    window.addEventListener("mousemove", (e) => {
      state.mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      state.mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    // =========================================================================
    // 2. FULL-VIEWPORT 3D STARFIELD & PERSPECTIVE CYBER FLOOR CANVAS
    // =========================================================================
    (function initSpace3D() {
      const canvas = document.getElementById("bg-3d");
      const ctx = canvas.getContext("2d");
      let w = 0, h = 0;

      function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        w = window.innerWidth;
        h = window.innerHeight;
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
      window.addEventListener("resize", resize);
      resize();

      const STAR_COUNT = 150;
      const stars = Array.from({ length: STAR_COUNT }, () => ({
        x: (Math.random() - 0.5) * 2200,
        y: (Math.random() - 0.5) * 1400,
        z: Math.random() * 1400 + 100,
        color: Math.random() > 0.45 ? "#00f5a0" : "#38bdf8",
      }));

      let gridOffset = 0;

      function draw() {
        ctx.clearRect(0, 0, w, h);

        // Deep space ambient glow
        const bgGrad = ctx.createRadialGradient(w * 0.5, h * 0.35, 20, w * 0.5, h * 0.5, Math.max(w, h) * 0.75);
        bgGrad.addColorStop(0, "rgba(12, 26, 48, 0.55)");
        bgGrad.addColorStop(1, "rgba(5, 8, 17, 1)");
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, w, h);

        const camX = state.mouseX * 90;
        const camY = state.mouseY * 55;
        const horizon = h * 0.62 - camY * 0.45;
        const cx = w * 0.5 - camX * 0.6;

        // 3D Perspective Cyber Floor
        gridOffset = (gridOffset + 0.9) % 60;
        ctx.lineWidth = 1;
        for (let z = 60; z < 1100; z += 60) {
          const depth = z - gridOffset;
          if (depth <= 10) continue;
          const scale = 340 / depth;
          const y = horizon + 180 * scale;
          if (y > h + 20) continue;
          const alpha = Math.max(0, Math.min(0.28, (1 - depth / 1100) * 0.35));
          ctx.strokeStyle = `rgba(56, 189, 248, ${alpha.toFixed(3)})`;
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(w, y);
          ctx.stroke();
        }

        for (let gx = -12; gx <= 12; gx++) {
          const xNear = cx + gx * 260;
          const xFar = cx + gx * 26;
          ctx.strokeStyle = "rgba(0, 245, 160, 0.11)";
          ctx.beginPath();
          ctx.moveTo(xFar, horizon);
          ctx.lineTo(xNear, h + 40);
          ctx.stroke();
        }

        // 3D Moving Stars
        for (const s of stars) {
          s.z -= 2.2;
          if (s.z <= 20) {
            s.x = (Math.random() - 0.5) * 2200;
            s.y = (Math.random() - 0.5) * 1400;
            s.z = 1400;
          }
          const scale = 360 / s.z;
          const sx = w * 0.5 + (s.x - camX * 1.4) * scale;
          const sy = h * 0.45 + (s.y - camY * 1.4) * scale;
          if (sx < -20 || sx > w + 20 || sy < -20 || sy > h + 20) continue;
          const r = Math.max(0.6, Math.min(3.2, scale * 2.8));
          const alpha = Math.max(0.1, Math.min(0.95, 1 - s.z / 1450));
          ctx.globalAlpha = alpha;
          ctx.fillStyle = s.color;
          ctx.beginPath();
          ctx.arc(sx, sy, r, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
        requestAnimationFrame(draw);
      }
      requestAnimationFrame(draw);
    })();

    // =========================================================================
    // 3. INTERACTIVE DRAGGABLE 3D HOLOGRAM CORE (PURE 3D PROJECTION ENGINE)
    // =========================================================================
    const HoloEngine = (function () {
      const canvas = document.getElementById("holo-canvas");
      const ctx = canvas.getContext("2d");
      let w = 0, h = 0;

      function resize() {
        const rect = canvas.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        w = Math.max(260, rect.width);
        h = Math.max(240, rect.height);
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
      window.addEventListener("resize", resize);

      // Build 3D Geometries
      function makeTesseract() {
        const verts = [];
        const edges = [];
        for (const s of [1.2, 0.58]) {
          for (const x of [-s, s]) {
            for (const y of [-s, s]) {
              for (const z of [-s, s]) {
                verts.push({ x, y, z });
              }
            }
          }
        }
        const cubePairs = [
          [0,1],[2,3],[4,5],[6,7],
          [0,2],[1,3],[4,6],[5,7],
          [0,4],[1,5],[2,6],[3,7]
        ];
        cubePairs.forEach(([a,b]) => edges.push([a, b]));
        cubePairs.forEach(([a,b]) => edges.push([a + 8, b + 8]));
        for (let i = 0; i < 8; i++) edges.push([i, i + 8]);
        return { verts, edges, label: "TESSERACT" };
      }

      function makeIcosahedron() {
        const t = (1 + Math.sqrt(5)) / 2;
        const raw = [
          [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
          [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
          [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]
        ];
        const verts = raw.map(([x, y, z]) => {
          const len = Math.hypot(x, y, z);
          return { x: (x / len) * 1.65, y: (y / len) * 1.65, z: (z / len) * 1.65 };
        });
        const edges = [];
        for (let i = 0; i < verts.length; i++) {
          for (let j = i + 1; j < verts.length; j++) {
            const d = Math.hypot(verts[i].x - verts[j].x, verts[i].y - verts[j].y, verts[i].z - verts[j].z);
            if (d < 1.85) edges.push([i, j]);
          }
        }
        return { verts, edges, label: "ICOSAHEDRON" };
      }

      function makeTorus() {
        const verts = [];
        const edges = [];
        const R = 1.25, r = 0.48;
        const segU = 18, segV = 9;
        for (let i = 0; i < segU; i++) {
          const u = (i / segU) * Math.PI * 2;
          for (let j = 0; j < segV; j++) {
            const v = (j / segV) * Math.PI * 2;
            verts.push({
              x: (R + r * Math.cos(v)) * Math.cos(u),
              y: r * Math.sin(v),
              z: (R + r * Math.cos(v)) * Math.sin(u),
            });
            const curr = i * segV + j;
            const nextU = ((i + 1) % segU) * segV + j;
            const nextV = i * segV + ((j + 1) % segV);
            edges.push([curr, nextU], [curr, nextV]);
          }
        }
        return { verts, edges, label: "TORUS FIELD" };
      }

      function makeHelix() {
        const verts = [];
        const edges = [];
        const steps = 24;
        for (let i = 0; i < steps; i++) {
          const t = (i / (steps - 1)) * Math.PI * 4;
          const y = ((i / (steps - 1)) - 0.5) * 3.1;
          verts.push({ x: Math.cos(t) * 0.95, y, z: Math.sin(t) * 0.95 });
          verts.push({ x: Math.cos(t + Math.PI) * 0.95, y, z: Math.sin(t + Math.PI) * 0.95 });
          const a = i * 2;
          const b = i * 2 + 1;
          if (i % 2 === 0) edges.push([a, b]);
          if (i > 0) {
            edges.push([a - 2, a], [b - 2, b]);
          }
        }
        return { verts, edges, label: "PYTHON HELIX" };
      }

      const shapes = {
        cube: makeTesseract(),
        ico: makeIcosahedron(),
        torus: makeTorus(),
        helix: makeHelix(),
      };

      const orbitTags = ["Python", "SQLite3", "AST", "AI/ML", "PageRank", "0 Deps"];

      let currentKey = "cube";
      let rotX = 0.45, rotY = 0.5;
      let velX = 0.005, velY = 0.011;
      let dragging = false;
      let lastX = 0, lastY = 0;

      canvas.addEventListener("pointerdown", (e) => {
        dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
        canvas.setPointerCapture(e.pointerId);
      });

      canvas.addEventListener("pointermove", (e) => {
        if (!dragging) return;
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        velY = dx * 0.012;
        velX = dy * 0.012;
        rotY += velY;
        rotX += velX;
      });

      canvas.addEventListener("pointerup", () => { dragging = false; });
      canvas.addEventListener("pointercancel", () => { dragging = false; });

      function setShape(key) {
        if (!shapes[key]) return false;
        currentKey = key;
        document.getElementById("holo-mode-label").textContent = shapes[key].label;
        document.querySelectorAll(".shape-btn").forEach((b) => {
          b.classList.toggle("active", b.dataset.shape === key);
        });
        return true;
      }

      function rotate(p, ax, ay) {
        const cosY = Math.cos(ay), sinY = Math.sin(ay);
        const x1 = p.x * cosY - p.z * sinY;
        const z1 = p.x * sinY + p.z * cosY;
        const cosX = Math.cos(ax), sinX = Math.sin(ax);
        const y2 = p.y * cosX - z1 * sinX;
        const z2 = p.y * sinX + z1 * cosX;
        return { x: x1, y: y2, z: z2 };
      }

      function frame(t) {
        if (!w) resize();
        ctx.clearRect(0, 0, w, h);

        if (!dragging) {
          rotX += velX;
          rotY += velY;
          velX += (0.0045 - velX) * 0.03;
          velY += (0.0105 - velY) * 0.03;
        }

        const shape = shapes[currentKey];
        const cx = w * 0.5;
        const cy = h * 0.5;
        const fov = Math.min(w, h) * 1.12;
        const camDist = 4.6;

        const projected = shape.verts.map((v) => {
          const r = rotate(v, rotX + state.mouseY * 0.2, rotY + state.mouseX * 0.2);
          const scale = fov / (camDist + r.z);
          return { x: cx + r.x * scale, y: cy + r.y * scale, z: r.z, scale };
        });

        // Sort edges back-to-front for crisp 3D depth shading
        const sortedEdges = shape.edges
          .map(([a, b]) => ({ a, b, z: (projected[a].z + projected[b].z) * 0.5 }))
          .sort((e1, e2) => e2.z - e1.z);

        for (const e of sortedEdges) {
          const p1 = projected[e.a];
          const p2 = projected[e.b];
          const depthNorm = Math.max(0, Math.min(1, (2.0 - e.z) / 3.8));
          const rCol = Math.round(56 * (1 - depthNorm));
          const gCol = Math.round(189 + (245 - 189) * depthNorm);
          const bCol = Math.round(248 + (160 - 248) * depthNorm);
          ctx.strokeStyle = `rgba(${rCol}, ${gCol}, ${bCol}, ${(0.22 + depthNorm * 0.72).toFixed(2)})`;
          ctx.lineWidth = 0.9 + depthNorm * 1.4;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }

        // Glowing 3D vertices
        for (const p of projected) {
          const depthNorm = Math.max(0, Math.min(1, (2.0 - p.z) / 3.8));
          const radius = 1.6 + depthNorm * 2.5;
          ctx.fillStyle = depthNorm > 0.5 ? "#00f5a0" : "#38bdf8";
          ctx.globalAlpha = 0.35 + depthNorm * 0.65;
          ctx.beginPath();
          ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
          ctx.fill();
        }

        // Orbiting 3D Skill Satellites
        ctx.font = "600 11px 'JetBrains Mono', monospace";
        orbitTags.forEach((label, idx) => {
          const angle = t * 0.00055 + (idx / orbitTags.length) * Math.PI * 2;
          const raw = {
            x: Math.cos(angle) * 2.15,
            y: Math.sin(angle * 1.5) * 0.72,
            z: Math.sin(angle) * 2.15,
          };
          const r = rotate(raw, rotX * 0.35, rotY * 0.35);
          const scale = fov / (camDist + r.z);
          const sx = cx + r.x * scale;
          const sy = cy + r.y * scale;
          const alpha = Math.max(0.22, Math.min(0.95, (2.2 - r.z) / 3.6));
          ctx.globalAlpha = alpha;
          ctx.fillStyle = idx % 2 === 0 ? "#00f5a0" : "#fbbf24";
          ctx.fillText(label, sx - 18, sy);
        });
        ctx.globalAlpha = 1;

        requestAnimationFrame(frame);
      }

      setTimeout(() => { resize(); requestAnimationFrame(frame); }, 30);
      return { setShape };
    })();

    // =========================================================================
    // 4. TERMINAL & PORTFOLIO DATA LOGIC
    // =========================================================================
    function printTerm(htmlLine) {
      const box = document.getElementById("term-output");
      const div = document.createElement("div");
      div.className = "term-line";
      div.innerHTML = htmlLine;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }

    function runCommand(raw) {
      const cmd = raw.trim().toLowerCase();
      if (!cmd) return;
      printTerm(`<span class="term-cmd">kushal@nst:~$</span> ${esc(raw)}`);

      if (cmd === "help") {
        printTerm(
          `<span class="term-cyan">Available commands:</span>\n` +
          `  3d [cube|ico|torus|helix] -> Morph the live 3D hologram\n` +
          `  whoami                    -> Brief developer bio\n` +
          `  python                    -> Execute Zen of Kushal\n` +
          `  skills                    -> List technical arsenal\n` +
          `  achievements              -> Dump SQLite achievements table\n` +
          `  audit                     -> Inspect single-file 3D architecture metrics\n` +
          `  joke                      -> Fetch certified developer humor\n` +
          `  sudo hire                 -> Attempt privilege escalation\n` +
          `  export                    -> Download full JSON dev dossier\n` +
          `  clear                     -> Wipe terminal output`
        );
      } else if (cmd.startsWith("3d")) {
        const arg = cmd.split(/\s+/)[1] || "torus";
        if (HoloEngine.setShape(arg)) {
          printTerm(`<span class="term-cmd">3D Hologram morphed -> ${esc(arg.toUpperCase())}</span> (Drag the hologram above to spin!)`);
        } else {
          printTerm(`<span class="term-warn">Usage: 3d cube | 3d ico | 3d torus | 3d helix</span>`);
        }
      } else if (cmd === "whoami") {
        const p = state.portfolio?.profile;
        printTerm(
          `<span class="term-cmd">${esc(p?.name)}</span> — ${esc(p?.role)}\n` +
          `${esc(p?.institution)}\nCore Language: <span class="term-warn">${esc(p?.core_language)}</span>`
        );
      } else if (cmd === "python") {
        printTerm(
          `<span class="term-cyan">Python 3.x (Kushal 3D Edition)</span>\n` +
          `>>> import antigravity\n` +
          `>>> print("Readability counts. So does shipping in 3D.")\n` +
          `<span class="term-cmd">Readability counts. So does shipping in 3D.</span>`
        );
      } else if (cmd === "skills") {
        const list = (state.portfolio?.profile?.skills || [])
          .map(s => `  [${s.level}%] ${s.name}`)
          .join("\n");
        printTerm(esc(list));
      } else if (cmd === "achievements") {
        const list = (state.portfolio?.achievements || [])
          .map(a => `  • (${a.period}) ${a.title}`)
          .join("\n");
        printTerm(esc(list));
      } else if (cmd === "audit") {
        const m = state.portfolio?.metrics || {};
        printTerm(
          `<span class="term-cyan">[ARCHITECTURAL VERDICT: EXTRAORDINARY 3D]</span>\n` +
          `  File Count     : 1 (portfolio.py)\n` +
          `  Dependencies   : 0 external packages\n` +
          `  3D Renderer    : Pure JS Perspective Projection + CSS preserve-3d\n` +
          `  Code Length    : ${esc(m.single_file_lines)} lines\n` +
          `  SQLite DB Size : ${esc(m.db_size_kb)} KB\n` +
          `  API Latency    : ${esc(state.portfolio?.latency_ms)} ms\n` +
          `  Server Uptime  : ${esc(m.uptime_seconds)}s`
        );
      } else if (cmd === "joke") {
        const j = JOKES[Math.floor(Math.random() * JOKES.length)];
        printTerm(`<span class="term-warn">${esc(j)}</span>`);
      } else if (cmd.startsWith("sudo hire")) {
        printTerm(
          `<span class="term-cmd">ACCESS GRANTED.</span> Initiating offer letter protocol...\n` +
          `Kushal runs on clean Python, crisp 3D UI, and zero bloat. Reach out via GitHub or Export Dossier!`
        );
      } else if (cmd === "export") {
        printTerm(`<span class="term-cyan">Downloading kushal_singla_dev_dossier.json...</span>`);
        window.location.href = "/api/export";
      } else if (cmd === "clear") {
        document.getElementById("term-output").innerHTML = "";
      } else {
        printTerm(`<span class="term-coral">bash: ${esc(cmd)}: command not found.</span> Type 'help' to see valid commands.`);
      }
    }

    function renderAchievements() {
      const grid = document.getElementById("ach-grid");
      const items = (state.portfolio?.achievements || []).filter(
        a => state.filter === "All" || a.category === state.filter
      );
      grid.innerHTML = items.map(a => `
        <article class="ach-card tilt-3d">
          <div class="z-pop-1">
            <div class="meta-row" style="margin-bottom:8px;">
              <span class="pill ${a.category === 'Achievement' ? 'amber' : 'mint'}">${esc(a.category)}</span>
              <span>${esc(a.period)}</span>
            </div>
            <h3 style="font-size:1.06rem;margin-bottom:8px;">${esc(a.title)}</h3>
            <p class="ach-desc">${esc(a.description)}</p>
          </div>
          <div class="z-pop-1" style="display:flex;flex-wrap:wrap;gap:6px;">
            ${a.tags.map(t => `<span class="pill">${esc(t)}</span>`).join("")}
          </div>
        </article>
      `).join("");
      attachTilt3D(grid);
    }

    async function loadPortfolio() {
      const res = await fetch("/api/portfolio");
      const data = await res.json();
      state.portfolio = data;

      document.getElementById("dev-name").textContent = data.profile.name;
      document.getElementById("dev-role").textContent = `${data.profile.role} • ${data.profile.institution}`;
      document.getElementById("dev-intro").textContent = data.profile.intro;

      document.getElementById("stat-lines").textContent = `${data.metrics.single_file_lines} lines`;
      document.getElementById("stat-db").textContent = `${data.metrics.db_size_kb} KB`;
      document.getElementById("stat-latency").textContent = `${data.latency_ms} ms`;
      document.getElementById("stat-views").textContent = data.metrics.page_views;

      const skillsGrid = document.getElementById("skills-grid");
      skillsGrid.innerHTML = data.profile.skills.map(s => `
        <div class="skill-item tilt-3d">
          <div class="skill-top z-pop-1">
            <strong>${esc(s.name)}</strong>
            <span class="skill-tag">${esc(s.tag)} • ${esc(s.level)}%</span>
          </div>
          <div class="bar-track z-pop-1">
            <div class="bar-fill" style="width:${Number(s.level)}%"></div>
          </div>
        </div>
      `).join("");
      attachTilt3D(skillsGrid);

      renderAchievements();
    }

    async function loadRepos(username) {
      const badge = document.getElementById("repo-source-badge");
      const notice = document.getElementById("repo-notice");
      const grid = document.getElementById("repos-grid");
      badge.textContent = "fetching...";

      const res = await fetch(`/api/repos?user=${encodeURIComponent(username)}`);
      const data = await res.json();

      badge.textContent = data.source === "github_live"
        ? `LIVE GitHub (${data.latency_ms}ms)`
        : data.source === "sqlite_cache"
          ? `SQLite Cache (${data.latency_ms}ms)`
          : "Featured Showcase";

      if (data.note) {
        notice.style.display = "block";
        notice.textContent = `⚠ ${data.note}`;
      } else {
        notice.style.display = "none";
      }

      document.getElementById("gh-profile-link").href = `https://github.com/${encodeURIComponent(data.username)}`;

      grid.innerHTML = data.repos.map(r => `
        <a class="repo-card tilt-3d" href="${esc(r.html_url)}" target="_blank" rel="noopener">
          <div class="z-pop-1">
            <div class="repo-name">${esc(r.name)} ↗</div>
            <p class="repo-desc" style="margin-top:8px;">${esc(r.description)}</p>
          </div>
          <div class="meta-row z-pop-1">
            <span class="pill">${esc(r.language)}</span>
            <span>★ ${esc(r.stargazers_count)} &nbsp; ⑂ ${esc(r.forks_count)}</span>
          </div>
        </a>
      `).join("");
      attachTilt3D(grid);
    }

    async function loadGuestbook() {
      const res = await fetch("/api/guestbook");
      const data = await res.json();
      const list = document.getElementById("gb-list");
      list.innerHTML = data.entries.map(e => `
        <div class="gb-item">
          <div class="gb-head">
            <span><span class="gb-author">${esc(e.author)}</span> <span style="color:var(--cyan);">(${esc(e.role)})</span></span>
            <span class="gb-time">${esc(e.created_at)}</span>
          </div>
          <div style="font-size:0.9rem;color:#e2e8f0;">${esc(e.message)}</div>
        </div>
      `).join("");
    }

    // Event Listeners
    document.getElementById("shape-btns").addEventListener("click", (e) => {
      if (!e.target.matches(".shape-btn")) return;
      HoloEngine.setShape(e.target.dataset.shape);
    });

    document.getElementById("term-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const input = document.getElementById("term-input");
      runCommand(input.value);
      input.value = "";
    });

    document.getElementById("audit-btn").addEventListener("click", () => {
      runCommand("audit");
      document.getElementById("terminal-deck").scrollIntoView({ behavior: "smooth" });
      document.getElementById("term-input").focus();
    });

    document.getElementById("repo-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const u = document.getElementById("gh-user-input").value.trim();
      if (u) loadRepos(u);
    });

    document.getElementById("ach-filters").addEventListener("click", (e) => {
      if (!e.target.matches(".tab-btn")) return;
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      state.filter = e.target.dataset.filter;
      renderAchievements();
    });

    document.getElementById("gb-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const status = document.getElementById("gb-status");
      status.textContent = "Committing to SQLite...";
      const payload = {
        author: document.getElementById("gb-author").value,
        role: document.getElementById("gb-role").value,
        message: document.getElementById("gb-msg").value,
      };
      const res = await fetch("/api/guestbook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        status.textContent = "✓ Merged into kushal_portfolio.db!";
        document.getElementById("gb-form").reset();
        loadGuestbook();
      } else {
        status.textContent = "✗ Merge conflict: check your inputs.";
      }
    });

    // Boot Sequence
    (async function boot() {
      attachTilt3D(document);
      printTerm(`<span class="term-cyan">Booting Kushal Singla 3D Single-File Full-Stack Monolith...</span>`);
      printTerm(`3D Projection Engine online. SQLite3 mounted. Type <span class="term-cmd">'help'</span> or <span class="term-cmd">'3d torus'</span>.`);
      await loadPortfolio();
      loadRepos(document.getElementById("gh-user-input").value);
      loadGuestbook();
    })();
  </script>
</body>
</html>
"""


# ==============================================================================
# ENTRYPOINT
# ==============================================================================
def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    print("=" * 64)
    print("  Kushal Singla — 3D Single-File Full-Stack Portfolio LIVE")
    print(f"  URL      : http://{HOST}:{PORT}")
    print(f"  Database : {DB_PATH}")
    print(f"  Export   : http://{HOST}:{PORT}/api/export")
    print("  Press Ctrl+C to shut down.")
    print("=" * 64)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down cleanly. Stay Pythonic.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
