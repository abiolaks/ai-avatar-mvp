import subprocess
import logging
import os
import sys
import tempfile
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Speaker:
    def __init__(self, voice="Samantha", rate=175):
        """
        Initialize cross-platform TTS engine.
        Uses macOS 'say' on Mac, gTTS on Linux/other platforms.
        """
        self.voice = voice  # Used for macOS
        self.rate = str(rate)  # Used for macOS
        self.platform = self._detect_platform()
        
    def _detect_platform(self):
        """Detect the operating system."""
        if sys.platform == "darwin":
            return "macos"
        return "linux"
    
    def speak(self, text):
        """
        Speak the text immediately/blocking.
        """
        logger.info(f"Speaking: '{text}'")
        
        if self.platform == "macos":
            self._speak_macos(text)
        else:
            # On Linux, we can't play audio directly via gTTS easily
            # So we'll save to temp file and could use a player like ffplay
            # For now, just log (since Docker typically runs headless)
            logger.info("[Linux] TTS would play here (headless mode)")
    
    def _speak_macos(self, text):
        """Use macOS 'say' command."""
        try:
            subprocess.run(["say", "-v", self.voice, "-r", self.rate, text])
        except Exception as e:
            logger.error(f"macOS TTS Error: {e}")

    def speak_to_file(self, text, output_path=None):
        """
        Save speech to a file (needed for SadTalker).
        Works on both macOS and Linux.
        """
        if not output_path:
            tf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_path = tf.name
            tf.close()
            
        logger.info(f"Saving speech to {output_path}...")
        
        if self.platform == "macos":
            self._speak_to_file_macos(text, output_path)
        else:
            self._speak_to_file_gtts(text, output_path)
            
        # Verify file exists
        if not os.path.exists(output_path):
            logger.error("TTS File generation failed.")
        
        return output_path
    
    def _speak_to_file_macos(self, text, output_path):
        """Use macOS 'say' command to save to file."""
        try:
            subprocess.run([
                "say", 
                "-v", self.voice, 
                "-r", self.rate, 
                "-o", output_path, 
                "--data-format=LEI16@44100", 
                text
            ])
        except Exception as e:
            logger.error(f"macOS TTS File Error: {e}")
    
    def _speak_to_file_gtts(self, text, output_path):
        """Use gTTS (Google Text-to-Speech) to save to file."""
        try:
            from gtts import gTTS
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            
            # gTTS saves as MP3 by default, but we need WAV for compatibility
            # Save as MP3 first, then convert to WAV using ffmpeg
            temp_mp3 = output_path.replace('.wav', '.mp3')
            tts.save(temp_mp3)
            
            # Convert MP3 to WAV using ffmpeg (already in Dockerfile)
            subprocess.run([
                "ffmpeg", "-y", "-i", temp_mp3,
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "1",
                output_path
            ], check=True, capture_output=True)
            
            # Clean up temp MP3
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
                
        except ImportError:
            logger.error("gTTS not installed. Install with: pip install gtts")
            raise
        except Exception as e:
            logger.error(f"gTTS Error: {e}")
            raise

if __name__ == "__main__":
    speaker = Speaker()
    
    # Test platform detection
    print(f"Platform: {speaker.platform}")
    
    # Test speak
    speaker.speak("Hello, I am your AI Avatar.")
    
    # Test speak_to_file
    path = speaker.speak_to_file("This is a saved audio file.")
    print(f"Saved to {path}")

