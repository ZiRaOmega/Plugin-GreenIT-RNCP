#!/usr/bin/env python3
"""Serveur de démonstration : statique + API SQLite, volontairement perfectible."""
from __future__ import annotations

import argparse
import json
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
WEB = ROOT.parent / "web"
DB = ROOT / "emargement.db"
# Aucun secret réel n’est présent dans cette démo publique.


def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as con:
        con.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))
        con.commit()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/emargement":
            name = parse_qs(parsed.query).get("name", [""])[0][:80]
            with sqlite3.connect(DB) as con:
                con.execute("INSERT INTO presences(name, created_at) VALUES (?, datetime('now'))", (name,))
                con.commit()
            self.respond({"ok": True})
            return
        if parsed.path == "/api/consultation":
            with sqlite3.connect(DB) as con:
                cur = con.execute("SELECT * FROM presences ORDER BY id DESC LIMIT 50")
                rows = [{"id": r[0], "name": r[1], "created_at": r[2]} for r in cur.fetchall()]
            self.respond({"rows": rows})
            return
        super().do_GET()

    def respond(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--db", type=Path, default=DB)
    args = ap.parse_args()
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"http://127.0.0.1:{args.port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
