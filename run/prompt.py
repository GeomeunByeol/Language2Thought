class UserPrompt:
    def __init__(self, data_name, lang):
        self.data_name = data_name
        self.lang = lang
        self.en_options = "A, B, C, D, or E" if (data_name == "Geography_CSAT" or data_name == "ar_five_updated") else "A, B, C, or D"
        self.ko_options = "A, B, C, D, E" if data_name == "Geography_CSAT" else "A, B, C, D"
        self.zh_options = "A、B、C 或 D"
        self.ar_options = "A، B، C، D، أو E" if data_name == "ar_five_updated" else "A، B، C، أو D"
        self.marks = {
            "en": ("Question", "Answer"),
            "ko": ("문제", "정답"),
            "zh": ("问题", "答案"),
            "ar": ("سؤال", "إجابة")

        }

    def get_prompt(self, prompt_type):
        # Prepare the base part of the prompt
        question_mark, answer_mark = self.marks[self.lang]
        if self.lang == "en":
            base_prompt = f"Read the given Question, and choose the correct answer from options {self.en_options}."
            prompt = {
                "short": f"{base_prompt} Respond with a single alphabet.",
                "long": f"{base_prompt} Respond with a single letter, then show your work.",
                "long_after": f'Answer the given multiple choice question and show your work. The answer can only be an option like {self.en_options}. You need to output the answer in your final sentence like "Therefore, the answer is ...".',
            }.get(prompt_type, "unknown prompt type")
        elif self.lang == "ko":
            base_prompt = f"주어진 질문을 읽고, 적절한 정답을 {self.ko_options} 중에 골라 알파벳 하나로 답하시오."
            prompt = {
                "short": base_prompt,
                "long": f"{base_prompt} 그런 후에 풀이 과정을 보이시오.",
                "long_after": f'주어진 객관식 문제에 답하고, 풀이 과정을 보이시오. 정답은 {self.ko_options} 중 하나여야 한다. 마지막 문장에서 "따라서 답은 ..."처럼 답을 출력하시오.',
            }.get(prompt_type, "unknown prompt type")
        elif self.lang == "zh":
            prompt = {
                "long_after": f'回答给定的多项选择题并展示您的解题过程。答案只能是一个选项，如{self.zh_options}。您需要在最后一句中输出答案，如“因此，答案是...”。',
            }.get(prompt_type, "unknown prompt type")
        elif self.lang == "ar":
            prompt = {
                "long_after": f'أجب عن سؤال الاختيار المتعدد المحدد واعرض عملك. يمكن أن تكون الإجابة خيارًا فقط مثل {self.ar_options}. يتعين عليك إخراج الإجابة في الجملة الأخيرة مثل "لذلك، الإجابة هي ...".',
            }.get(prompt_type, "unknown prompt type")
        else:
            prompt = "unknown language"

        return prompt, question_mark, answer_mark



