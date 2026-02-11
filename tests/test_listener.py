import sys
import os

# Project root added via pytest.ini

from core.listener import Listener

def test_listener():
    print("Initializing Listener...")
    listener = Listener(model_size="tiny") # Use tiny for fast testing
    
    print("\n--- Testing Recording & Transcription ---")
    print("Please speak a short sentence (5 seconds)...")
    text = listener.listen(duration=5)
    
    print(f"\nCaptured Text: {text}")
    
    if text:
        print("✅ Test Passed: meaningful text captured.")
    else:
        print("⚠️ Test Warning: No text captured (maybe silence?).")

if __name__ == "__main__":
    test_listener()
