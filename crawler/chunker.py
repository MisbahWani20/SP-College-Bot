import re

def split_into_chunks(text, chunk_size=450):
    """
    Split text into semantic chunks (~450 words).
    """
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 100:
            chunks.append(chunk)
    return chunks