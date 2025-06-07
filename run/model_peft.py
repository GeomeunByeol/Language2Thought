from transformers import AutoTokenizer
from peft import AutoPeftModelForCausalLM


def peft_load(model_id):
    model_checkpoint = model_id

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

    model = AutoPeftModelForCausalLM.from_pretrained(model_checkpoint, max_length=1024).to("cuda")
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to("cuda")



    return tokenizer, model


def peft_infer(tokenizer, model, messages):
    input_ids = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
                )
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    input_ids = input_ids.to("cuda")

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    outputs = model.generate(
        input_ids,
        max_new_tokens=1024,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )

    return input_ids, outputs