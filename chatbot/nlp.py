# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# from spellchecker import SpellChecker

# stop_words = set(stopwords.words("english"))
# stemmer = PorterStemmer()
# spell = SpellChecker()

# def preprocess_text(text):
#     text = text.lower()
#     text = correct_spelling(text)
#     tokens = word_tokenize(text)
#     filtered_words = []

#     for word in tokens:
#         if word.isalnum() and word not in stop_words:
#             filtered_words.append(stemmer.stem(word))
#     return filtered_words

# def correct_spelling(text):
#     corrected_words = []
#     words = text.split()
#     for word in words:
#         corrected_word = spell.correction(word)
#         corrected_words.append(corrected_word)
#     return " ".join(corrected_words)


import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from spellchecker import SpellChecker

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()
spell = SpellChecker()

# Preserve college names, abbreviations and programme names.
PROTECTED_WORDS = {
    "cu", "cus", "sp", "spc", "asc", "gcw", "iase",
    "it", "ai", "ml", "ba", "bsc", "bca", "bba",
    "bcom", "msc", "mca", "mcom", "mba", "bed", "med",
    "sri", "pratap", "srinagar", "cluster", "amar", "singh",
    "government", "women", "bemina", "university",
    "ncc", "nss", "hod", "hods", "ug", "pg", "phd",
}


def correct_spelling(text):
    if not text:
        return text

    # Contextually important question words that SpellChecker may miscorrect.
    common_corrections = {
        "whre": "where",
        "wher": "where",
        "waht": "what",
        "abut": "about",
        "collge": "college",
    }

    tokens = re.findall(r"[A-Za-z]+|[^A-Za-z]+", text)
    corrected_tokens = []

    for token in tokens:
        if not token.isalpha():
            corrected_tokens.append(token)
            continue

        word = token.lower()

        if word in PROTECTED_WORDS or len(word) <= 2:
            corrected_tokens.append(token)
            continue

        if word in common_corrections:
            corrected = common_corrections[word]
        else:
            corrected = spell.correction(word) or word

        # Preserve capitalization where practical.
        if token.isupper():
            corrected = corrected.upper()
        elif token.istitle():
            corrected = corrected.capitalize()

        corrected_tokens.append(corrected)

    return "".join(corrected_tokens)



def preprocess_text(text):
    text = correct_spelling(text.lower())
    tokens = word_tokenize(text)
    filtered_words = []

    for word in tokens:
        if word.isalnum() and word not in stop_words:
            filtered_words.append(stemmer.stem(word))

    return filtered_words
