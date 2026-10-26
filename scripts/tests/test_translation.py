
from deep_translator import GoogleTranslator

# Urdu → English

urdu_text = "بی ایس سی فزکس کی فیس کیا ہے؟"

urdu_to_english = GoogleTranslator(
source="ur",
target="en"
).translate(urdu_text)

print("Urdu:")
print(urdu_text)

print("\nEnglish:")
print(urdu_to_english)

# Hindi → English

hindi_text = "बीएससी फिजिक्स की फीस क्या है?"

hindi_to_english = GoogleTranslator(
source="hi",
target="en"
).translate(hindi_text)

print("\nHindi:")
print(hindi_text)

print("\nEnglish:")
print(hindi_to_english)

# English → Urdu

english_text = "What is the fee for BSc Physics?"

english_to_urdu = GoogleTranslator(
source="en",
target="ur"
).translate(english_text)

print("\nEnglish:")
print(english_text)

print("\nUrdu:")
print(english_to_urdu)

# English → Hindi

english_to_hindi = GoogleTranslator(
source="en",
target="hi"
).translate(english_text)

print("\nHindi:")
print(english_to_hindi)
