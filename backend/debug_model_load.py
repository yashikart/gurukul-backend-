import torch
from transformers import pipeline
import sys
import traceback

print("--- DIAGNOSTIC START ---")
try:
    print(f"Python Version: {sys.version}")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"Current Memory Alloc: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
    
    print("\nAttempting to load 'google/pegasus-xsum'...")
    
    print("\nAttempting to load 'pszemraj/led-base-book-summary'...")
    
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    tokenizer = AutoTokenizer.from_pretrained("pszemraj/led-base-book-summary")
    
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            "pszemraj/led-base-book-summary", 
            torch_dtype=dtype,
            weights_only=False
        ).to(device)
    except TypeError:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            "pszemraj/led-base-book-summary", 
            torch_dtype=dtype
        ).to(device)
        
    print(f"\nSUCCESS: LED Base Model loaded on {device}!")
    
    # Re-wrap in pipeline for consistency if needed, or use manually
    # summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

except Exception as e:
    print("\n!!! ERROR LOADING MODEL !!!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    traceback.print_exc()


