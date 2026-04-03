import translators as ts

def translate(text: str, target_lang: str) -> dict:
    """
    Uses the 'translators' library to perform real-time translation.
    It translates the source text to both English and the target language.
    """
    try:
        # Translate from source (auto-detect) to English
        english_translation = ts.translate_text(
            query_text=text,
            translator='bing',  # Changed from 'google'
            from_language='auto',
            to_language='en'
        )

        # Translate from source (auto-detect) to the target language
        target_translation = ts.translate_text(
            query_text=text,
            translator='bing',  # Changed from 'google'
            from_language='auto',
            to_language=target_lang
        )

        return {
            'english': english_translation,
            'target': target_translation,
        }
    except Exception as e:
        # If any error occurs during translation, return an error dictionary
        # This helps in debugging and provides a clear error to the user
        print(f"[Translation Error]: {e}")
        return {
            'error': f"Translation failed: {e}"
        }
