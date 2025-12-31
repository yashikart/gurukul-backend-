"""
Download model pickle files on startup if they don't exist
This runs automatically when the app starts on Render
"""

import os
import requests
import re
from pathlib import Path
import sys

def convert_google_drive_url(url: str) -> str:
    """Convert Google Drive share URL to direct download URL"""
    if "drive.google.com" in url:
        # Extract file ID from various Google Drive URL formats
        file_id = None
        
        # Format 1: https://drive.google.com/file/d/FILE_ID/view
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        # Format 2: https://drive.google.com/open?id=FILE_ID
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        # Format 3: Already direct download format
        elif "uc?export=download" in url:
            return url
        
        if file_id:
            # Convert to direct download URL
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            print(f"[Download] Converted Google Drive URL to direct download format")
            return direct_url
    
    return url

def download_file(url: str, filepath: Path, description: str = "file", expected_min_size_mb: float = 1.0):
    """Download a file from URL with validation"""
    try:
        # Convert Google Drive URLs to direct download format
        url = convert_google_drive_url(url)
        
        print(f"[Download] Downloading {description} from {url}...")
        
        # Use a session to handle Google Drive's virus scan warning
        session = requests.Session()
        
        # First, make a non-streaming request to check if we get the warning page
        response = session.get(url, stream=False, timeout=300, allow_redirects=True)
        response.raise_for_status()
        
        # Handle Google Drive virus scan warning page
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            # Check if it's the virus scan warning page
            text_lower = response.text.lower()
            if ("virus scan warning" in text_lower or 
                "download anyway" in text_lower or 
                "google drive can't scan" in text_lower or
                "this file is too large" in text_lower):
                
                print(f"[Download] Detected Google Drive virus scan warning page. Extracting download link...")
                
                # Method 1: Look for the form action with download link
                # The warning page has a form with action="/uc?export=download&id=..."
                form_action_match = re.search(r'action="(/uc\?export=download[^"]+)"', response.text)
                if form_action_match:
                    download_url = "https://drive.google.com" + form_action_match.group(1)
                    print(f"[Download] Found download link in form action")
                else:
                    # Method 2: Look for direct download link in href
                    href_match = re.search(r'href="(/uc\?export=download[^"]+)"', response.text)
                    if href_match:
                        download_url = "https://drive.google.com" + href_match.group(1)
                        print(f"[Download] Found download link in href")
                    else:
                        # Method 3: Extract from the page - look for the download button link
                        # Sometimes it's in a data attribute or JavaScript
                        js_match = re.search(r'/uc\?export=download[^"\'>\s]+', response.text)
                        if js_match:
                            download_url = "https://drive.google.com" + js_match.group(0)
                            print(f"[Download] Found download link in page content")
                        else:
                            print(f"[Download] ✗ Could not extract download link from warning page")
                            print(f"[Download] Trying alternative method: adding confirm parameter...")
                            # Alternative: Add confirm parameter to bypass warning
                            if "id=" in url:
                                file_id = url.split("id=")[1].split("&")[0]
                                download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
                            else:
                                return False
                
                # Now download from the actual file URL with streaming
                print(f"[Download] Downloading from actual file URL...")
                response = session.get(download_url, stream=True, timeout=300, allow_redirects=True)
                response.raise_for_status()
                
                # Verify we got a file, not HTML
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type:
                    print(f"[Download] ✗ Still receiving HTML. File might be too large or link is incorrect.")
                    return False
            else:
                # It's HTML but not the warning page - probably wrong URL
                print(f"[Download] ⚠ WARNING: Received HTML instead of file. URL might be incorrect.")
                print(f"[Download] Make sure you're using direct download URLs, not share links.")
                return False
        else:
            # Not HTML, should be the file - make a streaming request
            response = session.get(url, stream=True, timeout=300, allow_redirects=True)
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
                        if downloaded % (10 * 1024 * 1024) == 0:  # Print every 10 MB
                            print(f"[Download] {description}: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)")
        
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        
        # Validate file size
        if file_size_mb < expected_min_size_mb:
            print(f"[Download] ✗ ERROR: Downloaded file is too small ({file_size_mb:.2f} MB). Expected at least {expected_min_size_mb:.2f} MB.")
            print(f"[Download] This usually means the URL is incorrect or the file is corrupted.")
            filepath.unlink()  # Delete corrupted file
            return False
        
        print(f"[Download] ✓ {description} downloaded successfully! ({file_size_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"[Download] ✗ Failed to download {description}: {str(e)}")
        if filepath.exists():
            filepath.unlink()  # Delete partial/corrupted file
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
            success = download_file(model_url, model_file, "model pickle", expected_min_size_mb=100.0) and success
        
        if not tokenizer_file.exists():
            success = download_file(tokenizer_url, tokenizer_file, "tokenizer pickle", expected_min_size_mb=0.3) and success
        
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

