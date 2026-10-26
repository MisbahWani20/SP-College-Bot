import hashlib
import re
from collections import deque
from urllib.parse import urldefrag, urlparse
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

DATABASE_NAME = "spcollege_data.db"

ANNOUNCEMENT_URL = (
    "https://spcollege.edu.in/Main/List.aspx"
    "?SubType=Announcement&Type=Alert"
)

BASE_URL = "https://spcollege.edu.in/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def create_sp_website_table():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sp_college_website_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                title TEXT NOT NULL,
                item_date TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(item_type, title, url)
            )
        """)


def normalize_date(date_text):
    date_text = date_text.strip()

    for date_format in (
        "%d-%m-%Y",
        "%d-%B-%Y",
        "%d-%b-%Y",
        "%d-%m-%y",
    ):
        try:
            return datetime.strptime(
                date_text, date_format
            ).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def fetch_sp_announcements():
    response = requests.get(
        ANNOUNCEMENT_URL,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    items = []

    # The page displays each announcement as a list item.
    for element in soup.find_all(["li", "tr"]):
        text = element.get_text(" ", strip=True)

        if not text or "dated:" not in text.lower():
            continue

        link = element.find("a", href=True)
        if not link:
            continue

        title = link.get_text(" ", strip=True)
        if not title:
            continue

        # Extract the publication date displayed after "Dated:"
        import re
        match = re.search(
            r"Dated:\s*(\d{1,2}[-/][A-Za-z0-9-]+[-/]\d{2,4})",
            text,
            re.IGNORECASE
        )

        item_date = None
        if match:
            raw_date = match.group(1).replace("/", "-")
            item_date = normalize_date(raw_date)
        url = urljoin(ANNOUNCEMENT_URL, link["href"])
        items.append((
            "notification",
            title,
            item_date,
            url
        ))
    if not items:
        raise RuntimeError(
            "No dated announcement links were found. "
            "Existing database records were left unchanged."
        )
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.executemany("""
            INSERT INTO sp_college_website_items
                (item_type, title, item_date, url)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item_type, title, url)
            DO UPDATE SET item_date = excluded.item_date
        """, items)
    return len(items)


def create_sp_pages_table():
    """Store text collected from SP College website pages."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sp_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                source_type TEXT,
                content TEXT,
                content_hash TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sp_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT,
                chunk_index INTEGER,
                chunk_text TEXT,
                chunk_hash TEXT
            )
        """)


def normalize_page_url(url):
    """Normalize a URL and reject pages outside the college website."""
    url = urldefrag(url)[0]
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if parsed.netloc.lower() not in (
        "spcollege.edu.in",
        "www.spcollege.edu.in"
    ):
        return None

    path = parsed.path.lower()

    excluded_extensions = (
        ".pdf", ".jpg", ".jpeg", ".png", ".gif",
        ".webp", ".svg", ".css", ".js", ".zip",
        ".doc", ".docx", ".xls", ".xlsx", ".mp4"
    )

    if path.endswith(excluded_extensions):
        return None

    if "/admin/" in path:
        return None

    if any(term in parsed.query.lower() for term in (
        "logout", "signout", "delete=", "edit="
    )):
        return None

    # Keep query parameters because ASP.NET pages use them
    # to identify different departments and website sections.
    return url


def split_page_into_chunks(content, max_length=1200):
    """Split page text into searchable pieces."""
    paragraphs = [
        p.strip()
        for p in re.split(r"\n+", content)
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        while len(paragraph) > max_length:
            if current:
                chunks.append(current)
                current = ""

            chunks.append(paragraph[:max_length])
            paragraph = paragraph[max_length:]

        if not paragraph:
            continue

        if len(current) + len(paragraph) + 1 > max_length:
            if current:
                chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n{paragraph}" if current else paragraph

    if current:
        chunks.append(current)

    return chunks


def crawl_sp_website(max_pages=250, max_depth=3):
    """
    Crawl internal SP College pages, including department pages
    and their linked faculty, notices, syllabus and contact pages.
    """
    start_urls = [
        BASE_URL,
        urljoin(BASE_URL, "Main/Default.aspx"),
        urljoin(BASE_URL, "Main/ViewPage.aspx?Page=test"),
        urljoin(BASE_URL, "Main/PeopleList.aspx"),
        urljoin(BASE_URL, "Main/CourseList.aspx"),
    ]

    queue = deque()

    for url in start_urls:
        normalized = normalize_page_url(url)
        if normalized:
            queue.append((normalized, 0))

    visited = set()
    saved_count = 0

    with requests.Session() as session:
        session.headers.update(HEADERS)

        while queue and len(visited) < max_pages:
            url, depth = queue.popleft()

            if url in visited:
                continue

            visited.add(url)

            try:
                response = session.get(url, timeout=20)
                response.raise_for_status()

                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if "text/html" not in content_type:
                    continue

                soup = BeautifulSoup(response.text, "lxml")

                # Remove navigation and scripts so the saved content
                # focuses on information from the page itself.
                for element in soup.find_all([
                    "script", "style", "noscript", "svg"
                ]):
                    element.decompose()

                title = (
                    soup.title.get_text(" ", strip=True)
                    if soup.title else url
                )

                content = soup.get_text("\n", strip=True)
                content = re.sub(r"\n{3,}", "\n\n", content).strip()

                if not content:
                    continue

                content_hash = hashlib.sha256(
                    content.encode("utf-8")
                ).hexdigest()

                with sqlite3.connect(DATABASE_NAME) as conn:
                    conn.execute("""
                        INSERT INTO sp_pages
                            (url, title, source_type, content, content_hash,
                             fetched_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(url) DO UPDATE SET
                            title = excluded.title,
                            source_type = excluded.source_type,
                            content = excluded.content,
                            content_hash = excluded.content_hash,
                            fetched_at = CURRENT_TIMESTAMP
                    """, (
                        url,
                        title,
                        "website_page",
                        content,
                        content_hash
                    ))

                    # Refresh searchable chunks for this page.
                    conn.execute(
                        "DELETE FROM sp_chunks WHERE source_url = ?",
                        (url,)
                    )

                    chunks = split_page_into_chunks(content)

                    for index, chunk in enumerate(chunks):
                        chunk_hash = hashlib.sha256(
                            chunk.encode("utf-8")
                        ).hexdigest()

                        conn.execute("""
                            INSERT INTO sp_chunks
                                (source_url, chunk_index, chunk_text,
                                 chunk_hash)
                            VALUES (?, ?, ?, ?)
                        """, (url, index, chunk, chunk_hash))

                saved_count += 1
                print(f"[{saved_count}] Saved: {title}")

                # Follow links to subpages, but stop at the depth limit.
                if depth < max_depth:
                    for link_tag in soup.find_all("a", href=True):
                        next_url = normalize_page_url(
                            urljoin(response.url, link_tag["href"])
                        )

                        if (
                            next_url
                            and next_url not in visited
                        ):
                            queue.append((next_url, depth + 1))

            except requests.RequestException as error:
                print(f"Could not fetch {url}: {error}")

    print(f"\nSP College website pages saved: {saved_count}")
    return saved_count

if __name__ == "__main__":
    create_sp_website_table()
    create_sp_pages_table()
    count = fetch_sp_announcements()
    print("SP College announcements imported:", count)
    crawl_sp_website(max_pages=250, max_depth=3)
