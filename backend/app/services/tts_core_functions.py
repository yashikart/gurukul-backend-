import pyttsx3
import uuid
import os
import re


def initialize_tts_engine(language='en'):
    """
    Initialize and configure the TTS engine with language support
    Args:
        language (str): Language code (e.g., 'en' for English, 'es' for Spanish, 'fr' for French)
    """
    engine = pyttsx3.init()
    
    # Language to voice mapping (based on common SAPI5 voice names and language codes)
    # Windows SAPI5 voices often have language codes in their IDs (e.g., EN-US, ES-ES, FR-FR)
    language_mapping = {
        'en': ['english', 'zira', 'david', 'mark', 'en-us', 'en_us', 'en_gb'],
        'es': ['spanish', 'helena', 'sabina', 'es-es', 'es_es', 'es-mx', 'es_mx'],
        'fr': ['french', 'hortense', 'denis', 'fr-fr', 'fr_fr', 'fr-ca', 'fr_ca'],
        'de': ['german', 'hedda', 'stefan', 'de-de', 'de_de'],
        'it': ['italian', 'elsa', 'cosimo', 'it-it', 'it_it'],
        'pt': ['portuguese', 'heloisa', 'daniel', 'pt-pt', 'pt_pt', 'pt-br', 'pt_br'],
        'ru': ['russian', 'irina', 'pavel', 'ru-ru', 'ru_ru'],
        'zh': ['chinese', 'huihui', 'kangkang', 'zh-cn', 'zh_cn', 'zh-tw', 'zh_tw'],
        'ja': ['japanese', 'haruka', 'ichiro', 'ja-jp', 'ja_jp'],
        'ko': ['korean', 'heami', 'ko-kr', 'ko_kr'],
        'hi': ['hindi', 'kalpana', 'hemant', 'hi-in', 'hi_in'],
        'ar': ['arabic', 'hoda', 'naayf', 'ar-sa', 'ar_sa', 'ar-eg', 'ar_eg'],
    }
    
    # Configure TTS settings for better quality
    voices = engine.getProperty('voices')
    if voices:
        target_keywords = language_mapping.get(language.lower(), ['english', 'zira', 'en-us'])
        voice_found = False
        selected_voice = None
        
        # Debug: Print available voices (first time only, can be commented out later)
        if not hasattr(initialize_tts_engine, '_voices_logged'):
            print(f"[TTS] Available voices on system:")
            for i, v in enumerate(voices):
                print(f"  {i+1}. Name: {v.name}, ID: {v.id}")
            initialize_tts_engine._voices_logged = True
        
        # Try to find a voice matching the language
        for voice in voices:
            voice_name_lower = voice.name.lower()
            voice_id_lower = voice.id.lower()
            
            # Check both voice name and ID for language keywords
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in voice_name_lower or keyword_lower in voice_id_lower:
                    engine.setProperty('voice', voice.id)
                    selected_voice = voice.name
                    voice_found = True
                    print(f"[TTS] Selected voice for language '{language}': {voice.name}")
                    break
            
            if voice_found:
                break
        
        # Fallback: use first available voice if language not found
        if not voice_found and voices:
            engine.setProperty('voice', voices[0].id)
            print(f"[TTS] Language '{language}' not found, using default voice: {voices[0].name}")

    # Set speech rate (words per minute)
    engine.setProperty('rate', 180)  # Slightly slower for clarity

    # Set volume (0.0 to 1.0)
    engine.setProperty('volume', 0.9)
    
    return engine


def text_to_speech_simple(text, output_filename=None):
    """
    Convert text to speech and save as an audio file
    
    Args:
        text (str): The text to convert to speech
        output_filename (str, optional): Filename for output. If None, generates a unique filename.
        
    Returns:
        str: Path to the generated audio file
    """
    if not text:
        raise ValueError("Text is required")
    
    if not output_filename:
        output_filename = f"tts_{uuid.uuid4()}.wav"
    
    if not output_filename.endswith('.wav'):
        output_filename += '.wav'
    
    # Initialize TTS engine
    engine = initialize_tts_engine()
    
    # Generate audio file
    engine.save_to_file(text, output_filename)
    engine.runAndWait()
    
    # Verify file was created
    if not os.path.exists(output_filename):
        raise Exception("Audio generation failed - file not created")
    
    # Check file size
    file_size = os.path.getsize(output_filename)
    if file_size == 0:
        os.remove(output_filename)  # Remove empty file
        raise Exception("Audio generation failed - empty file")
    
    return output_filename


