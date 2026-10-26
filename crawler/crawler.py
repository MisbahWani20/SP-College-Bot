from config import WEBSITES
from utils import download_page
from extractor import extract_text
from chatbot.database import insert_web_knowledge

import os


SAVE_FOLDER = "data/raw"

os.makedirs(
    SAVE_FOLDER,
    exist_ok=True
)

for website in WEBSITES:

    print(f"Crawling {website['name']}...")

    try:

        html = download_page(
            website["url"]
        )

        text = extract_text(html)

        filename = website["name"] \
            .replace(" ", "_") + ".txt"

        filepath = os.path.join(
            SAVE_FOLDER,
            filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(text)

        print("Saved:", filename)

    except Exception as e:

        print(
            "Error:",
            website["name"],
            e
        )

print("\nFinished.")