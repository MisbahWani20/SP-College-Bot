import os
import sys
import openpyxl

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.database import add_answer, add_question

# Excel file path
EXCEL_FILE = "data/official_data/master_faq.xlsx"

# Load workbook
workbook = openpyxl.load_workbook(EXCEL_FILE)
sheet = workbook.active

current_answer = None
current_answer_id = None

# Skip first row (header)
for row in sheet.iter_rows(min_row=2, values_only=True):

    intent, question, answer, category, keywords, source, last_updated = row

    # Skip empty rows
    if not question:
        continue

    # Insert answer only if it is different
    if answer != current_answer:

        current_answer_id = add_answer(
            intent,
            answer,
            category,
            source,
            str(last_updated)
        )

        current_answer = answer

    # Insert question
    add_question(
        current_answer_id,
        question,
        keywords
    )

print("FAQs Imported Successfully!")