import re


def answer_extraction(user_prompt_type, prediction, lang_detect):
    if not prediction:
        return None
    
    def extract_answer(answer_label):
        """Common processing for answer extraction"""
        multiple_answers = re.search(fr'{answer_label}:\s*([ABCDE]),\s*[ABCDE]', prediction)  # Answer: A, B
        if multiple_answers:
            return None
        
        direct_answer = re.search(fr'{answer_label}:\s*([ABCDE])', prediction, re.DOTALL)  # Answer: A
        if direct_answer:
            return direct_answer.group(1).upper()
        
        return None
    
    def extract_text_after_label(label):
        """Extract text following the label"""
        patterns = list(re.finditer(fr'{label}\s*(.*)', prediction, re.IGNORECASE | re.DOTALL))
        if not patterns:
            match = re.findall(r'[ABCDE]\.', prediction)
            unique_match = set(match)
            if len(unique_match) == 1:
                return unique_match.pop().strip('.').upper()
        else:
            if user_prompt_type == "long_after":
                pattern = patterns[-1]
            else:
                pattern = patterns[0]
            
            and_or_separated = re.search(fr'{label}\s+([ABCDE])\s+(and|or|또는)\s+([ABCDE])\b', pattern.group(0))
            if and_or_separated:
                return None  # Return None for cases like "A and B" or "A 또는 B"

            and_or_separated = re.search(fr'{label}\s+([ABCDE])와\s+([ABCDE])\b', pattern.group(0))
            if and_or_separated:
                return None  # Return None for cases like "A와 B"

            comma_separated = re.search(fr'(?i){label}\s+([ABCDE]),\s+([ABCDE])\b', pattern.group(0),  re.DOTALL)
            
            if comma_separated:
                return None
            
            # Return the first capital letter if there are no commas directly following it
            single_letter = re.search(r'\b([ABCDE])', pattern.group(1))
            if single_letter:
                return single_letter.group(1).upper()
        
        return None
    
    if user_prompt_type == "short" and len(prediction) <= 2:
        return prediction[0].upper() if prediction else None

    if lang_detect != 'ko':
        answer = extract_answer("Answer")
        if answer:
            return answer
        answer = extract_text_after_label("answer is")
        if "답은" in prediction and answer is None:
            answer = extract_text_after_label("답은")
        return answer
    else:
        answer = extract_answer("답")
        if answer:
            return answer
        answer = extract_text_after_label("답은")
        if "answer is" in prediction and answer is None:
            answer = extract_text_after_label("answer is")
        return answer


def normalize(text):
    if text is None:
    	return ""
    return text.replace("(", "").replace(")", "").upper().strip()


def check_equal(answer, prediction):
    '''Compare prediction against the reference'''
    ans = normalize(answer)
    pred = normalize(prediction)

    if ans == pred:
        return True
    else:
        return False