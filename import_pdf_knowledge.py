import os
import fitz  # PyMuPDF
import sqlite3

DATABASE = "chatbot/faq.db"

PDF_FOLDER = "data/official_data/pdfs"


conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS pdf_knowledge(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    pdf_name TEXT,

    page INTEGER,

    chunk TEXT
)
""")


for file in os.listdir(PDF_FOLDER):

    if not file.endswith(".pdf"):
        continue

    pdf_path = os.path.join(PDF_FOLDER, file)

    print("Reading:", file)

    doc = fitz.open(pdf_path)

    for page_no in range(len(doc)):

        page = doc.load_page(page_no)

        text = page.get_text()

        if len(text.strip()) == 0:
            continue

        cursor.execute("""

        INSERT INTO pdf_knowledge(

            pdf_name,

            page,

            chunk

        )

        VALUES(?,?,?)

        """,(

            file,

            page_no + 1,

            text

        ))

    doc.close()


conn.commit()
conn.close()

print("PDF Knowledge Imported Successfully.")