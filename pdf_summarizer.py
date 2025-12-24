"""
Advanced PDF Summarizer with Multi-Page Support
Uses BART model for contextual, comprehensive summarization
"""

import torch
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer
from typing import List, Dict, Optional
import re

class PDFSummarizer:
    """Advanced PDF summarizer with multi-page support and comprehensive coverage"""
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize PDF summarizer
        
        Args:
            model_name: Hugging Face model name (default: facebook/bart-large-cnn)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.summarizer = None
        self.max_chunk_length = 1024
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization of model and tokenizer"""
        if not self._initialized:
            try:
                print(f"[PDF Summarizer] Loading model: {self.model_name}")
                self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
                self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
                self.summarizer = pipeline(
                    "summarization", 
                    model=self.model, 
                    tokenizer=self.tokenizer, 
                    framework="pt"
                )
                self._initialized = True
                print(f"[PDF Summarizer] Model loaded successfully!")
            except Exception as e:
                print(f"[PDF Summarizer] Error loading model: {str(e)}")
                raise
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _chunk_text(self, text: str, max_tokens: int = 900) -> List[str]:
        """Split text into chunks that fit within token limit"""
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.tokenizer.encode(sentence, add_special_tokens=False))
            
            if current_length + sentence_tokens > max_tokens and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_length += sentence_tokens
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def summarize_page(self, page_text: str, page_num: int, max_length: int = 150, min_length: int = 40, improve_grammar: bool = True, target_chars: int = 500) -> str:
        """Summarize a single page"""
        if not page_text or len(page_text.strip()) < 50:
            return f"[Page {page_num}]: Insufficient content"
        
        self._initialize()
        
        try:
            encoded = self.tokenizer.encode(page_text, truncation=False)
            
            if len(encoded) > self.max_chunk_length:
                # Chunk and summarize
                chunks = self._chunk_text(page_text, max_tokens=900)
                chunk_summaries = []
                
                for i, chunk in enumerate(chunks):
                    try:
                        summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                        chunk_summaries.append(summary[0]['summary_text'])
                    except Exception as e:
                        print(f"[PDF Summarizer] Error summarizing chunk {i+1} of page {page_num}: {str(e)}")
                        chunk_summaries.append(chunk[:200])
                
                # Combine chunk summaries
                combined = " ".join(chunk_summaries)
                if len(self.tokenizer.encode(combined, truncation=False)) > self.max_chunk_length:
                    # Summarize the combined summary
                    final = self.summarizer(combined, max_length=max_length + 30, min_length=min_length + 10, do_sample=False)
                    summary_text = final[0]['summary_text']
                else:
                    summary_text = combined
            else:
                summary = self.summarizer(page_text, max_length=max_length, min_length=min_length, do_sample=False)
                summary_text = summary[0]['summary_text']
            
            # Adjust summary length to target ~500 characters
            if target_chars > 0:
                current_length = len(summary_text)
                attempts = 0
                max_attempts = 3
                
                while attempts < max_attempts:
                    if current_length < target_chars * 0.8:  # If too short (less than 80% of target), expand
                        # Try to expand the summary
                        try:
                            expanded_max = min(max_length + (target_chars - current_length) // 4, 250)
                            expanded = self.summarizer(
                                page_text, 
                                max_length=expanded_max, 
                                min_length=min_length + 20, 
                                do_sample=False
                            )
                            expanded_text = expanded[0]['summary_text']
                            if len(expanded_text) > current_length:
                                summary_text = expanded_text
                                current_length = len(summary_text)
                                print(f"[PDF Summarizer] Page {page_num} summary expanded to {current_length} chars (target: {target_chars})")
                        except Exception as e:
                            print(f"[PDF Summarizer] Error expanding summary: {str(e)}")
                        attempts += 1
                    elif current_length > target_chars * 1.3:  # If too long (more than 130% of target), trim
                        # Keep first ~500 chars but try to end at sentence boundary
                        sentences = summary_text.split('. ')
                        trimmed = []
                        char_count = 0
                        for sentence in sentences:
                            if char_count + len(sentence) + 2 <= target_chars:
                                trimmed.append(sentence)
                                char_count += len(sentence) + 2
                            else:
                                break
                        if trimmed:
                            summary_text = '. '.join(trimmed) + '.'
                            current_length = len(summary_text)
                            print(f"[PDF Summarizer] Page {page_num} summary trimmed to {current_length} chars (target: {target_chars})")
                        else:
                            # Fallback: truncate at word boundary
                            words = summary_text.split()
                            trimmed_words = []
                            char_count = 0
                            for word in words:
                                if char_count + len(word) + 1 <= target_chars:
                                    trimmed_words.append(word)
                                    char_count += len(word) + 1
                                else:
                                    break
                            if trimmed_words:
                                summary_text = ' '.join(trimmed_words) + '.'
                                current_length = len(summary_text)
                        attempts += 1
                    else:
                        # Summary is within acceptable range (80%-130% of target)
                        print(f"[PDF Summarizer] Page {page_num} summary length: {current_length} chars (target: {target_chars})")
                        break
            
            # Improve grammar and clarity if enabled
            if improve_grammar and summary_text:
                try:
                    import asyncio
                    # Try to get the grammar improvement function from main module
                    try:
                        import sys
                        if 'main' in sys.modules:
                            main_module = sys.modules['main']
                            if hasattr(main_module, 'improve_grammar_and_clarity'):
                                # Run async function
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # If loop is running, create a task
                                    import concurrent.futures
                                    with concurrent.futures.ThreadPoolExecutor() as executor:
                                        future = executor.submit(asyncio.run, main_module.improve_grammar_and_clarity(summary_text))
                                        summary_text = future.result(timeout=30)
                                else:
                                    summary_text = loop.run_until_complete(main_module.improve_grammar_and_clarity(summary_text))
                    except Exception as e:
                        print(f"[PDF Summarizer] Grammar improvement not available: {str(e)}")
                except Exception as e:
                    print(f"[PDF Summarizer] Error improving grammar: {str(e)}")
            
            return summary_text
        except Exception as e:
            print(f"[PDF Summarizer] Error summarizing page {page_num}: {str(e)}")
            return f"[Page {page_num}]: Error - {str(e)}"
    
    def summarize_all_pages(self, pages: List[str], summary_type: str = "detailed", improve_grammar: bool = True) -> Dict:
        """
        Summarize all pages comprehensively
        
        Args:
            pages: List of page texts
            summary_type: "concise", "detailed", or "comprehensive"
        
        Returns:
            Dictionary with page summaries and overall summary
        """
        self._initialize()
        
        print(f"[PDF Summarizer] Processing {len(pages)} pages with {summary_type} summary type...")
        
        # Determine summary parameters based on type
        # Each page should give approximately 500 characters
        if summary_type == "concise":
            page_max_length = 120  # Target ~500 chars (tokens to chars ratio ~4:1)
            page_min_length = 80
            overall_max_length = 200
            overall_min_length = 80
        elif summary_type == "detailed":
            page_max_length = 150  # Target ~500 chars
            page_min_length = 100
            overall_max_length = 300
            overall_min_length = 120
        else:  # comprehensive
            page_max_length = 180  # Target ~500 chars
            page_min_length = 120
            overall_max_length = 400
            overall_min_length = 150
        
        # Step 1: Summarize each page individually
        page_summaries = []
        for i, page_text in enumerate(pages, 1):
            if page_text and len(page_text.strip()) > 50:
                print(f"[PDF Summarizer] Summarizing page {i}/{len(pages)}...")
                page_summary = self.summarize_page(page_text, i, page_max_length, page_min_length, improve_grammar=improve_grammar, target_chars=500)
                page_summaries.append({
                    "page_number": i,
                    "summary": page_summary,
                    "original_length": len(page_text),
                    "summary_length": len(page_summary)
                })
            else:
                print(f"[PDF Summarizer] Page {i} has insufficient content, skipping...")
                page_summaries.append({
                    "page_number": i,
                    "summary": f"[Page {i}]: No content available",
                    "original_length": len(page_text) if page_text else 0,
                    "summary_length": 0
                })
        
        # Step 2: Create comprehensive overall summary from all page summaries
        print(f"[PDF Summarizer] Creating overall summary from {len(page_summaries)} page summaries...")
        
        # Combine all page summaries
        combined_summaries = "\n\n".join([
            f"Page {ps['page_number']}: {ps['summary']}" 
            for ps in page_summaries 
            if ps['summary_length'] > 0
        ])
        
        if not combined_summaries or len(combined_summaries.strip()) < 100:
            return {
                "page_summaries": page_summaries,
                "overall_summary": "Unable to generate overall summary - insufficient content",
                "total_pages": len(pages),
                "pages_summarized": len([ps for ps in page_summaries if ps['summary_length'] > 0])
            }
        
        # Create overall summary
        try:
            # Check if combined summaries are too long
            encoded = self.tokenizer.encode(combined_summaries, truncation=False)
            
            if len(encoded) > self.max_chunk_length:
                # Use recursive summarization
                chunks = self._chunk_text(combined_summaries, max_tokens=900)
                chunk_summaries = []
                
                for i, chunk in enumerate(chunks):
                    try:
                        summary = self.summarizer(
                            chunk, 
                            max_length=overall_max_length // len(chunks) + 50, 
                            min_length=overall_min_length // len(chunks) + 20, 
                            do_sample=False
                        )
                        chunk_summaries.append(summary[0]['summary_text'])
                    except Exception as e:
                        print(f"[PDF Summarizer] Error in chunk {i+1}: {str(e)}")
                        chunk_summaries.append(chunk[:300])
                
                # Final summary of chunk summaries
                final_input = " ".join(chunk_summaries)
                if len(self.tokenizer.encode(final_input, truncation=False)) > self.max_chunk_length:
                    # One more round
                    final = self.summarizer(
                        final_input, 
                        max_length=overall_max_length, 
                        min_length=overall_min_length, 
                        do_sample=False
                    )
                    overall_summary = final[0]['summary_text']
                else:
                    final = self.summarizer(
                        final_input, 
                        max_length=overall_max_length, 
                        min_length=overall_min_length, 
                        do_sample=False
                    )
                    overall_summary = final[0]['summary_text']
            else:
                # Single pass summary
                overall = self.summarizer(
                    combined_summaries, 
                    max_length=overall_max_length, 
                    min_length=overall_min_length, 
                    do_sample=False
                )
                overall_summary = overall[0]['summary_text']
            
            print(f"[PDF Summarizer] Overall summary created: {len(overall_summary)} characters")
            
            # Improve grammar of overall summary
            if improve_grammar and overall_summary:
                try:
                    import sys
                    if 'main' in sys.modules:
                        main_module = sys.modules['main']
                        if hasattr(main_module, 'improve_grammar_and_clarity'):
                            import asyncio
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                import concurrent.futures
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(asyncio.run, main_module.improve_grammar_and_clarity(overall_summary))
                                    overall_summary = future.result(timeout=30)
                            else:
                                overall_summary = loop.run_until_complete(main_module.improve_grammar_and_clarity(overall_summary))
                            print(f"[PDF Summarizer] Overall summary grammar improved")
                except Exception as e:
                    print(f"[PDF Summarizer] Error improving overall summary grammar: {str(e)}")
            
        except Exception as e:
            print(f"[PDF Summarizer] Error creating overall summary: {str(e)}")
            overall_summary = combined_summaries[:500] + "..."
        
        return {
            "page_summaries": page_summaries,
            "overall_summary": overall_summary,
            "total_pages": len(pages),
            "pages_summarized": len([ps for ps in page_summaries if ps['summary_length'] > 0]),
            "summary_type": summary_type
        }

