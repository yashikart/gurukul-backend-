
import PyPDF2
import sys

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"Total Pages: {len(reader.pages)}")
            for i, page in enumerate(reader.pages):
                print(f"--- Page {i+1} ---")
                text = page.extract_text()
                if text:
                     print(text)
                else:
                     print("(No text extracted)")
            print("--- End of extraction ---")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    pdf_path = r"c:\Users\pc45\Desktop\Gurukul\1766874937125-Soham K Gurukul Finalisation Task.pdf"
    extract_text_from_pdf(pdf_path)
