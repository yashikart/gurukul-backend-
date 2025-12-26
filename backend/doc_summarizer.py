"""
Multi-Section DOC Summarizer using Groq Cloud API
Replaces local transformers to avoid Memory Crash on Free Tier Hosting.
"""

import os
import requests
import json
from typing import List, Dict, Optional
import time

class DOCSummarizer:
    """Cloud-based DOC summarizer using Groq API"""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = os.getenv("GROQ_API_ENDPOINT", "https://api.groq.com/openai/v1/chat/completions")
        self.model_name = os.getenv("GROQ_MODEL_NAME", model_name)
        
        if not self.api_key:
            print("[DOC Summarizer] WARNING: GROQ_API_KEY not found in environment variables.")

    def _call_groq(self, text: str, prompt_type: str = "summarize", target_length: str = "detailed") -> str:
        """Helper to call Groq API"""
        if not self.api_key:
            return "Error: GROQ_API_KEY not configured."

        system_prompt = "You are an expert summarizer. Analyze the text and provide a high-quality summary."
        
        if prompt_type == "summarize":
            user_prompt = f"""
Please provide a {target_length} summary of the following section from a document.
Focus on the key points, main arguments, and important details.
Do not add preamble like "Here is the summary". just give the summary directly.

Text to summarize:
{text[:15000]} 
""" 
        elif prompt_type == "overall":
            user_prompt = f"""
Here are summaries of multiple sections from a document. 
Please synthesize them into one cohesive, comprehensive overall summary of the entire document.
Ensure smooth flow and logical structure.
Target Length: {target_length}

Section Summaries:
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
            # Simple retry mechanism
            for _ in range(3):
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    time.sleep(2) # Rate limit wait
                    continue
                else:
                    return f"API Error: {response.text}"
            return "Error: Failed to get response from Groq API after retries"
        except Exception as e:
            return f"Error: {str(e)}"

    def summarize_section(self, section_text: str, section_num: int, **kwargs) -> str:
        """Summarize a single section"""
        if not section_text or len(section_text.strip()) < 50:
            return f"[Section {section_num}]: Insufficient content"
            
        summary_type = kwargs.get('summary_type', 'detailed')
        print(f"[DOC Summarizer] Summarizing Section {section_num} via Groq...")
        
        return self._call_groq(section_text, prompt_type="summarize", target_length=summary_type)

    def summarize_all_sections(self, sections: List[str], summary_type: str = "detailed", improve_grammar: bool = True) -> Dict:
        """Summarize all sections"""
        section_summaries = []
        
        # Process each section
        for i, section_text in enumerate(sections, 1):
            summary = self.summarize_section(section_text, i, summary_type=summary_type)
            section_summaries.append({
                "section_number": i,
                "summary": summary,
                "original_length": len(section_text) if section_text else 0,
                "summary_length": len(summary)
            })
            # Small delay to avoid rate limits
            time.sleep(0.5)
            
        # Create overall summary
        valid_summaries = [ss['summary'] for ss in section_summaries if "Error" not in ss['summary']]
        combined_text = "\n\n".join(valid_summaries)
        
        if combined_text:
            print("[DOC Summarizer] Generating Overall Summary via Groq...")
            overall_summary = self._call_groq(combined_text, prompt_type="overall", target_length=summary_type)
        else:
            overall_summary = "Could not generate overall summary."

        return {
            "section_summaries": section_summaries,
            "overall_summary": overall_summary,
            "total_sections": len(sections),
            "sections_summarized": len(section_summaries),
            "summary_type": summary_type
        }
