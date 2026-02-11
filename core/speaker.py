import subprocess
import logging
import os
import tempfile
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Speaker:
    def __init__(self, voice="Samantha", rate=175):
        """
        Initialize TTS engine (MacOS 'say' command wrapper).
        """
        self.voice = voice # 'Samantha' is a good default for Mac
        self.rate = str(rate)

    def speak(self, text):
        """
        Speak the text immediately/blocking.
        """
        logger.info(f"Speaking: '{text}'")
        try:
            # -v Voice, -r Rate
            subprocess.run(["say", "-v", self.voice, "-r", self.rate, text])
        except Exception as e:
            logger.error(f"TTS Error: {e}")

    def speak_to_file(self, text, output_path=None):
        """
        Save speech to a file (needed for MuseTalk).
        """
        if not output_path:
            # Create a temp file path (MacOS 'say' supports .aiff or .wav/mp4 with --data-format)
            # Default 'say -o file.wav' creates a WAVE file.
            tf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_path = tf.name
            tf.close()
            
        logger.info(f"Saving speech to {output_path}...")
        try:
            # -o OutputFile, --data-format=LEF32@44100 (optional, default is usually fine)
            subprocess.run(["say", "-v", self.voice, "-r", self.rate, "-o", output_path, "--data-format=LEI16@44100", text])
            
            # Wait for file to exist/flush (subprocess.run should wait, but just safe check)
            if not os.path.exists(output_path):
                 logger.error("TTS File generation failed.")
            
        except Exception as e:
            logger.error(f"TTS File Error: {e}")
            
        return output_path

if __name__ == "__main__":
    speaker = Speaker()
    speaker.speak("Hello, I am your AI Avatar running on Mac.")
    path = speaker.speak_to_file("This is a saved audio file.")
    print(f"Saved to {path}")
    # clean up
    # if os.path.exists(path):
    #    os.remove(path)
