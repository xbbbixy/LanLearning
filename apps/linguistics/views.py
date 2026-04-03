from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import translators as ts

from .services import translator, parser, aligner

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def analyze_sentence(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_text = data.get('text')
            target_lang = data.get('target_lang')

            if not original_text:
                return JsonResponse({'error': 'Text is required'}, status=400)

            # 1. Translate
            translations = translator.translate(original_text, target_lang)
            if 'error' in translations:
                return JsonResponse({'error': translations['error']}, status=500)
            
            english_text = translations['english']
            target_text = translations['target']

            # --- NEW: Perform parsing for all three languages ---
            # We assume the original language is Chinese ('zh')
            original_analysis = parser.parse_sentence(original_text, lang='zh')
            english_analysis = parser.parse_sentence(english_text, lang='en')
            target_analysis = parser.parse_sentence(target_text, lang=target_lang)

            # 3. Align the three independent analyses
            alignment = aligner.align(
                original_analysis=original_analysis,
                english_analysis=english_analysis,
                target_analysis=target_analysis
            )

            # 4. Format and return the final response
            response_data = {
                'alignment': alignment
            }
            
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

def get_word_definition(request):
    word = request.GET.get('word')
    sentence = request.GET.get('sentence')
    lang = request.GET.get('lang', 'en')
    target_lang = request.GET.get('target_lang', 'ja')

    if not word:
        return JsonResponse({'error': 'Word is required'}, status=400)

    response_data = {
        'word': word,
        'part_of_speech': None,
        'phonetic': None,
        'definitions': [],
        'examples': [],
        'translation_en': None,
        'translation_target': None,
        'translation_zh': None,
    }

    try:
        if lang == 'zh':
            response_data['translation_en'] = ts.translate_text(word, translator='bing', from_language='zh', to_language='en')
            response_data['translation_target'] = ts.translate_text(word, translator='bing', from_language='zh', to_language=target_lang)
        else:
            response_data['translation_zh'] = ts.translate_text(word, translator='bing', from_language=lang, to_language='zh')
    except Exception as e:
        print(f"Translation in popup failed: {e}")

    word_to_lookup = word
    if sentence:
        try:
            analysis = parser.parse_sentence(sentence, lang=lang)
            for word_info in analysis:
                if word_info['word'].lower() == word.lower():
                    response_data['part_of_speech'] = word_info.get('role_zh', word_info.get('role'))
                    word_to_lookup = word_info.get('lemma', word)
                    break
        except Exception as e:
            print(f"Stanza parsing failed: {e}")

    supported_dictionary_langs = ['en', 'ja', 'fr', 'de']
    if lang in supported_dictionary_langs:
        # --- New: Implement a two-step fallback for dictionary lookup ---
        # 1. First, try to look up the word's lemma (e.g., 'geben')
        # 2. If that fails, fall back to the original word (e.g., 'Geben')
        
        api_data = None
        try:
            # Attempt 1: Look up the lemma
            primary_response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word_to_lookup}')
            if primary_response.status_code == 200:
                api_data = primary_response.json()[0]
            else:
                # Attempt 2: Fallback to the original word if lemma fails
                secondary_response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}')
                if secondary_response.status_code == 200:
                    api_data = secondary_response.json()[0]

            if api_data:
                phonetics = api_data.get('phonetics', [])
                if phonetics and phonetics[0].get('text'):
                    response_data['phonetic'] = phonetics[0]['text']
                else:
                    response_data['phonetic'] = api_data.get('phonetic', '')

                for meaning in api_data.get('meanings', []):
                    for definition in meaning.get('definitions', []):
                        if definition.get('definition'):
                            response_data['definitions'].append(definition['definition'])
                        if definition.get('example'):
                            response_data['examples'].append(definition['example'])
                            
        except Exception as e:
            print(f"Dictionary API call failed for '{word_to_lookup}' or '{word}': {e}")

    return JsonResponse(response_data)

