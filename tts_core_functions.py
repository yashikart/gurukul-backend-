import pyttsx3
import uuid
import os


def initialize_tts_engine():
    """Initialize and configure the TTS engine"""
    engine = pyttsx3.init()
    
    # Configure TTS settings for better quality
    voices = engine.getProperty('voices')
    if voices:
        # Try to use a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

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


def text_to_speech_stream(text):
    """
    Convert text to speech and return the audio data directly
    
    Args:
        text (str): The text to convert to speech
        
    Returns:
        bytes: Audio data
    """
    if not text:
        raise ValueError("Text is required")
    
    import tempfile
    
    # Initialize TTS engine
    engine = initialize_tts_engine()
    
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