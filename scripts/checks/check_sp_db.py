
import sqlite3

conn = sqlite3.connect("spcollege_data.db")

tables = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

for table in tables:
    name = table[0]
    count = conn.execute(
        f'SELECT COUNT(*) FROM "{name}"'
    ).fetchone()[0]
    print(f"{name}: {count} rows")

# print("\n--- SAVED SP COLLEGE PAGES ---")

# conn = sqlite3.connect("spcollege_data.db")

# for row in conn.execute("""
#     SELECT title, url
#     FROM sp_pages
#     ORDER BY title
# """):
#     print(f"{row[0]} | {row[1]}")


# conn.close()

# print("\n--- DEPARTMENT AND FACULTY PAGE CONTENT ---")

# conn = sqlite3.connect("spcollege_data.db")

# for row in conn.execute("""
#     SELECT title, url, content
#     FROM sp_pages
#     WHERE lower(url) LIKE '%department%'
#        OR lower(url) LIKE '%profile%'
#        OR lower(url) LIKE '%peoplelist%'
#        OR lower(content) LIKE '%head of department%'
#        OR lower(content) LIKE '%hod%'
#        OR lower(content) LIKE '%faculty%'
#     ORDER BY title
# """):
#     print(f"\nTITLE: {row[0]}")
#     print(f"URL: {row[1]}")
#     print(f"CONTENT PREVIEW: {(row[2] or '')[:700]}")
#     print("-" * 60)

# conn.close()
print("\n--- IT DEPARTMENT CONTENT CHECK ---")

conn = sqlite3.connect("spcollege_data.db")

row = conn.execute("""
    SELECT content
    FROM sp_pages
    WHERE url LIKE '%Page=IT_Department%'
    LIMIT 1
""").fetchone()

if row and row[0]:
    content = row[0]

    print("Total content characters:", len(content))

    for keyword in [
        "Faculty",
        "HOD",
        "Head of Department",
        "Programmes",
        "Syllabus",
        "Notices",
        "Contact Us"
    ]:
        print(f"{keyword}: {keyword.lower() in content.lower()}")

    print("\n--- SAVED CONTENT END PREVIEW ---")
    print(content[-1500:])
else:
    print("IT Department content not found.")

conn.close()
print("\n--- IT DEPARTMENT CHUNKS CHECK ---")

conn = sqlite3.connect("spcollege_data.db")

rows = conn.execute("""
    SELECT source_url, chunk_index, chunk_text
    FROM sp_chunks
    WHERE source_url LIKE '%Page=IT_Department%'
    ORDER BY chunk_index
""").fetchall()

print("Total IT Department chunks:", len(rows))

for row in rows:
    print(f"\nChunk {row[1]}:")
    print((row[2] or "")[:500])
    print("-" * 40)

conn.close()


