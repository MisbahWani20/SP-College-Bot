import pdfplumber

pdf_path = "data/official_data/Prospectus.pdf"

with pdfplumber.open(pdf_path) as pdf:

    for i, page in enumerate(pdf.pages):

        tables = page.extract_tables()

        if tables:

            print(f"\n========== PAGE {i+1} ==========\n")

            for table in tables:

                for row in table:
                    print(row)

                print("-" * 80)