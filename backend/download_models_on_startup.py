"""
Download model pickle files on startup if they don't exist
This runs automatically when the app starts on Render
"""

import os
import requests
from pathlib import Path
import sys

def download_file(url: str, filepath: Path, description: str = "file"):
    """Download a file from URL"""
    try:
        print(f"[Download] Downloading {description} from {url}...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Print every MB
                            print(f"[Download] {description}: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)")
        
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"[Download] ✓ {description} downloaded successfully! ({file_size_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"[Download] ✗ Failed to download {description}: {str(e)}")
        return False

def ensure_models_exist():
    """Ensure model pickle files exist, download if missing"""
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    model_file = models_dir / "led_model_quantized.pkl.gz"
    tokenizer_file = models_dir / "tokenizer.pkl.gz"
    
    # Get download URLs from environment variables
    model_url = os.getenv("MODEL_PICKLE_URL")
    tokenizer_url = os.getenv("TOKENIZER_PICKLE_URL")
    
    # Check if files already exist
    if model_file.exists() and tokenizer_file.exists():
        model_size = model_file.stat().st_size / (1024 * 1024)
        tokenizer_size = tokenizer_file.stat().st_size / (1024 * 1024)
        print(f"[Models] Model files already exist:")
        print(f"  - led_model_quantized.pkl.gz: {model_size:.2f} MB")
        print(f"  - tokenizer.pkl.gz: {tokenizer_size:.2f} MB")
        return True
    
    # If URLs are provided, download files
    if model_url and tokenizer_url:
        print("[Models] Model files not found. Downloading from URLs...")
        success = True
        
        if not model_file.exists():
            success = download_file(model_url, model_file, "model pickle") and success
        
        if not tokenizer_file.exists():
            success = download_file(tokenizer_url, tokenizer_file, "tokenizer pickle") and success
        
        if success:
            print("[Models] ✓ All model files downloaded successfully!")
            return True
        else:
            print("[Models] ⚠ Some files failed to download. App will use HuggingFace fallback.")
            return False
    else:
        print("[Models] ⚠ Model files not found and download URLs not configured.")
        print("[Models] Set MODEL_PICKLE_URL and TOKENIZER_PICKLE_URL environment variables.")
        print("[Models] App will use HuggingFace fallback (may be slow).")
        return False

if __name__ == "__main__":
    ensure_models_exist()

