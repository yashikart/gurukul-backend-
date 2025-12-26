"""
Multi-Page PDF Summarizer using Groq Cloud API
Replaces local transformers to avoid Memory Crash on Free Tier Hosting.
"""

import os
import requests
import json
from typing import List, Dict, Optional
import time

class PDFSummarizer:
    """Cloud-based PDF summarizer using Groq API"""
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = os.getenv("GROQ_API_ENDPOINT", "https://api.groq.com/openai/v1/chat/completions")
        self.model_name = os.getenv("GROQ_MODEL_NAME", model_name)
        
        if not self.api_key:
            print("[PDF Summarizer] WARNING: GROQ_API_KEY not found in environment variables.")

    def _call_groq(self, text: str, prompt_type: str = "summarize", target_length: str = "detailed") -> str:
        """Helper to call Groq API"""
        if not self.api_key:
            return "Error: GROQ_API_KEY not configured."

        system_prompt = "You are an expert summarizer. Analyze the text and provide a high-quality summary."
        
        if prompt_type == "summarize":
            user_prompt = f"""
Please provide a {target_length} summary of the following text from a page of a document.
Focus on the key points, main arguments, and important details.
Do not add preamble like "Here is the summary". just give the summary directly.

Text to summarize:
{text[:15000]} 
""" # Limit to 15k chars to be safe 
        elif prompt_type == "overall":
            user_prompt = f"""
Here are summaries of multiple pages from a document. 
Please synthesize them into one cohesive, comprehensive overall summary of the entire document.
Ensure smooth flow and logical structure.
Target Length: {target_length}

Page Summaries:
{text[:20000]}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 2048
        }
        
        try:
            # Simple retry mechanism with Exponential Backoff
            for attempt in range(3):
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    wait_time = 3 * (attempt + 1)
                    print(f"[PDF Summarizer] Rate limit hit. Retrying in {wait_time}s...")
                    time.sleep(wait_time) # Exponential backoff
                    continue
                else:
                    return f"API Error: {response.text}"
            return "Error: Failed to get response from Groq API after retries"
        except Exception as e:
            return f"Error: {str(e)}"

    def summarize_page(self, page_text: str, page_num: int, **kwargs) -> str:
        """Summarize a single page"""
        if not page_text or len(page_text.strip()) < 50:
            return f"[Page {page_num}]: Insufficient content"
            
        summary_type = kwargs.get('summary_type', 'detailed')
        print(f"[PDF Summarizer] Summarizing Page {page_num} via Groq...")
        
        return self._call_groq(page_text, prompt_type="summarize", target_length=summary_type)

    def summarize_all_pages(self, pages: List[str], summary_type: str = "detailed", improve_grammar: bool = True) -> Dict:
        """Summarize all pages"""
        page_summaries = []
        
        # Process each page
        for i, page_text in enumerate(pages, 1):
            summary = self.summarize_page(page_text, i, summary_type=summary_type)
            page_summaries.append({
                "page_number": i,
                "summary": summary,
                "original_length": len(page_text) if page_text else 0,
                "summary_length": len(summary)
            })
            # Small delay to avoid rate limits
            time.sleep(0.5)
            
        # Create overall summary
        valid_summaries = [ps['summary'] for ps in page_summaries if "Error" not in ps['summary']]
        combined_text = "\n\n".join(valid_summaries)
        
        if combined_text:
            print("[PDF Summarizer] Generating Overall Summary via Groq...")
            overall_summary = self._call_groq(combined_text, prompt_type="overall", target_length=summary_type)
        else:
            overall_summary = "Could not generate overall summary."

        return {
            "page_summaries": page_summaries,
            "overall_summary": overall_summary,
            "total_pages": len(pages),
            "pages_summarized": len(page_summaries),
            "summary_type": summary_type
        }
