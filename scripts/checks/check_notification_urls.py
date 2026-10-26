import sqlite3

conn = sqlite3.connect("chatbot/faq.db")
cursor = conn.cursor()

print("\n===== WEB KNOWLEDGE =====\n")

cursor.execute("""
    SELECT page_title, url
    FROM web_knowledge
    WHERE LOWER(url) LIKE '%notification%'
    ORDER BY id
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

print("\n===== WEB CHUNKS =====\n")

cursor.execute("""
    SELECT DISTINCT page_title, url
    FROM web_chunks
    WHERE LOWER(url) LIKE '%notification%'
    ORDER BY url
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()