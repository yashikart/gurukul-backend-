from abc import ABC, abstractmethod

class VoiceEngineInterface(ABC):
    """
    Standard interface for all text-to-speech requests in Gurukul.
    Ensures structural discipline and deterministic behavior.
    """
    
    @abstractmethod
    async def generate_audio(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech data (bytes).
        
        Args:
            text (str): The text to synthesize (max 5000 chars).
            language (str): ISO 639-1 language code.
            
        Returns:
            bytes: The synthesized audio data.
        """
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """
        Return the inner status of the voice engine.
        """
        pass
