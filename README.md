# Language2Thought
This is the official code repository for the paper: *When Language Shapes Thought: Cross-Lingual Transfer of Factual Knowledge in Question Answering*

Accepted to CIKM2025 (link will be available soon) \
[Arxiv Link](https://www.arxiv.org/abs/2505.24409) (expanded verion)

Code will be updated.

## Setup
```bash
git clone https://github.com/GeomeunByeol/Language2Thought.git
cd Language2Thought

conda create -n L2T python==3.11
conda activate L2T
pip install -r requirements.txt
```

### Optional dependencies
- Using gguf model (with CUDA)
```bash
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
```

- Using OpenAI model
```bash
pip install openai
```

- Using VLLM
```bash
pip install vllm
```

- Using PEFT (Adapter)
```bash
pip install peft
```

## Run
Quick start with the provided script
```bash
chmod +x example.sh
./example.sh
```

```bash
python ./src/generate.py --quant "True" \
    --huggingface-token "YOUR_HUGGINGFACE_TOKEN" \  
    --model-type "llama" \
    --model-id "meta-llama/Llama-3.1-8B-Instruct" \
    --seed "$seed" \
    --dataset-dir "../dataset/ko" \
    --prompt-type "I" \ 
    --q-lang "en" \  # "en" or "zh" or "ko" or "ar"
    --i-lang "en" \
    --t-lang "en"
```
### prompt-type 
- "I": baseline (q-lang == t-lang)
- "IT": L2T-Consistent or L2T-Transfer (q-lang == t-lang -> L2T-Consistent, q-lang != t-lang -> L2T-Transfer)
- "ITO": L2T-Align (q-lang != t-lang)


## References (Dataset)
- [CLIcK: A Benchmark Dataset of Cultural and Linguistic Intelligence in Korean](https://aclanthology.org/2024.lrec-main.296/)
- [SeaEval for Multilingual Foundation Models: From Cross-Lingual Alignment to Cultural Reasoning](https://aclanthology.org/2024.naacl-long.22/)
- [CMMLU: Measuring massive multitask language understanding in Chinese](https://arxiv.org/abs/2306.09212)
- [ArabicMMLU: Assessing Massive Multitask Language Understanding in Arabic](https://aclanthology.org/2024.findings-acl.334/)
