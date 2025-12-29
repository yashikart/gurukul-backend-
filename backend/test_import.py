import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Current Directory: {os.getcwd()}")

try:
    print("Attempting to import google.generativeai...")
    import google.generativeai
    print("SUCCESS: google.generativeai imported.")
except ImportError as e:
    print(f"FAILURE: google.generativeai could not be imported. Error: {e}")

try:
    print("Attempting to import PDFSummarizer from pdf_summarizer...")
    from pdf_summarizer import PDFSummarizer
    print("SUCCESS: PDFSummarizer imported.")
    
    # Try instantiation to check for init errors
    print("Attempting to instantiate PDFSummarizer...")
    summ = PDFSummarizer()
    print("SUCCESS: PDFSummarizer instantiated.")
    
except Exception as e:
    print(f"FAILURE: PDFSummarizer error. Error: {e}")
    import traceback
    traceback.print_exc()
