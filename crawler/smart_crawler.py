import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

from config import WEBSITES
from extractor import extract_text
from chunker import split_into_chunks
from chatbot.database import insert_web_chunk
from chatbot.database import insert_web_knowledge,insert_web_chunk

SAVE_FOLDER = os.path.join(BASE_DIR, "data", "raw")

os.makedirs(SAVE_FOLDER, exist_ok=True)

KEYWORDS = [
    "department",
    "course",
    "programme",
    "program",
    "admission",
    "academic",
    "faculty",
    "library",
    "notification",
    "notice",
    "scholarship",
    "student",
    "facility",
    "exam",
    "iqac",
    "about",
    "contact"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}


for website in WEBSITES:

    print("=" * 60)
    print("Crawling:", website["name"])

    visited = set()

    combined_text = ""

    try:

        response = requests.get(
            website["url"],
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(response.text, "lxml")

        domain = urlparse(website["url"]).netloc

        links = set()

        for a in soup.find_all("a", href=True):

            full_url = urljoin(
                website["url"],
                a["href"]
            )

            if urlparse(full_url).netloc != domain:
                continue

            url_lower = full_url.lower()

            if any(word in url_lower for word in KEYWORDS):

                links.add(full_url)

        links.add(website["url"])

        print("Pages Found:", len(links))

        for link in links:

            if link in visited:
                continue

            visited.add(link)

            try:

                page = requests.get(
                    link,
                    headers=headers,
                    timeout=20
                )

                text = extract_text(page.text)
                title = BeautifulSoup(
                    page.text,
                   "lxml"
                ).title
                if title:
                 page_title = title.text.strip()
                else:
                 page_title = "No Title"
                insert_web_knowledge(
                  website["name"],
                 page_title,
                 link,
                 text
                )

                chunks = split_into_chunks(text)
                for index, chunk in enumerate(chunks):
                 insert_web_chunk(
                   website["name"],
                   page_title,
                   link,
                   index + 1,
                   chunk

                 )

                combined_text += "\n\n"
                combined_text += "=" * 80
                combined_text += "\n"
                combined_text += link
                combined_text += "\n"
                combined_text += "=" * 80
                combined_text += "\n\n"
                combined_text += text

                print("✓", link)

            except Exception as e:

                print("\nError:", e)

        filename = website["name"].replace(" ", "_") + ".txt"

        filepath = os.path.join(
            SAVE_FOLDER,
            filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(combined_text)

        print("Saved:", filename)

    except Exception as e:

        print(e)

print("\nFinished.")