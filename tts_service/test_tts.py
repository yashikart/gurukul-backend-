"""
Simple test script to verify TTS functionality
"""
import pyttsx3
import os

def test_tts_basic():
    """Test basic TTS functionality"""
    print("Testing TTS Engine...")
    
    try:
        # Initialize engine
        engine = pyttsx3.init()
        print("✓ TTS engine initialized successfully")
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"✓ Found {len(voices)} voices available")
        
        # Print voice details
        for i, voice in enumerate(voices[:3]):  # Show first 3 voices
            print(f"  Voice {i+1}: {voice.name}")
        
        # Test speech rate
        rate = engine.getProperty('rate')
        print(f"✓ Current speech rate: {rate} words/min")
        
        # Test volume
        volume = engine.getProperty('volume')
        print(f"✓ Current volume: {volume}")
        
        # Generate test audio
        test_text = "Hello! This is a test of the Gurukul text to speech service."
        output_file = "tts_outputs/test_audio.wav"
        
        # Create output directory if it doesn't exist
        os.makedirs("tts_outputs", exist_ok=True)
        
        print(f"\nGenerating audio file: {output_file}")
        engine.save_to_file(test_text, output_file)
        engine.runAndWait()
        
        # Check if file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ Audio file generated successfully!")
            print(f"  File: {output_file}")
            print(f"  Size: {file_size} bytes")
            return True
        else:
            print("✗ Audio file was not created")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TTS Service Test")
    print("=" * 60)
    success = test_tts_basic()
    print("=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Tests failed")
    print("=" * 60)
