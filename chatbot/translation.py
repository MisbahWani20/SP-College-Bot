from deep_translator import GoogleTranslator, MyMemoryTranslator

def normalize_translated_programme_names(text):
    replacements = {
        "bscit": "bsc it",
        "bsc it": "bsc it",
        "b.sc.it": "bsc it",
        "b.sc it": "bsc it",

        "mscit": "msc it",
        "msc it": "msc it",
        "m.sc.it": "msc it",
        "m.sc it": "msc it",
    }

    normalized = text.lower()

    for old, new in replacements.items():
        normalized = normalized.replace(old, new)

    return normalized

LANGUAGES = {
    "en": "english",
    "ur": "urdu",
    "hi": "hindi",
}


def translate_to_english(text, source_language):

    if source_language == "en":
        return text
    language = LANGUAGES.get(source_language)
    if not language:
        raise Exception( f"Unsupported source language: {source_language}" )
    try:
        translator = GoogleTranslator(
            source=language,
            target="english"
        )
        result = translator.translate(text)
        if result:
            return result
    except Exception as error:
        print(
            "Google translation failed:",
            error
        )
    try:
        translator = MyMemoryTranslator(
            source=language,
            target="english"
        )
        result = translator.translate(text)
        if result:
            return result
    except Exception as error:
        print(
            "Fallback translation failed:",
            error
        )
    raise Exception(
        "Unable to translate the question."
    )


def translate_from_english(text, target_language):

    if target_language == "en":
        return text
    language = LANGUAGES.get(target_language)
    if not language:
        raise Exception( f"Unsupported target language: {target_language}" )
    try:

        translator = GoogleTranslator(
            source="english",
            target=language
        )

        result = translator.translate(text)

        if result:
            return result

    except Exception as error:

        print(
            "Google translation failed:",
            error
        )

    try:

        translator = MyMemoryTranslator(
            source="english",
            target=language
        )

        result = translator.translate(text)

        if result:
            return result

    except Exception as error:

        print(
            "Fallback translation failed:",
            error
        )

    raise Exception(
        "Unable to translate the response."
    )
def split_text(text, max_length=450):
    words = text.split() 
    chunks = [] 
    current_chunk = "" 
    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += ( word + " " ) 
        else:
            if current_chunk.strip(): 
                chunks.append( current_chunk.strip() )
            current_chunk = word + " "
    if current_chunk.strip(): 
        chunks.append( current_chunk.strip() ) 
    return chunks
def translate_chunk( 
        text, 
        source_language, 
        target_language 
):
        try:
          translator = GoogleTranslator(
            source = source_language,
            target = target_language
        )
          result = translator.translate(text)
          if result:
            return result
        except Exception as error:
            print( "Google translation failed:", error )
        try: 
            translator = MyMemoryTranslator( source=source_language, target=target_language )
            result = translator.translate(text)
            if result: 
                return result
        except Exception as error: 
            print( "Fallback translation failed:", error ) 
        raise Exception( "Unable to translate response chunk." )
def translate_from_english( 
        text, 
        target_language 
):
        if target_language == "en": 
            return text 
        language = LANGUAGES.get( target_language )
        if not language: 
            raise Exception( f"Unsupported target language: " f"{target_language}" )
        if not language: 
            raise Exception( f"Unsupported target language: " f"{target_language}" )
        if len(text) <= 450: 
            return translate_chunk( text, "english", language )
        chunks = split_text( text, max_length=450 )
        translated_chunks = []
        for chunk in chunks:
            try: 
                translated_chunk = translate_chunk( chunk, "english", language )
                translated_chunks.append( translated_chunk )
            except Exception as error:
                print( "Chunk translation failed:", error )
                translated_chunks.append( chunk )
            return " ".join( translated_chunks )
    
    

          
       