def remove_emojis(text):
    """
    Remove emojis and emoji-like symbols from text
    
    Args:
        text (str): Text that may contain emojis
        
    Returns:
        str: Text with emojis removed
    """
    # Remove emojis using regex pattern
    # This pattern matches most emoji ranges in Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+", 
        flags=re.UNICODE
    )
    
    # Remove emojis and clean up extra spaces
    text_without_emojis = emoji_pattern.sub('', text)
    # Clean up multiple spaces
    text_without_emojis = re.sub(r'\s+', ' ', text_without_emojis).strip()
    
    return text_without_emojis


def translate_text(text, target_language='en'):
    """
    Translate text to target language using Groq API
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (e.g., 'en', 'es', 'fr', 'ja')
        
    Returns:
        str: Translated text
    """
    # Remove emojis before translation
    text = remove_emojis(text)
    
    # Language name mapping for better translation prompts
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh': 'Chinese (Simplified)',
        'ja': 'Japanese',
        'ko': 'Korean',
        'hi': 'Hindi',
        'ar': 'Arabic',
    }
    
    target_lang_name = language_names.get(target_language.lower(), 'English')
    
    # If target is English, no translation needed
    if target_language.lower() == 'en':
        return text
    
    try:
        import os
        import requests
        from app.core.config import settings
        
        # Get Groq API key
        api_key = settings.GROQ_API_KEY or os.getenv('GROQ_API_KEY')
        if not api_key:
            print(f"[TTS] No GROQ_API_KEY found, skipping translation")
            return text
        
        # Strict translation prompt - only translate, no additions
        # Calculate max_tokens based on input length (translation shouldn't be much longer)
        word_count = len(text.split())
        # Limit max_tokens to prevent model from generating extra content
        max_tokens = min(max(word_count * 2, 100), 300)  # More conservative: 100-300 tokens
        
        # Very strict system prompt to prevent hallucinations
        system_prompt = f"""You are a translation tool. Your ONLY job is to translate the given text to {target_lang_name}.

RULES:
- Translate ONLY the provided text
- Do NOT add any explanations, notes, or additional information
- Do NOT add context or examples
- Do NOT mention other languages or topics
- Return ONLY the translation, nothing else
- If the text is already in {target_lang_name}, return it unchanged"""

        # Simple user prompt with clear delimiter
        translation_prompt = f"Translate this text to {target_lang_name}:\n\n{text}"
        
        # Call Groq API using requests (same way as other services)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to use a faster model for translation (smaller = faster)
        default_model = settings.GROQ_MODEL_NAME or "llama-3.3-70b-versatile"
        # Use fastest available model - try smaller models first for speed
        fast_model = "llama-3.1-8b-instant"  # Fastest Groq model
        
        # Try with fast model first (without stop sequences - they might cause 400 errors)
        payload = {
            "model": fast_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": translation_prompt}
            ],
            "temperature": 0.0,  # Zero temperature for fastest, most deterministic output
            "max_tokens": max_tokens
            # Note: Not using stop sequences as they might cause 400 errors with some models
        }
        
        try:
            response = requests.post(
                settings.GROQ_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=10  # Even shorter timeout
            )
            # If fast model fails, try with default model
            if response.status_code != 200:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('error', {}).get('message', '')
                except:
                    error_detail = response.text[:200]
                raise Exception(f"Fast model returned {response.status_code}: {error_detail}")
        except Exception as e:
            # Fallback to default model if fast model fails
            print(f"[TTS] Fast model failed, using default: {e}")
            # Create fresh payload for default model (without stop sequences)
            payload_fallback = {
                "model": default_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": translation_prompt}
                ],
                "temperature": 0.0,
                "max_tokens": max_tokens
            }
            
            try:
                response = requests.post(
                    settings.GROQ_API_ENDPOINT,
                    headers=headers,
                    json=payload_fallback,
                    timeout=15
                )
            except Exception as fallback_error:
                print(f"[TTS] Default model also failed: {fallback_error}")
                raise fallback_error
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result['choices'][0]['message']['content'].strip()
            
            # Clean up the translation - remove any extra content
            # Remove quotation marks
            translated_text = translated_text.strip('"').strip("'").strip()
            
            # Remove common prefixes that models add
            prefixes_to_remove = [
                f"{target_lang_name}:",
                f"Translation:",
                f"Translated text:",
                f"Here is the translation:",
                f"The translation is:",
            ]
            for prefix in prefixes_to_remove:
                if translated_text.lower().startswith(prefix.lower()):
                    translated_text = translated_text[len(prefix):].strip()
            
            # Remove any notes or explanations that might have been added
            # Split by common separators and take only the first part
            separators = ["\n\nNote:", "\n\nAlso:", "\n\nAdditionally:", "\n\n---", "\n\nNote that"]
            for sep in separators:
                if sep in translated_text:
                    translated_text = translated_text.split(sep)[0].strip()
            
            # Limit length - if translation is way longer than original, truncate
            original_length = len(text)
            if len(translated_text) > original_length * 3:  # If 3x longer, something's wrong
                # Take first part that's roughly similar length
                words = translated_text.split()
                original_words = text.split()
                max_words = len(original_words) * 2  # Allow 2x word count max
                translated_text = " ".join(words[:max_words])
                print(f"[TTS] Warning: Translation was too long, truncated to {max_words} words")
            
            print(f"[TTS] Translated text to {target_lang_name} (length: {len(translated_text)} vs original: {len(text)})")
            return translated_text
        else:
            print(f"[TTS] Translation API error: {response.status_code}, using original text")
            return text
        
    except Exception as e:
        print(f"[TTS] Translation failed: {e}, using original text")
        return text


