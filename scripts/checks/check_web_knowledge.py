import sqlite3

conn = sqlite3.connect("chatbot/faq.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM web_knowledge")
count = cursor.fetchone()[0]

print("Total Records:", count)

cursor.execute("""
SELECT college, page_title
FROM web_knowledge
LIMIT 5
""")

rows = cursor.fetchall()

print("\nSample Records:\n")

for row in rows:
    print(row)

conn.close()