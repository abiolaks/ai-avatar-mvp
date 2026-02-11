import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.speaker import Speaker

def test_speaker():
    print("Initializing Speaker...")
    speaker = Speaker()
    
    print("Testing immediate speech...")
    speaker.speak("System check initiated. Audio output functional.")
    
    print("Testing save to file...")
    path = speaker.speak_to_file("Audio file generation successful.")
    
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"✅ Audio file created at: {path} ({os.path.getsize(path)} bytes)")
    else:
        print("❌ Failed to create audio file.")

    # Cleanup
    if os.path.exists(path):
        os.remove(path)

if __name__ == "__main__":
    test_speaker()
