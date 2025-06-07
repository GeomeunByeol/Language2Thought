import re

def answer_extraction(user_prompt_type, prediction, lang_detect, input, answer_option):  # , input, dataset_name
    if not prediction:
        return None

    # If the input contains at least two occurrences of "E. ", we assume there are five options: A, B, C, D, E
    if input.count("E. ") >= 2:
        # Extract text for option A between "A. " and "B. "
        if re.search(r'A\. (.*?)(?=\s*)B\.', input, re.DOTALL) is not None:
            A = re.search(r'A\. (.*?)(?=\s*)B\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else:
            A = None

        if re.search(r'B\. (.*?)(?=\s*)C\.', input, re.DOTALL) is not None:
            B = re.search(r'B\. (.*?)(?=\s*)C\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else:
            B = None

        if re.search(r'C\. (.*?)(?=\s*)D\.', input, re.DOTALL) is not None:
            C = re.search(r'C\. (.*?)(?=\s*)D\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else: 
            C = None

        if re.search(r'D\. (.*?)(?=\s*)E\.', input, re.DOTALL) is not None:
            D = re.search(r'D\. (.*?)(?=\s*)E\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else:
            D = None

        if re.search(r'E\. (.*?)$', input) is not None:
            E = re.search(r'E\. (.*?)$', input).group(1).strip()
        else: 
            E = None
        # print(A, B, C, D, E)

        # Determine the answer content based on the provided answer_option.
        # If answer_option is "E", then answer_content is E.
        if answer_option == "E":
            answer_content = E
        # Otherwise, try to extract the text for the given answer option from its starting letter to the next option's letter.
        else:
            if re.search(fr'{answer_option}\. (.*?)(?=\s*){chr(ord(answer_option) + 1)}\.', input, re.DOTALL) is not None:
                answer_content = re.search(fr'{answer_option}\. (.*?)(?=\s*){chr(ord(answer_option) + 1)}\.', input, re.DOTALL).group(1).replace('\n', '').strip()
            else:
                answer_content = None

        # Build a list of all extracted option texts.
        not_answer_content_list = [A, B, C, D, E]
        # Remove the answer_content from the list, leaving only the distractor options.
        if answer_content in not_answer_content_list:
            not_answer_content_list.remove(answer_content)

        
    else:
        if re.search(r'A\. (.*?)(?=\s*)B\.', input, re.DOTALL) is not None:
            A = re.search(r'A\. (.*?)(?=\s*)B\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else:
            A = None

        if re.search(r'B\. (.*?)(?=\s*)C\.', input, re.DOTALL) is not None:
            B = re.search(r'B\. (.*?)(?=\s*)C\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else:
            B = None

        if re.search(r'C\. (.*?)(?=\s*)D\.', input, re.DOTALL) is not None:
            C = re.search(r'C\. (.*?)(?=\s*)D\.', input, re.DOTALL).group(1).replace('\n', '').strip()
        else: 
            C = None

        if re.search(r'D\. (.*?)$', input) is not None:
            D = re.search(r'D\. (.*?)$', input).group(1).replace('\n', '').strip()
        else: 
            D = None

        if answer_option == "D":
            answer_content = D
        else:
            if re.search(fr'{answer_option}\. (.*?)(?=\s*){chr(ord(answer_option) + 1)}\.', input, re.DOTALL) is not None:
                answer_content = re.search(fr'{answer_option}\. (.*?)(?=\s*){chr(ord(answer_option) + 1)}\.', input, re.DOTALL).group(1).replace('\n', '').strip()
            else:
                answer_content = None

        not_answer_content_list = [A, B, C, D]
        if answer_content in not_answer_content_list:
            not_answer_content_list.remove(answer_content)

    
    def extract_answer(answer_label):
        """Common processing for extracting the answer from prediction"""
        # Look for a pattern where the label is followed by an answer letter (A-E or corresponding Arabic letters)
        # and then another answer letter after a comma. If found, it's ambiguous so return None.
        multiple_answers = re.search(fr'{answer_label}:\s*([ABCDEأبجده]),\s*[ABCDEأبجده]', prediction)
        if multiple_answers:
            return None
        
        # Look for a direct answer pattern with the label followed by a single answer letter.
        direct_answer = re.search(fr'{answer_label}:\s*([ABCDEأبجده])', prediction)  # 정답: A
        if direct_answer:
            return direct_answer.group(1).upper()
        
        return None
    
    
    def extract_text_after_label(label):
        """Extract the text following the given label from the prediction."""
        patterns = list(re.finditer(fr'{label}\s*(.*)', prediction, re.IGNORECASE | re.DOTALL))
        if not patterns:
            match = re.findall(r'[ABCDEأبجده]\.', prediction)
            # print(match)
            unique_match = set(match)
            if len(unique_match) == 1:
                return unique_match.pop().strip('.').upper()
            else:
                return None
        else:
            if user_prompt_type == "long_after":                
                pattern = patterns[-1]
            else:
                pattern = patterns[0]
            
            # Check if the extracted text contains multiple answers separated by words like 'and', 'or' (including Arabic variants)
            and_or_separated = re.search(r'\b([ABCDEأبجده])\s+(and|or|و|أو)\s+([ABCDEأبجده])\b', pattern.group(1))
            
            if and_or_separated:
                return None 

            # Check if multiple answers are separated by a comma or its Arabic equivalent
            comma_separated = re.search(r'\b([ABCDEأبجده]).*(,|،)\s*([ABCDEأبجده])\b', pattern.group(1))
            
            if comma_separated:
                return None
            
            single_letter = re.search(r'\b([ABCDEأبجده])\.', pattern.group(1))
            if single_letter:
                return single_letter.group(1).upper()


        if (answer_content is not None) and (answer_content in pattern.group()):
            for option in not_answer_content_list:
                if option is not None and option in prediction:
                    return False
                else:
                    return True
        else:
            return False

        
        return None


    if lang_detect == 'en':
        answer = extract_answer("Answer")
        if answer:
            return answer
        
        answer = extract_text_after_label("answer is")

        if ("الإجابة هي" in prediction) and (answer is None):  # In Arabic, an adjective is inserted between the noun (answer) and the verb (is).
            answer = extract_text_after_label("الإجابة هي")
        if ("الجواب هو" in prediction) and (answer is None):
            answer = extract_text_after_label("الجواب هو")
        if ("الإجابة الصحيحة هي" in prediction) and (answer is None): 
            answer = extract_text_after_label("الإجابة الصحيحة هي")
        if ("الجواب الصحيح هو" in prediction) and (answer is None):
            answer = extract_text_after_label("الجواب الصحيح هو")
        return answer
        
    else:
        answer = extract_answer("إجابة")
        if answer:
            return answer
        answer = extract_answer("الجواب")
        if answer:
            return answer
        
        answer = extract_text_after_label("الإجابة هي")

        if ("الجواب هو" in prediction) and (answer is None):
            answer = extract_text_after_label("الجواب هو")
        if ("الإجابة الصحيحة هي" in prediction) and (answer is None): 
            answer = extract_text_after_label("الإجابة الصحيحة هي")
        if ("الجواب الصحيح هو" in prediction) and (answer is None):
            answer = extract_text_after_label("الجواب الصحيح هو")
        if "answer is" in prediction and (answer is None):
            answer = extract_text_after_label("answer is")
        return answer
        

def normalize(text):
    if text is None:
    	return ""
    if type(text) == bool:
        return text

    arabic_to_english = {
        'أ': 'A',
        'ب': 'B',
        'ج': 'C',
        'د': 'D',
        'ه': 'E'
    }

    for arabic_char, english_char in arabic_to_english.items():
        text = text.replace(arabic_char, english_char)

    return text.replace("(", "").replace(")", "").upper().strip()


def check_equal(answer, prediction):
    '''Compare prediction against the reference'''
    ans = normalize(answer)
    pred = normalize(prediction)

    if pred == True or (ans == pred):
        return True
    else:
        return False
    