class SystemPrompt:
    def __init__(self, i_lang, t_lang, role_type=None):
        self.i_lang = i_lang
        self.t_lang = t_lang
        self.role_type = role_type
    
    def persona_prompt(self):
        if self.i_lang == "en":
            if self.t_lang == "en":
                persona = "an English speaker"
            elif self.t_lang == "ko":
                persona = "a Korean speaker"
            elif self.t_lang == "zh":
                persona = "a Chinese speaker"
            elif self.t_lang == "ar":
                persona = "an Arabic speaker"
            else:
                print("Wrong Language")
        elif self.i_lang == "ko":
            if self.t_lang == "en":
                persona = "영어 화자"
            elif self.t_lang == "ko":
                persona = "한국어 화자"
            else:
                print("Wrong Language")
        elif self.i_lang == "zh":
            if self.t_lang == "en":
                persona = "英语使用者"
            elif self.t_lang == "zh":
                persona = "中文使用者"
            else:
                print("Wrong Language")
        elif self.i_lang == "ar":
            if self.t_lang == "en":
                persona = "متحدث باللغة الانجليزية"
            elif self.t_lang == "ar":
                persona = "متحدث باللغة العربية"
            else:
                print("Wrong Language")
        else:
            print("Wrong Language")
        
        if self.role_type == "adopt":
            if self.i_lang == "en":
                prompt = f"Adopt the identity of {persona}. Answer the questions while staying in strict accordance with the nature of this identity."
            elif self.i_lang == "ko":
                prompt = f"{persona}의 정체성을 취해라. 질문에 답할 때 {persona}의 특성을 충실하게 따라라."
            elif self.i_lang == "zh":
                prompt = f"采用{persona}的身份。严格按照此身份的性质回答问题"
            elif self.i_lang == "ar":
                prompt = f"تبنى هوية {persona}. أجب عن الأسئلة مع الالتزام التام بطبيعة هذه الهوية."
            else:
                print("Wrong Language")

        elif self.role_type == "take":
            if self.i_lang == "en":
                prompt = f"Take the role of {persona}. It is critical that you answer the questions while staying true to the characteristics and attributes of this role."
            elif self.i_lang == "ko":
                prompt = f"{persona}의 역할을 해라. 질문에 답할 때 {persona}의 특성과 속성을 유지하는 것이 중요하다."
            elif self.i_lang == "zh":
                prompt = f"扮演{persona}的角色。回答问题时，务必要忠实于该角色的特征和属性。"
            elif self.i_lang == "ar":
                prompt = f"قم بدور {persona}. من الضروري أن تجيب على الأسئلة مع الالتزام بخصائص وصفات هذا الدور."
            else:
                print("Wrong Language")

        elif self.role_type == "you":
            if self.i_lang == "en":
                prompt = f"You are {persona}. Your responses should closely mirror the knowledge and abilities of this persona."
            elif self.i_lang == "ko":
                prompt = f"당신은 {persona}이다. 당신은 {persona}의 지식과 능력을 밀접하게 반영하여 응답해야 한다."
            elif self.i_lang == "zh":
                prompt = f"您是{persona}。您的回答应该与该角色的知识和能力相符。"
            elif self.i_lang == "ar":
                prompt = f"أنت {persona}. يجب أن تعكس ردودك بشكل وثيق المعرفة والقدرات الخاصة بهذه الشخصية."
            else:
                print("Wrong Language")
        return prompt

    
    def IT_prompt(self):
        if self.i_lang == "en":
            if self.t_lang == "en":
                return "Think in English."
            elif self.t_lang == "ko":
                return "Think in Korean."
            elif self.t_lang == "zh":
                return "Think in Chinese."
            elif self.t_lang == "ar":
                return "Think in Arabic."
            else:
                print("Wrong Language")
        elif self.i_lang == "ko":
            if self.t_lang == "en":
                return "영어로 생각하시오."
            elif self.t_lang == "ko":
                return "한국어로 생각하시오."
            else:
                print("Wrong Language")
        elif self.i_lang == "zh":
            if self.t_lang == "en":
                return "用英语思考。"
            elif self.t_lang == "zh":
                return "用中文思考。"
            else:
                print("Wrong Language")
        elif self.i_lang == "ar":
            if self.t_lang == "en":
                return "فكر باللغة الانجليزية."
            elif self.t_lang == "ar":
                return "فكر باللغة العربية."
            else:
                print("Wrong Language")
        else:
            print("Wrong Language")
    
    def ITO_prompt(self):
        if self.i_lang == "en":
            if self.t_lang == "ko":
                cross_think_instruct = "Think in Korean and answer in English."
            elif self.t_lang == "zh":
                cross_think_instruct = "Think in Chinese and answer in English."
            elif self.t_lang == "ar":
                cross_think_instruct = "Think in Arabic and answer in English."
            else:
                print("Wrong Language")
        elif self.i_lang == "ko":
            if self.t_lang == "en":
                cross_think_instruct = "영어로 생각하고 한국어로 답하시오."
            else:
                print("Wrong Language")
        elif self.i_lang == "zh":
            if self.t_lang == "en":
                cross_think_instruct = "用英语思考，用中文回答。"
        elif self.i_lang == "ar":
            if self.t_lang == "en":
                cross_think_instruct = "فكر باللغة الإنجليزية وأجب باللغة العربية."
        else:
            print("Wrong Language")
        return cross_think_instruct



def generate_prompt(q_lang, i_lang, t_lang, role_type, user_prompt_type, prompt_type, query, data_name):
    user_prompt = UserPrompt(data_name, q_lang)
    system_prompt = SystemPrompt(i_lang, t_lang, role_type)

    # User prompts
    u_i, q_mark, a_mark = user_prompt.get_prompt(user_prompt_type)
    if user_prompt_type == "long_after":
        u_p = f"{u_i}\n\n{q_mark}: {query}"
    else:
        u_p = f"{u_i}\n\n{q_mark}: {query}\n{a_mark}:"
    
    # System prompts
    if prompt_type == "I":
        s_p = None
    elif prompt_type == "IT":
        s_p = system_prompt.IT_prompt()
    elif prompt_type == "ITO":
        s_p = system_prompt.ITO_prompt()
    elif prompt_type == "persona":
        s_p = system_prompt.persona_prompt()
    else:
        print("Wrong prompt type")

    # 메시지 구성
    if prompt_type == "I":
        messages = [
            {"role": "user", "content": u_p}
        ]
    else:
        messages = [
            {"role": "system", "content": s_p},
            {"role": "user", "content": u_p}
        ]

    return messages