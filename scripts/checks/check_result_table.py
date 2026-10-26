import requests
from bs4 import BeautifulSoup

URL = "https://www.cusrinagar.edu.in/Result/ResultNotificationList"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    URL,
    headers=headers,
    timeout=20
)

response.raise_for_status()

soup = BeautifulSoup(
    response.text,
    "lxml"
)

rows = soup.find_all("tr")

for row in rows:

    cells = row.find_all("td")

    if cells:

        print("\nROW")
        print("-" * 60)

        for index, cell in enumerate(cells):

            print(
                f"CELL {index}:",
                cell.get_text(" ", strip=True)
            )

        print("-" * 60)