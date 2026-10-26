import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DATABASE_NAME = "chatbot/faq.db"

NOTIFICATION_URL = (
    "https://www.cusrinagar.edu.in/Notification/NotificationListPartial"
)

RESULT_URL = (
    "https://www.cusrinagar.edu.in/Result/ResultNotificationList"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def create_cus_website_table():

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cus_website_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            title TEXT NOT NULL,
            item_date TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def clear_cus_website_items(item_type):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cus_website_items
        WHERE item_type = ?
    """, (item_type,))

    conn.commit()
    conn.close()

def normalize_date(date_text):
    try:
        return datetime.strptime(
            date_text.strip(),
            "%d-%B-%Y"
        ).strftime("%Y-%m-%d")
    except ValueError:
        return date_text.strip()


def save_item(item_type, title, item_date, url):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cus_website_items
        (item_type, title, item_date, url)
        VALUES (?, ?, ?, ?)
    """, (
        item_type,
        title,
        item_date,
        url
    ))

    conn.commit()
    conn.close()


def fetch_notifications():
    response = requests.get(
        NOTIFICATION_URL,
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()
    soup = BeautifulSoup(
        response.text,
        "lxml"
    )
    rows = soup.find_all("tr")
    if not rows:
        raise RuntimeError(
          "CUS notification page returned no notification rows."
        )
    clear_cus_website_items("notification")
    count = 0
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        title = cells[0].get_text(
            " ",
            strip=True
        )
        item_date = cells[1].get_text(
            " ",
            strip=True
        )
        item_date = normalize_date(item_date)
        link = row.find("a")
        if not title:
            continue
        url = None
        if link and link.get("href"):
            url = link.get("href")
            if url.startswith("/"):
                url = "https://www.cusrinagar.edu.in" + url
        save_item(
            "notification",
            title,
            item_date,
            url
        )
        count += 1
    return count

def fetch_results():
    response = requests.get(
        RESULT_URL,
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()
    soup = BeautifulSoup(
        response.text,
        "lxml"
    )
    rows = soup.find_all("tr")
    if not rows:
     raise RuntimeError(
         "CUS result page returned no result rows."
    )
    clear_cus_website_items("result")
    count = 0
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        title = cells[1].get_text(
            " ",
            strip=True
        )

        item_date = cells[4].get_text(
            " ",
            strip=True
        )
        item_date = normalize_date(item_date)
        link = row.find("a")
        if not title:
            continue
        url = None
        if link and link.get("href"):
            url = link.get("href")
            if url.startswith("/"):
                url = "https://www.cusrinagar.edu.in" + url
        save_item(
            "result",
            title,
            item_date,
            url
        )
        count += 1
    return count


if __name__ == "__main__":
    print("Creating CUS website table...")
    create_cus_website_table()
    print("Fetching notifications...")
    notification_count = fetch_notifications()
    print(
        "Notifications imported:",
        notification_count
    )
    print("Fetching results...")
    result_count = fetch_results()
    print(
        "Results imported:",
        result_count
    )
    print("\nCUS website data updated successfully.")