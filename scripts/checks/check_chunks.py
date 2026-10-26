import sqlite3

conn = sqlite3.connect("chatbot/faq.db")

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM web_chunks")

count = cursor.fetchone()[0]

print("Total Chunks:", count)

cursor.execute("""

SELECT
college,
page_title,
chunk_no

FROM web_chunks

LIMIT 10

""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
