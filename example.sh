python ./run/generate.py --quant "True" \
    --huggingface-token "YOUR_HUGGINGFACE_TOKEN" \
    --model-type "llama" \
    --model-id "meta-llama/Llama-3.1-8B-Instruct" \
    --seed "$seed" \
    --dataset-dir "./dataset/ko" \
    --prompt-type "I" \
    --q-lang "en" \
    --i-lang "en" \
    --t-lang "en"
