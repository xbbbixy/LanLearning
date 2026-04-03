import stanza
import os

STANZA_RESOURCES_DIR = "D:\\stanza_resources"
PIPELINE_CACHE = {}

# --- NEW: Final & Comprehensive Chinese mapping for Universal Dependencies ---
ROLE_ZH_MAP = {
    # Core Arguments
    'nsubj': '主语',
    'obj': '宾语',  # Added for general object
    'dobj': '宾语',
    'iobj': '间接宾语',
    'csubj': '从句主语',
    'ccomp': '从句补语',
    'xcomp': '开放性从句补语',
    'nsubj:pass': '被动主语',
    'csubj:pass': '被动从句主语',

    # Non-core Dependents
    'obl': '斜向定语',
    'vocative': '呼格',
    'expl': '虚词',
    'dislocated': '移位',
    'advcl': '状语从句',
    'advmod': '状语',
    'discourse': '话语标记',

    # Modifiers
    'amod': '形容词修饰',
    'nummod': '数量修饰',
    'acl': '从句修饰',
    'acl:relcl': '关系从句',

    # Noun Dependents
    'appos': '同位语',
    'nmod': '名词修饰',
    'nmod:poss': '所有格',
    'det': '限定词',
    'clf': '分类词',

    # Compounding and MWE
    'compound': '复合词',
    'compound:prt': '动词小品',
    'fixed': '固定搭配',
    'flat': '平行结构',
    'goeswith': '连接词',

    # Function Words
    'aux': '助动词',
    'aux:pass': '被动助动词',
    'cop': '系动词',
    'mark': '标记',
    'case': '格位标记',

    # Coordination
    'conj': '并列项',
    'cc': '并列连词',

    # Special
    'root': '核心动词',  # Changed from ROOT
    'punct': '标点',
    'parataxis': '并列句',
    'orphan': '孤立词',
    'reparandum': '修正词',
    'dep': '未分类依赖',
}

def get_pipeline(lang: str):
    if lang not in PIPELINE_CACHE:
        print(f"--- Caching pipeline for language: '{lang}'... ---")
        PIPELINE_CACHE[lang] = stanza.Pipeline(
            lang=lang, dir=STANZA_RESOURCES_DIR, 
            processors='tokenize,pos,lemma,depparse', download_method=None
        )
        print(f"--- Pipeline for '{lang}' cached successfully. ---")
    return PIPELINE_CACHE[lang]

def parse_sentence(text: str, lang: str = 'en') -> list:
    nlp = get_pipeline(lang)
    doc = nlp(text)
    if not doc.sentences:
        return []
    sentence = doc.sentences[0]
    
    final_roles = []
    for word in sentence.words:
        role_en = word.deprel
        # Use explicit if/else for robust fallback
        if role_en in ROLE_ZH_MAP:
            role_zh = ROLE_ZH_MAP[role_en]
        else:
            role_zh = f"({role_en})" # Fallback for any truly unknown tags
            
        final_roles.append({
            "word": word.text, 
            "role": role_en, 
            "role_zh": role_zh
        })

    return final_roles
