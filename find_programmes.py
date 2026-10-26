import re

with open("prospectus_text.txt", "r", encoding="utf-8") as file:
    text = file.read()

lines = text.split("\n")

print("\n========== POSSIBLE PROGRAMMES ==========\n")

for line in lines:

    line = line.strip()

    if len(line) < 3:
        continue

    keywords = [
        "Bachelor",
        "Master",
        "B.A",
        "B.Sc",
        "B.Com",
        "BBA",
        "BCA",
        "B.Ed",
        "MBA",
        "MCA",
        "M.Sc",
        "M.Com",
        "M.A"
    ]

    if any(word in line for word in keywords):
        print(line)