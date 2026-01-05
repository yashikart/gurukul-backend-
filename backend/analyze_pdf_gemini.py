
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

def analyze_pdf(pdf_path):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        with open("task_list.txt", "w") as f:
            f.write("Error: GEMINI_API_KEY not found in .env")
        return

    genai.configure(api_key=api_key)
    
    try:
        print("Uploading file...")
        pdf_file = genai.upload_file(pdf_path, mime_type="application/pdf")
        
        while pdf_file.state.name == "PROCESSING":
            time.sleep(2)
            pdf_file = genai.get_file(pdf_file.name)
            
        if pdf_file.state.name == "FAILED":
             with open("task_list.txt", "w") as f:
                f.write("File processing failed.")
             return

        print("Generating content...")
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content([pdf_file, "List all the tasks that need to be done from this document. Just list them clearly as bullet points."])
        
        with open("task_list.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        pdf_file.delete()
        
    except Exception as e:
        with open("task_list.txt", "w") as f:
            f.write(f"Error calling Gemini: {e}")

if __name__ == "__main__":
    pdf_path = r"c:\Users\pc45\Desktop\Gurukul\1766874937125-Soham K Gurukul Finalisation Task.pdf"
    analyze_pdf(pdf_path)
