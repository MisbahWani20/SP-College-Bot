import pdfplumber
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

document_chunks = []


def load_document(pdf_path, source):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if len(paragraph) > 30:

            embedding = model.encode(
                paragraph,
                convert_to_tensor=True
            )

            document_chunks.append({
                "text": paragraph,
                "embedding": embedding,
                "source": source
            })

    print(f"{source} Loaded Successfully!")

def search_documents(query):

    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )

    best_score = 0
    best_text = None
    best_source = None

    for chunk in document_chunks:

        score = util.cos_sim(
            query_embedding,
            chunk["embedding"]
        ).item()

        if score > best_score:

            best_score = score
            best_text = chunk["text"]
            best_source = chunk["source"]

    return best_text, best_source, best_score