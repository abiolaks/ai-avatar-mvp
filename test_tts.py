from core.speaker import Speaker
import os
import time

def test_tts():
    print("Initializing Speaker (MacOS 'say')...")
    speaker = Speaker()
    
    print("Testing direct speech...")
    speaker.speak("Testing, one, two, three. Can you hear me?")
    
    print("Testing save to file...")
    path = speaker.speak_to_file("This is a test of saving audio to a file.")
    print(f"File saved to: {path}")
    
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print("SUCCESS: Audio file created and has content.")
        # Play it back using afplay to confirm structure
        # os.system(f"afplay {path}") 
    else:
        print("FAIL: Audio file missing or empty.")

if __name__ == "__main__":
    test_tts()
