
# GGUF Quantization Guide for Smart Traffic FLAN-T5 Alert Generator
# ================================================================
# Run these commands AFTER fine-tuning (finetune_flan_t5() completed)

# Step 1: Install llama.cpp (one-time setup)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build && cmake --build build --config Release

# Step 2: Convert fine-tuned model to GGUF format
python llama.cpp/convert_hf_to_gguf.py slm_module/finetuned_flan_t5 \
    --outfile slm_module/quantized_gguf/flan_t5_traffic.gguf \
    --outtype f16

# Step 3: Quantize to 4-bit (Q4_K_M — best size/quality balance)
./llama.cpp/build/bin/llama-quantize \
    slm_module/quantized_gguf/flan_t5_traffic.gguf \
    slm_module/quantized_gguf/flan_t5_traffic_q4km.gguf \
    Q4_K_M

# Step 4: Verify compression
# Original fine-tuned model : ~300 MB (FP32)
# After f16 conversion       : ~150 MB
# After Q4_K_M quantization  : ~80  MB  (4x smaller, <2% quality loss)

echo "Quantization complete. Model ready for Ollama deployment."
