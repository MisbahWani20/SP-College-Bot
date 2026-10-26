"""Print a quick report for spcollege_data.db without modifying it."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "spcollege_data.db"

if not DB.exists():
    raise SystemExit(f"Database not found: {DB}\nRun: python crawler/sp_college_pipeline.py --init-only")

with sqlite3.connect(DB) as conn:
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {"sp_pages", "sp_chunks"}
    if not required.issubset(tables):
        raise SystemExit(f"Missing tables. Found: {sorted(tables)}")

    total_pages = conn.execute("SELECT COUNT(*) FROM sp_pages").fetchone()[0]
    html_pages = conn.execute("SELECT COUNT(*) FROM sp_pages WHERE source_type='html'").fetchone()[0]
    pdf_pages = conn.execute("SELECT COUNT(*) FROM sp_pages WHERE source_type='pdf'").fetchone()[0]
    chunks = conn.execute("SELECT COUNT(*) FROM sp_chunks").fetchone()[0]
    duplicate_urls = conn.execute("SELECT COUNT(*) FROM (SELECT url FROM sp_pages GROUP BY url HAVING COUNT(*) > 1)").fetchone()[0]
    duplicate_chunks = conn.execute("SELECT COUNT(*) FROM (SELECT source_url, chunk_index FROM sp_chunks GROUP BY source_url, chunk_index HAVING COUNT(*) > 1)").fetchone()[0]

    print(f"Database: {DB}")
    print(f"Pages: {total_pages} (HTML: {html_pages}, PDF: {pdf_pages})")
    print(f"Chunks: {chunks}")
    print(f"Duplicate page URLs: {duplicate_urls}")
    print(f"Duplicate chunk indexes: {duplicate_chunks}")
    print("\nSample saved sources:")
    for title, kind, url, length in conn.execute(
        "SELECT title, source_type, url, length(content) FROM sp_pages ORDER BY id DESC LIMIT 10"
    ):
        print(f"- [{kind}] {title[:70]} | {length} chars | {url}")

    print("\nSample chunks:")
    for url, idx, text in conn.execute(
        "SELECT source_url, chunk_index, chunk_text FROM sp_chunks ORDER BY id LIMIT 3"
    ):
        print(f"- {url} [chunk {idx}]: {text[:180]}...")
