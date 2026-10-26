"""Collect readable content from the official SP College website into an isolated SQLite DB.

This script does NOT modify chatbot/faq.db, chatbot/knowledge.db, or chatbot.db.
Run from the project root:
    python crawler/sp_college_pipeline.py --init-only
    python crawler/sp_college_pipeline.py --max-pages 100
"""
from __future__ import annotations

import argparse
import hashlib
import io
import logging
import re
import sqlite3
import time
from contextlib import closing
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "spcollege_data.db"
START_URL = "https://spcollege.edu.in/Main/Default.aspx"
ALLOWED_HOSTS = {"spcollege.edu.in", "www.spcollege.edu.in"}
USER_AGENT = "SPCollegeStudentInfoBot/1.0 (educational project; polite crawler)"
REQUEST_TIMEOUT = 20
MAX_PDF_BYTES = 30 * 1024 * 1024
DELAY_SECONDS = 0.6

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".ico",
    ".css", ".js", ".mjs", ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".rar", ".7z", ".mp4", ".mp3", ".avi", ".mov", ".xlsx",
    ".xls", ".doc", ".docx", ".ppt", ".pptx", ".exe", ".dmg",
}
SKIP_PATH_PARTS = ("/logout", "/log-out", "/signin", "/sign-in", "/login", "/admin")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def canonicalize(url: str) -> str | None:
    """Normalize a URL and allow only the official SP College host."""
    url, _fragment = urldefrag(url.strip())
    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        return None
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        return None
    if parsed.username or parsed.password:
        return None
    path = parsed.path or "/"
    ext = Path(path.lower()).suffix
    if ext in SKIP_EXTENSIONS:
        return None
    lowered_path = path.lower()
    if any(part in lowered_path for part in SKIP_PATH_PARTS):
        return None
    # Remove common tracking parameters but preserve functional ASP.NET query strings.
    if parsed.query:
        kept = []
        for item in parsed.query.split("&"):
            key = item.split("=", 1)[0].lower()
            if key not in {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}:
                kept.append(item)
        query = "&".join(kept)
    else:
        query = ""
    # Use HTTPS and remove the default port. Preserve query parameters because ASP.NET
    # pages often use them to identify specific official content.
    return urlunparse(("https", host, path, "", query, ""))



def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.5",
    })
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return session



