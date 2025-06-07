import re


def answer_extraction(user_prompt_type, prediction, lang_detect):
    if not prediction:
        return None
    
    def extract_answer(answer_label, lang_detect):
        """Common processing for answer extraction"""
        colon = ':' if lang_detect == 'en' else '：'
        comma = ',' if lang_detect == 'en' else '，'

        multiple_answers = re.search(fr'{answer_label}{colon}\s*([ABCDE]){comma}\s*[ABCDE]', prediction)  # Answer: A, B
        if multiple_answers:
            return None
        
        direct_answer = re.search(fr'{answer_label}{colon}\s*([ABCDE])', prediction)  # Answer: A
        if direct_answer:
            return direct_answer.group(1).upper()
        
        return None
    
    def extract_text_after_label(label, lang_detect):
        """Extract text following the label"""
        patterns = list(re.finditer(fr'{label}\s*(.*)', prediction, re.IGNORECASE | re.DOTALL))

        # Set punctuation and comma based on detected language
        punctuation = '.' if lang_detect == 'en' else '。'
        comma = ',' if lang_detect == 'en' else '，'

        # If no pattern is found for the label
        if not patterns:
            # Look for a standalone answer letter (A-E) immediately followed by the punctuation
            match = re.findall(fr'[ABCDE]{punctuation}', prediction)
            unique_match = set(match)
             # If there's exactly one unique match, return it after stripping the punctuation
            if len(unique_match) == 1:
                return unique_match.pop().strip(punctuation).upper()
        else:
            if user_prompt_type == "long_after":
                pattern = patterns[-1]
            else:
                pattern = patterns[0]

            # Check if the label is followed by two answers separated by 'and', 'or', '和', or '或'
            and_or_separated = re.search(fr'{label}\s*([ABCDE])\s*(and|or|和|或)\s*([ABCDE])\b', pattern.group(0))
            if and_or_separated:
                return None  # Ambiguous case: multiple answers found

            # Check if the label is followed by two answers separated by a comma (language-specific)
            comma_separated = re.search(fr'(?i){label}\s*([ABCDE]){comma}\s*([ABCDE])\b', pattern.group(0),  re.DOTALL)      
            if comma_separated:
                return None  # Ambiguous case: multiple answers found
            
            if lang_detect == "en":
                single_letter = re.search(r'\b([ABCDE])', pattern.group(1))
            else:
                single_letter = re.search(r'([ABCDE])', pattern.group(1))
            if single_letter:
                return single_letter.group(1).upper()
        
        return None
    
    if user_prompt_type == "short" and len(prediction) <= 2:
        return prediction[0].upper() if prediction else None

    if lang_detect == 'en':
        answer = extract_answer("Answer", lang_detect)
        if answer:
            return answer
        answer = extract_text_after_label("answer is", lang_detect)
        if "答案是" in prediction and answer is None:
            answer = extract_text_after_label("答案是", lang_detect)
        return answer
    
    else:
        answer = extract_answer("答案", lang_detect)
        if answer:
            return answer
        answer = extract_text_after_label("答案是", lang_detect)
        if "answer is" in prediction and answer is None:
            answer = extract_text_after_label("answer is", lang_detect)

        return answer


def normalize(text):
    if text is None:
    	return ""
    if type(text) == float:
        print(text)
    return text.replace("(", "").replace(")", "").upper().strip()


def check_equal(answer, prediction):
    '''Compare prediction against the reference'''
    ans = normalize(answer)
    pred = normalize(prediction)

    if ans == pred:
        return True
    else:
        return False