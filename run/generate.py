### The code will be publicly released on GitHub after the paper is accepted.

import pandas as pd
import numpy as np
import random
import os
import sys
import glob
from tqdm import tqdm
import argparse
import logging
from datasets import Dataset
from transformers import set_seed
import torch
from langdetect import detect
import prompt as p
import model_llama as ml
import model_openai as mo
import model_peft as mp
import model_vllm as mv
import eval_zh as ez
import eval_ko as ek
import eval_ar as ea


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_data(dataset_dir):
    dataset_paths = glob.glob(os.path.join(dataset_dir, '*.csv'))
    dataset_paths.sort()

    return dataset_paths


def build_output_dir(args, data_language):
    """Build the output directory path based on the input arguments."""
    role_part = f"/{args.role_type}" if args.role_type is not None else ""
    directory = (
        f"{args.output_dir}/{data_language}/{args.model_name}/"
        f"{args.user_prompt_type}/{args.prompt_type}{role_part}/"
        f"Q{args.q_lang}_I{args.i_lang}_T{args.t_lang}/seed{args.seed}"
    )
    return directory


def setup_logger(directory):
    """Setup logger with both console and file handlers."""
    logger = logging.getLogger("inference")
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(os.path.join(directory, "log.txt"), encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(file_handler)
    return logger


def infer_llm(args, messages, tokenizer=None, model=None, client=None, model_id=None):
    """
    Infer response from the LLM based on the model type.
    
    Returns:
        model_input: The input fed to the model.
        llm_guess: The generated response from the LLM.
    """
    if (args.model_type == "llama") or (args.model_type == "peft"): 
        if args.model_type == "llama":
            prompt, response = ml.llama_infer(args.quant, tokenizer, model, messages)
        else :
            prompt, response = mp.peft_infer(tokenizer, model, messages)

        if args.quant:
            llm_guess = response["choices"][0]["text"][len(prompt):]
        else:
            llm_guess = response[0][prompt.shape[-1]:]
            llm_guess = tokenizer.decode(llm_guess, skip_special_tokens=True)
            prompt = tokenizer.decode(prompt[0])

        model_input = prompt

    elif args.model_type == "openai":
        response = mo.openai_infer(client, model_id, messages)
        llm_guess = response.choices[0].message.content
        model_input = messages

    elif args.model_type == "vllm":
        prompt, response = mv.vllm_infer(tokenizer, model, messages)
        llm_guess = response[0].outputs[0].text
        model_input = prompt

    else:
        raise ValueError("Wrong Model")
    
    return model_input, llm_guess


def main(args):
    # Get the dataset language from the dataset directory name
    data_language = args.dataset_dir.split("/")[-1]

    # Build and create the output directory
    directory = build_output_dir(args, data_language)
    os.makedirs(directory, exist_ok=True)

    # Redirect stdout to the log file
    log_path = os.path.join(directory, "log.txt")
    sys.stdout = open(log_path, "w", encoding="utf-8")

    # Setup logger
    logger = setup_logger(directory)

    # Log input arguments
    logger.info("====== Arguments ======")
    for k, v in vars(args).items():
        logger.info(f"{k:25}: {v}")

    # Set random seed
    logger.info(f"[+] Set Random Seed to {args.seed}")
    set_seed(args.seed)

    # Load model based on model type
    logger.info("[+] Loading Model")
    if args.model_type == "llama":
        tokenizer, model = ml.llama_load(args.quant, args.model_id, args.model_path, args.model_name)
    elif args.model_type == "openai":
        client, model_id = mo.openai_load(args.model_id)
    elif args.model_type == "peft":
        tokenizer, model = mp.peft_load(args.model_id)
    elif args.model_type == "vllm":
        tokenizer, model = mv.vllm_load(args.quant, args.model_id, args.model_name, args.seed)
    else:
        logger.error("Wrong Model")
        return

    dataset_paths = get_data(args.dataset_dir)

    data_count = 0
    lang_en = lang_original = else_lang = 0
    correct_count = 0
    extraction_failure_count = 0

    # Process each dataset file
    for dataset_path in dataset_paths:
        base_name = os.path.basename(dataset_path).replace(".csv", "")
        output_file = os.path.join(directory, f"{base_name}_output.csv")

        logger.info(f"[+] Processing {dataset_path}")
        dataset = Dataset.from_csv(dataset_path)
        results = []
        data_count += len(dataset)

        # Process each data entry with a progress bar
        for i in tqdm(range(len(dataset)), desc="Processing data"):
            input_query = dataset[args.q_lang][i]
            answer = dataset["answer"][i]

            # Generate prompt for the given query
            messages = p.generate_prompt(
                args.q_lang, args.i_lang, args.t_lang, args.role_type,
                args.user_prompt_type, args.prompt_type, input_query, base_name
            )
            if i == 0:
                logger.info(f"Prompt example:\n{messages}")

            # Get LLM response
            try:
                if args.model_type == "openai":
                    model_input, llm_guess = infer_llm(
                        args, messages, client=client, model_id=model_id
                    )
                else:
                    model_input, llm_guess = infer_llm(
                        args, messages, tokenizer=tokenizer, model=model
                    )
            except Exception as e:
                logger.error(f"Error during inference: {e}")
                continue

            # Detect language of the LLM response
            try:
                response_lang = detect(llm_guess)
            except Exception as e:
                response_lang = ""

            # Update language counters
            if response_lang == "en":
                lang_en += 1
            elif response_lang == data_language:
                lang_original += 1
            elif response_lang:
                else_lang += 1

            # Extract answer and check correctness
            try:
                if args.dataset_dir.split('/')[-1] == "zh":
                    predicted_answer = ez.answer_extraction(
                        args.user_prompt_type, llm_guess, response_lang
                    )
                    correct_count += int(ek.check_equal(answer, predicted_answer))
                elif args.dataset_dir.split('/')[-1] == "ko":
                    predicted_answer = ek.answer_extraction(
                        args.user_prompt_type, llm_guess, response_lang
                    )
                    correct_count += int(ez.check_equal(answer, predicted_answer))
                elif args.dataset_dir.split('/')[-1] == "ar":
                    predicted_answer = ea.answer_extraction(
                        args.user_prompt_type, llm_guess, response_lang, model_input, answer
                    )
                    correct_count += int(ea.check_equal(answer, predicted_answer))
                else:
                    raise ValueError("Wrong Dataset")

                
            except Exception as e:
                predicted_answer = ""

            if predicted_answer is None:
                extraction_failure_count += 1

            # Append the result
            results.append({
                "input": model_input,
                "answer": answer,
                "LLM response": llm_guess,
                "response_lang": response_lang,
                "predicted_answers": predicted_answer
            })

            if i == 0:
                logger.info(f"Response example:\n{llm_guess}")

        # Save results to a CSV file
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)
        logger.info(f"[+] Output saved to \"{output_file}\"")

    # Log overall statistics
    logger.info(f"[+] Data Count: {data_count}")
    logger.info(
        f"[+] Original Language Ratio: {lang_original / data_count:.4f}, "
        f"English Ratio: {lang_en / data_count:.4f}, Other Count: {else_lang}"
    )
    logger.info(f"[+] Correct Count: {correct_count}")
    logger.info(f"[+] Extraction Failure Count: {extraction_failure_count}")
    logger.info(f"[+] Accuracy: {correct_count / data_count:.4f}")

    sys.stdout.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("Common Parameter")
    g.add_argument("--quant", type=str, default="False", help="quantization")
    g.add_argument("--model-type", type=str, default="openai", choices=["llama", "openai", "peft", "vllm"], help="model type")
    g.add_argument("--huggingface-token", type=str, default="", help=" your huggingface token")
    g.add_argument("--output-dir", type=str, default="../results", help="output directory path")
    g.add_argument("--model-id", type=str, default="meta-llama/Meta-Llama-3-70B-Instruct", help="model id")
    g.add_argument("--model-path", type=str, default="../../../Models/llama3.1_gguf/", help="model file path")
    g.add_argument("--model-name", type=str, default="Meta-Llama-3-70B-Instruct.IQ4_XS.gguf", help="model file path")
    g.add_argument("--seed", type=int, default=1, help="random seed")
    g.add_argument("--dataset-dir", type=str, default="../dataset/ko", help="dataset directory path")
    g.add_argument("--user-prompt-type", type=str, default="long_after", choices=["short", "long", "long_after"], help="user prompt type")
    g.add_argument("--prompt-type", type=str, default="I", choices=["I", "IT", "ITO", "persona"], help="system prompt type") 
    g.add_argument("--q-lang", type=str, default="ko", choices=["en", "ko", "zh", "ar"], help="question language")
    g.add_argument("--i-lang", type=str, default="ko", choices=["en", "ko", "zh", "ar"], help="instruction language")
    g.add_argument("--t-lang", type=str, default="ko", choices=["en", "ko", "zh", "ar"], help="think language")
    g.add_argument("--role-type", type=str, default=None, choices=[None, "adopt", "take", "you"], help="persona type")

    args = parser.parse_args()

    main(args)