def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_database() -> None:
    """Create isolated SP College tables; never touch the legacy chatbot databases."""
    with closing(connect_db()) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sp_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL CHECK(source_type IN ('html', 'pdf')),
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sp_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_hash TEXT NOT NULL,
            FOREIGN KEY(source_url) REFERENCES sp_pages(url) ON DELETE CASCADE,
            UNIQUE(source_url, chunk_index)
        );
        CREATE INDEX IF NOT EXISTS idx_sp_chunks_source_url ON sp_chunks(source_url);
        CREATE INDEX IF NOT EXISTS idx_sp_pages_source_type ON sp_pages(source_type);
        CREATE INDEX IF NOT EXISTS idx_sp_pages_title ON sp_pages(title);
        """)
        conn.commit()
    logging.info("SP database ready: %s", DB_PATH)


def split_chunks(text: str, words_per_chunk: int = 180, overlap: int = 25) -> list[str]:
    """Split readable text into overlapping chunks; skip tiny/noisy fragments."""
    text = re.sub(r"[ \t]+", " ", text)
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in text.splitlines()]
    clean = "\n".join(p for p in paragraphs if p)
    words = clean.split()
    if not words:
        return []
    chunks = []
    step = max(1, words_per_chunk - overlap)
    for start in range(0, len(words), step):
        part = " ".join(words[start:start + words_per_chunk]).strip()
        if len(part) >= 80:
            chunks.append(part)
        if start + words_per_chunk >= len(words):
            break
    return chunks


def save_page(url: str, title: str, source_type: str, content: str) -> bool:
    """Upsert a page; only rebuild chunks when its text actually changes."""
    content = re.sub(r"\x00", "", content).strip()
    if len(content) < 80:
        logging.info("Skip nearly-empty content: %s", url)
        return False
    digest = sha256(content)
    with closing(connect_db()) as conn:
        old = conn.execute("SELECT content_hash FROM sp_pages WHERE url = ?", (url,)).fetchone()
        if old and old[0] == digest:
            logging.info("Unchanged: %s", url)
            return False
        conn.execute("""
            INSERT INTO sp_pages(url, title, source_type, content, content_hash, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title=excluded.title,
                source_type=excluded.source_type,
                content=excluded.content,
                content_hash=excluded.content_hash,
                fetched_at=excluded.fetched_at
        """, (url, title[:500], source_type, content, digest, now_utc()))
        # Delete and rebuild only this URL's chunks to avoid duplicates/stale text.
        conn.execute("DELETE FROM sp_chunks WHERE source_url = ?", (url,))
        chunks = split_chunks(content)
        for index, chunk in enumerate(chunks, start=1):
            conn.execute("""
                INSERT INTO sp_chunks(source_url, chunk_index, chunk_text, chunk_hash)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(source_url, chunk_index) DO UPDATE SET
                    chunk_text=excluded.chunk_text,
                    chunk_hash=excluded.chunk_hash
            """, (url, index, chunk, sha256(chunk)))
        conn.commit()
    logging.info("Saved %s (%s chunks): %s", source_type, len(chunks), title)
    return True



def html_to_text(html: str, url: str) -> tuple[str, str, list[str]]:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(" ", strip=True) if soup.title else url

    # Remove scripts and other elements that are not useful text
    for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe"]):
        tag.decompose()

    content_root = soup.body or soup
    text = content_root.get_text(separator="\n", strip=True)
    
    # Clean up excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # Collect page links
    links = []
    for a in soup.find_all("a", href=True):
        candidate = canonicalize(urljoin(url, a["href"]))
        if candidate:
            links.append(candidate)

    return title, text, links


def pdf_to_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data), strict=False)
    pages = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            logging.warning("Could not extract a PDF page: %s", exc)
            page_text = ""
        if page_text.strip():
            pages.append(page_text.strip())
    return "\n\n".join(pages)


def load_robots(session: requests.Session) -> RobotFileParser:
    robots_url = "https://spcollege.edu.in/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        response = session.get(robots_url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            parser.parse(response.text.splitlines())
        else:
            logging.warning("robots.txt returned HTTP %s; check site policy before crawling.", response.status_code)
            parser.parse([])
    except requests.RequestException as exc:
        logging.warning("Could not read robots.txt (%s). Check the site's access policy before proceeding.", exc)
        parser.parse([])
    return parser


def get_title_from_pdf_url(url: str) -> str:
    name = Path(urlparse(url).path).name or "Official SP College PDF"
    return re.sub(r"[_-]+", " ", name)


def crawl(max_pages: int, max_pdfs: int) -> None:
    init_database()
    session = make_session()
    robots = load_robots(session)
    queue = deque([START_URL])
    queued = {START_URL}
    visited: set[str] = set()
    pdf_count = 0

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        if not robots.can_fetch(USER_AGENT, url):
            logging.info("Blocked by robots.txt: %s", url)
            continue
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True, stream=False)
            response.raise_for_status()
            final_url = canonicalize(response.url)
            if not final_url:
                logging.info("Skip redirect outside official domain: %s", response.url)
                continue
            content_type = response.headers.get("Content-Type", "").lower()
            path_lower = urlparse(final_url).path.lower()
            looks_pdf = "application/pdf" in content_type or path_lower.endswith(".pdf")

            if looks_pdf:
                if pdf_count >= max_pdfs:
                    logging.info("PDF limit reached; skip: %s", final_url)
                    continue
                if len(response.content) > MAX_PDF_BYTES:
                    logging.warning("PDF too large; skip: %s", final_url)
                    continue
                # Verify actual PDF bytes before parsing. This avoids treating HTML error pages as PDFs.
                if not response.content.startswith(b"%PDF"):
                    logging.warning("PDF URL did not return PDF bytes; skip: %s", final_url)
                    continue
                try:
                    text = pdf_to_text(response.content)
                except Exception as exc:
                    logging.warning("PDF extraction failed for %s: %s", final_url, exc)
                    continue
                title = get_title_from_pdf_url(final_url)
                if text.strip():
                    save_page(final_url, title, "pdf", text)
                else:
                    logging.warning("No selectable text found in PDF (possibly scanned): %s", final_url)
                pdf_count += 1
                time.sleep(DELAY_SECONDS)
                continue

            if "text/html" not in content_type and not content_type.startswith("application/xhtml+xml"):
                logging.info("Skip non-HTML/non-PDF content (%s): %s", content_type or "unknown", final_url)
                continue
            print(response.text[:1500])
            title, text, links = html_to_text(response.text, final_url)
            print("DEBUG:", response.status_code, response.url)
            print("DEBUG:", title, "| extracted characters:", len(text), "| links:", len(links))
            if text.strip():
                save_page(final_url, title, "html", text)
            else:
                logging.info("No readable text: %s", final_url)

            for link in links:
                if link not in queued and link not in visited:
                    queued.add(link)
                    queue.append(link)

        except requests.RequestException as exc:
            logging.warning("Request failed for %s: %s", url, exc)
        except Exception as exc:
            logging.exception("Unexpected error on %s: %s", url, exc)
        finally:
            time.sleep(DELAY_SECONDS)

    with closing(connect_db()) as conn:
        pages = conn.execute("SELECT COUNT(*) FROM sp_pages").fetchone()[0]
        chunks = conn.execute("SELECT COUNT(*) FROM sp_chunks").fetchone()[0]
        html_pages = conn.execute("SELECT COUNT(*) FROM sp_pages WHERE source_type='html'").fetchone()[0]
        pdf_pages = conn.execute("SELECT COUNT(*) FROM sp_pages WHERE source_type='pdf'").fetchone()[0]
    logging.info("Crawl finished. Visited=%d; saved pages=%d (HTML=%d, PDF=%d); chunks=%d; database=%s",
                 len(visited), pages, html_pages, pdf_pages, chunks, DB_PATH)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect official SP College HTML and PDF text into a separate SQLite database.")
    parser.add_argument("--init-only", action="store_true", help="Create the isolated SP College tables without making web requests.")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum URLs to visit, including PDFs (default: 100).")
    parser.add_argument("--max-pdfs", type=int, default=40, help="Maximum PDFs to process (default: 40).")
    args = parser.parse_args()
    if args.max_pages < 1 or args.max_pdfs < 0:
        parser.error("--max-pages must be >= 1 and --max-pdfs must be >= 0")
    init_database()
    if args.init_only:
        logging.info("Schema test complete. No website requests were made.")
        return
    crawl(max_pages=args.max_pages, max_pdfs=args.max_pdfs)


if __name__ == "__main__":
    main()
