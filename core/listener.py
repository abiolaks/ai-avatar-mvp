import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import os
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Listener:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        """
        Initialize the Listener with a Whisper model.
        """
        logger.info(f"Loading Whisper model: {model_size} on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info("Whisper model loaded.")

    def record_audio_with_vad(self, max_duration=5, sample_rate=16000, chunk_duration=0.5, silence_threshold=200, silence_chunks=6):
        """
        Record audio from the microphone with Voice Activity Detection.
        Stops recording when silence is detected for a specified duration.
        
        Args:
            max_duration: Maximum recording duration in seconds
            sample_rate: Audio sample rate
            chunk_duration: Duration of each audio chunk in seconds
            silence_threshold: RMS threshold below which audio is considered silence (lowered to 200 for better sensitivity)
            silence_chunks: Number of consecutive silent chunks before stopping (6 chunks = 3 seconds)
        """
        chunk_size = int(chunk_duration * sample_rate)
        max_chunks = int(max_duration / chunk_duration)
        
        logger.info(f"Recording with VAD (max {max_duration}s, will stop after 3s of silence)...")
        print("🎙️  Speak now (will stop 3 seconds after you finish)...")
        
        chunks = []
        silent_chunk_count = 0
        has_detected_speech = False
        
        for i in range(max_chunks):
            # Record one chunk
            chunk = sd.rec(chunk_size, samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait()
            
            # Calculate RMS (Root Mean Square) to detect voice activity
            rms = np.sqrt(np.mean(chunk**2))
            
            chunks.append(chunk)
            
            # Check if chunk is silent
            if rms < silence_threshold:
                silent_chunk_count += 1
                # Only show silence indicator if we've already detected speech
                if has_detected_speech:
                    print(".", end="", flush=True)
                
                # Stop if we've had enough consecutive silent chunks AND we've detected speech
                if silent_chunk_count >= silence_chunks and has_detected_speech:
                    print()  # New line
                    logger.info(f"Silence detected after {(i+1)*chunk_duration:.1f}s. Stopping recording.")
                    break
            else:
                if not has_detected_speech:
                    print("🔴 Recording...", flush=True)
                    has_detected_speech = True
                silent_chunk_count = 0  # Reset counter on voice activity
                print("▮", end="", flush=True)  # Visual indicator of speech
        
        print()  # New line after recording
        if silent_chunk_count < silence_chunks:
            logger.info(f"Recording complete (reached max duration: {max_duration}s).")
        
        # Concatenate all chunks
        audio_data = np.concatenate(chunks, axis=0)
        return audio_data, sample_rate

    def record_audio(self, duration=5, sample_rate=16000):
        """
        Record audio from the microphone for a fixed duration.
        """
        logger.info(f"Recording for {duration} seconds...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        logger.info("Recording complete.")
        return audio_data, sample_rate

    def transcribe(self, audio_data, sample_rate):
        """
        Transcribe audio data using Faster-Whisper.
        """
        # Save to temporary file for Whisper (it expects a file path or array, but let's be safe with temp file for now)
        # Actually faster-whisper accepts numpy array if flattened and normalized correctly, 
        # but let's stick to file for robustness first.
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            wav.write(tmp_file.name, sample_rate, audio_data)
            tmp_path = tmp_file.name

        try:
            # Force English (en) to stop random Chinese/Russian noise
            segments, info = self.model.transcribe(tmp_path, beam_size=5, language="en")
            
            valid_segments = []
            for segment in segments:
                # Filter out hallucinations (common in silence)
                if segment.no_speech_prob > 0.6: # Stricter threshold (was implicit/default)
                    logger.info(f"Skipped (no_speech_prob={segment.no_speech_prob:.2f}): {segment.text}")
                    continue
                
                if segment.avg_logprob < -1.5: # Further relaxed (was -1.0, then -0.8)
                    logger.info(f"Skipped (low confidence={segment.avg_logprob:.2f}): {segment.text}")
                    continue
                    
                valid_segments.append(segment.text)

            text = " ".join(valid_segments)
            return text.strip()
        finally:
            os.remove(tmp_path)

    def listen(self, duration=5, use_vad=True):
        """
        High-level method to record and transcribe.
        
        Args:
            duration: Duration in seconds (max duration if use_vad=True)
            use_vad: Whether to use Voice Activity Detection
        """
        if use_vad:
            audio, rate = self.record_audio_with_vad(max_duration=duration)
        else:
            audio, rate = self.record_audio(duration)
        text = self.transcribe(audio, rate)
        logger.info(f"Transcribed: '{text}'")
        return text

if __name__ == "__main__":
    listener = Listener()
    print("Speak now...")
    text = listener.listen(duration=5, use_vad=True)
    print(f"Result: {text}")

