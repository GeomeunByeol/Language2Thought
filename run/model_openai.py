from openai import OpenAI

def openai_load(model_id):
    client = OpenAI()
    return client, model_id


def openai_infer(client, model_id, messages):
    completion = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=1024)
    
    return completion