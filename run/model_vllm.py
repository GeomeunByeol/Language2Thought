from transformers import AutoTokenizer
import torch
from vllm import LLM, SamplingParams


def vllm_load(quant, model_id, model_name, seed):
    base_checkpoint = model_id
    adapter_checkpoint = model_name

    tokenizer = AutoTokenizer.from_pretrained(base_checkpoint)
    if quant == "True":  # Applicable to models trained using QLoRA
        llm = LLM(
            model=adapter_checkpoint, 
            tokenizer=base_checkpoint, 
            gpu_memory_utilization=0.85,
            trust_remote_code=True,
            dtype=torch.bfloat16, 
            quantization="bitsandbytes", 
            load_format="bitsandbytes", 
            max_model_len=8000, 
            seed=seed
        )
    else:        
        llm = LLM(
            model=base_checkpoint,
            tokenizer=base_checkpoint, 
            seed=seed
        )
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # llm.to("cuda")


    return tokenizer, llm


def vllm_infer(tokenizer, model, messages):
    messages = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)

    sampling_params = SamplingParams(temperature=0.6, top_p=0.9, max_tokens=1024)

    outputs = model.generate(messages,sampling_params)

    return messages, outputs