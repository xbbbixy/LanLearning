from itertools import zip_longest

def align(original_analysis: list, english_analysis: list, target_analysis: list) -> list:
    """
    NEW: Aligns three independent analysis lists (original, English, target).
    Each list contains dictionaries with 'word', 'role', and 'role_zh'.
    """
    final_alignment = []
    
    # Determine the maximum length to iterate, ensuring all words are included
    max_len = max(len(original_analysis), len(english_analysis), len(target_analysis))

    for i in range(max_len):
        # Safely get the analysis object or a default placeholder
        original_item = original_analysis[i] if i < len(original_analysis) else { 'word': '-', 'role': None, 'role_zh': '' }
        english_item = english_analysis[i] if i < len(english_analysis) else { 'word': '-', 'role': None, 'role_zh': '' }
        target_item = target_analysis[i] if i < len(target_analysis) else { 'word': '-', 'role': None, 'role_zh': '' }

        # Create a unified dictionary for this alignment position
        # This structure is now different and must be handled by the frontend
        final_alignment.append({
            'original': original_item,
            'english': english_item,
            'target': target_item,
        })

    return final_alignment
