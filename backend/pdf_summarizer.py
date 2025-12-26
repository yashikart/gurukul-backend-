"""
Multi-Page PDF Summarizer using Google Gemini API
Replaces Groq to avoid Rate Limiting and leverage large context window.
"""

import os
import google.generativeai as genai
import json
from typing import List, Dict, Optional
import time

class PDFSummarizer:
    """Cloud-based PDF summarizer using Google Gemini API"""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("[PDF Summarizer] WARNING: GEMINI_API_KEY not found in environment variables.")
        else:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test model validity with a dummy call
                # self.model.generate_content("test") 
            except Exception as e:
                print(f"[PDF Summarizer] Warning: Failed to load model '{model_name}': {e}. Falling back to 'gemini-pro'...")
                self.model = genai.GenerativeModel("gemini-pro")

    def summarize_all_pages(self, pages: List[str], summary_type: str = "detailed", improve_grammar: bool = False) -> Dict:
        """
        Summarize ALL pages in a single API call using Gemini's large context window.
        Returns a dictionary matching the expected structure.
        """
        if not self.api_key:
            return {
                "page_summaries": [],
                "overall_summary": "Error: GEMINI_API_KEY not configured.",
                "total_pages": len(pages),
                "pages_summarized": 0,
                "summary_type": summary_type
            }

        print(f"[PDF Summarizer] Preparing to summarize {len(pages)} pages using Gemini...")

        # 1. Construct a single large prompt with all page content
        full_text_content = ""
        for i, page_text in enumerate(pages, 1):
            full_text_content += f"\n--- START OF PAGE {i} ---\n{page_text}\n--- END OF PAGE {i} ---\n"

        # 2. Define the prompt for structured JSON output
        prompt = f"""
        You are an expert document summarizer. 
        I will provide the text content of a PDF document, separated by page markers.
        
        Your task is to:
        1. Create a detailed overall summary of the ENTIRE document.
        2. Create a brief summary for EACH individual page.
        
        Output format: JSON object with keys "overall_summary" (string) and "page_summaries" (list of strings, in page order).
        
        Summary requirements:
        - Overall summary should be comprehensive, capturing all key points, arguments, and conclusions.
        - Page summaries should be concise (2-3 sentences max).
        - Maintain the original meaning and context.
        - Do not use markdown formatting in the JSON JSON string values.
        
        Document Content:
        {full_text_content}
        """

        try:
            # 3. Call Gemini API
            # 3. Call Gemini API
            print("[PDF Summarizer] Sending request to Gemini...")
            try:
                response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            except Exception as e:
                # Dynamic fallback for "404 Model Not Found" errors during runtime
                if "404" in str(e) or "not found" in str(e).lower():
                    print("[PDF Summarizer] Primary model failed (404). Switching to fallback 'gemini-pro' and retrying...")
                    self.model = genai.GenerativeModel("gemini-pro")
                    response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                else:
                    raise e
            
            # 4. Parse Response
            try:
                result = json.loads(response.text)
                overall_summary = result.get("overall_summary", "Summary generation failed to return overall summary.")
                raw_page_summaries = result.get("page_summaries", [])
            except json.JSONDecodeError:
                # Fallback if valid JSON wasn't returned
                print("[PDF Summarizer] Failed to parse JSON response. Falling back to raw text.")
                overall_summary = response.text
                raw_page_summaries = []

            # 5. Format output for existing backend structure
            formatted_page_summaries = []
            
            # Map raw summaries back to pages (handle mismatches gracefully)
            for i, page_text in enumerate(pages, 1):
                raw_summary = raw_page_summaries[i-1] if i <= len(raw_page_summaries) else "Summary not generated for this page."
                
                formatted_page_summaries.append({
                    "page_number": i,
                    "summary": raw_summary,
                    "original_length": len(page_text) if page_text else 0,
                    "summary_length": len(raw_summary)
                })

            print("[PDF Summarizer] Gemini processing complete!")
            
            return {
                "page_summaries": formatted_page_summaries,
                "overall_summary": overall_summary,
                "total_pages": len(pages),
                "pages_summarized": len(formatted_page_summaries),
                "summary_type": summary_type
            }

        except Exception as e:
            print(f"[PDF Summarizer] Error calling Gemini: {str(e)}")
            return {
                "page_summaries": [],
                "overall_summary": f"Error during summarization: {str(e)}",
                "total_pages": len(pages),
                "pages_summarized": 0,
                "summary_type": summary_type
            }
