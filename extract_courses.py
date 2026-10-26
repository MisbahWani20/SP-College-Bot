import pdfplumber
import re

pdf_path = "data/official_data/Prospectus.pdf"

courses = set()

pattern = re.compile(
    r"\b(B\.A|B\.Sc(?:\s*\([^)]+\))?|B\.Com|BCA|BBA|MBA|MCA|M\.Sc(?:\s*[A-Za-z ]+)?|M\.A(?:\s*[A-Za-z ]+)?|M\.Com|IMBA|IMCA|B\.Ed(?:-M\.Ed)?)\b",
    re.IGNORECASE
)

with pdfplumber.open(pdf_path) as pdf:

    for page in pdf.pages:

        text = page.extract_text()

        if not text:
            continue

        matches = pattern.findall(text)

        for match in matches:
            courses.add(match.strip())

print("\n===== COURSES FOUND =====\n")

for course in sorted(courses):
    print(course)