
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone

PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_DIR / "spcollege_data.db"

SOURCES = [
    {
        "url": "https://spcollege.edu.in/Main/Default.aspx",
        "title": "SP College - About and Contact Information",
        "content": """
Sri Pratap College, also known as SP College, is located at
M.A. Road, Srinagar, Jammu and Kashmir, India - 190001.

The college was established in 1905.

SP College offers undergraduate and postgraduate education
in various science and other subject areas.

Full postal address:
Sri Pratap College
M.A. Road, Srinagar
Jammu and Kashmir, India
PIN code: 190001

Official phone number: 0194-2476828
Phone link: tel:+911942476828

Official email: sri-pratap-college@jk.gov.in
Additional college email: spcsgr1905@gmail.com

Official email link: mailto:sri-pratap-college@jk.gov.in
Additional email link: mailto:spcsgr1905@gmail.com

Official website:
https://spcollege.edu.in/Main/Default.aspx

Official contact page:
https://spcollege.edu.in/Main/contactus.aspx

Google Maps location:
https://www.google.com/maps?q=34.075868,74.8204322

Official coordinates:
Latitude: 34.075868
Longitude: 74.8204322

For current announcements, admissions, timetables, examination
notices and other updates, consult the official college website.
"""
    },
    {
        "url": "https://spcollege.edu.in/Main/List.aspx?SubType=Announcement&Type=Alert",
        "title": "SP College Official Announcements",
        "content": """
This is the official announcements page of Sri Pratap College.

Students can check this page for college announcements,
admission updates, examination notices, timetables, fee notices
and other student-related information.

Always open the original notice to confirm its details,
applicable batch or semester, and dates.

Official announcements link:
https://spcollege.edu.in/Main/List.aspx?SubType=Announcement&Type=Alert
"""
    },
    {
        "url": "https://spcollege.edu.in/Main/List.aspx?Type=QuickLink",
        "title": "SP College Quick Links",
        "content": """
The official SP College Quick Links page lists student resources,
including:

- Admissions Information Brochure 2026-27
- Undergraduate Admission 2026-27
- Syllabus
- Academic Bank of Credits (ABC) Portal
- SWAYAM Portal
- National Anti-Ragging Helpline: 1800-180-5522

Use the official Quick Links page to open resources and
check their latest details.

Official Quick Links:
https://spcollege.edu.in/Main/List.aspx?Type=QuickLink
"""
    },
    
    {
        "url": "https://spcollege.edu.in/Main/CourseList.aspx",
        "title": "SP College Courses and Programmes",
        "content": """
Sri Pratap College Srinagar offers undergraduate,
postgraduate and integrated programmes in different subject areas.

The college offers programmes and subjects in areas such as:
Biochemistry, Bioinformatics, Biotechnology, Botany,
Chemistry, Clinical Biochemistry, Electronics, English,
Environmental Studies, Geography, Geology, Human Genetics,
Information Technology, Mathematics, Physics, Statistics,
Water Management and Zoology.

The college has undergraduate programmes and postgraduate
programmes in selected subjects. Programme duration,
eligibility, intake capacity and current availability vary
by course.

For the complete and updated course list, visit:
https://spcollege.edu.in/Main/CourseList.aspx

Students should check the official course list for the
latest programme details.
"""
    }
]


def make_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_into_chunks(content, max_chars=800):
    paragraphs = [
        paragraph.strip()
        for paragraph in content.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""

            for start in range(0, len(paragraph), max_chars):
                chunks.append(paragraph[start:start + max_chars])
            continue

        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = (
                current + "\n\n" + paragraph
                if current else paragraph
            )

    if current:
        chunks.append(current)

    return chunks


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}\n"
            "Run the database initialization command first."
        )

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        for source in SOURCES:
            content = source["content"].strip()

            conn.execute(
                """
                INSERT INTO sp_pages
                    (url, title, source_type, content,
                     content_hash, fetched_at)
                VALUES (?, ?, 'html', ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    source_type = excluded.source_type,
                    content = excluded.content,
                    content_hash = excluded.content_hash,
                    fetched_at = excluded.fetched_at
                """,
                (
                    source["url"],
                    source["title"],
                    content,
                    make_hash(content),
                    datetime.now(timezone.utc).isoformat()
                )
            )

            # Rebuild this page's chunks safely when rerunning.
            conn.execute(
                "DELETE FROM sp_chunks WHERE source_url = ?",
                (source["url"],)
            )

            for index, chunk in enumerate(split_into_chunks(content)):
                conn.execute(
                    """
                    INSERT INTO sp_chunks
                        (source_url, chunk_index, chunk_text, chunk_hash)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        source["url"],
                        index,
                        chunk,
                        make_hash(chunk)
                    )
                )

        conn.commit()

    print("Starter SP College information saved successfully.")
    print(f"Database: {DB_PATH}")
    print(f"Sources processed: {len(SOURCES)}")


if __name__ == "__main__":
    main()
