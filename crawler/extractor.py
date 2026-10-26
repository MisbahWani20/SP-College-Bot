from bs4 import BeautifulSoup


def extract_text(html):

    soup = BeautifulSoup(html, "lxml")

    for tag in soup([
        "script",
        "style",
        "noscript"
    ]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)