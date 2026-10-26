import pdfplumber

PDF_PATH = "data/official_data/Prospectus.pdf"

text = ""

with pdfplumber.open(PDF_PATH) as pdf:

    print("Total Pages:", len(pdf.pages))

    for page in pdf.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n\n"

print("Extraction Completed!")

with open("prospectus_text.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("Text Saved Successfully!")