def text_to_speech_stream(text, language='en', use_google_tts=True, translate=True):
    """
    Convert text to speech and return the audio data directly
    
    Args:
        text (str): The text to convert to speech
        language (str): Language code (e.g., 'en', 'es', 'fr'). Defaults to 'en'
        use_google_tts (bool): If True, use Google TTS (supports all languages). 
                             If False, use pyttsx3 (system voices only)
        translate (bool): If True, translate text to target language before speaking
        
    Returns:
        bytes: Audio data
    """
    if not text:
        raise ValueError("Text is required")
    
    import tempfile
    
    # Remove emojis from text before processing
    text = remove_emojis(text)
    
    # Translate text if needed and not English
    if translate and language.lower() != 'en':
        text = translate_text(text, language)
    
    # Use Google TTS for better language support (default)
    if use_google_tts:
        try:
            from gtts import gTTS
            import io
            
            # Language code mapping for Google TTS
            # Google TTS uses full language codes (e.g., 'en', 'es', 'fr', 'de')
            # Most of our codes are already compatible, but we can map if needed
            lang_code = language.lower()
            
            # Create Google TTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            
            if not audio_data:
                raise Exception("Google TTS failed - no audio data")
            
            print(f"[TTS] Used Google TTS for language '{language}'")
            return audio_data
            
        except Exception as e:
            print(f"[TTS] Google TTS failed: {e}, falling back to pyttsx3")
            # Fall back to pyttsx3 if Google TTS fails
            use_google_tts = False
    
    # Fallback to pyttsx3 (system voices)
    if not use_google_tts:
        # Initialize TTS engine with language
        engine = initialize_tts_engine(language)
        
        # Create temporary file for audio generation
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filepath = temp_file.name

        try:
            # Generate audio to temporary file
            engine.save_to_file(text, temp_filepath)
            engine.runAndWait()

            # Read the generated audio file into memory
            with open(temp_filepath, 'rb') as audio_file:
                audio_data = audio_file.read()

            # Clean up temporary file
            os.unlink(temp_filepath)

            if not audio_data:
                raise Exception("Audio generation failed - no data")

            return audio_data

        except Exception as e:
            # Ensure temp file is cleaned up even on error
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
            raise e


def speak_text_directly(text):
    """
    Speak text directly without saving to file
    
    Args:
        text (str): The text to speak
    """
    if not text:
        raise ValueError("Text is required")
    
    # Initialize TTS engine
    engine = initialize_tts_engine()
    
    # Speak the text directly
    engine.say(text)
    engine.runAndWait()


# Example usage
if __name__ == "__main__":
    sample_text = "Hello, this is a text to speech example."
    
    # Method 1: Save to file
    filename = text_to_speech_simple(sample_text, "example_output.wav")
    print(f"Audio saved to: {filename}")
    
    # Method 2: Speak directly
    speak_text_directly("This will be spoken directly.")