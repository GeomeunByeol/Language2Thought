from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


def llama_load(quant, model_id, model_path, model_name):
    if quant == "True":
        from llama_cpp import Llama
        # Use llama.cpp for GGUF quantization
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = Llama(
            model_path=model_path+model_name,
            n_gpu_layers=-1,
            n_ctx=1024,
            n_batch=1024,
            verbose=False
            )
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_id)

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            # torch_dtype=torch.bfloat16,    # Optional: Select appropriate torch data type
            torch_dtype=torch.float16,
            # device_map="auto",
        )
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model.to("cuda")



    return tokenizer, model


def llama_infer(quant, tokenizer, model, messages):
    if quant == "True":
        generation_kwargs = {
            "max_tokens": 1024,
            "stop": ["<|eot_id|>"],
            "echo": True,
            # "temperature": 0.6,  
            # "top_p": 0.9
            }
    
        prompt = tokenizer.apply_chat_template(
                messages, 
                tokenize = False,
                add_generation_prompt=True
            )
    
        outputs = model(prompt, **generation_kwargs)

        return prompt, outputs

    else:
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