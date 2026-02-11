import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.thinker import Thinker

def test_thinker():
    print("Initializing Thinker...")
    try:
        thinker = Thinker()
    except Exception as e:
        print(f"Failed to init Thinker (is Ollama running?): {e}")
        return

    # Simulate conversation
    inputs = [
        "Hi, I want to learn coding.",
        "I am a beginner.",
        "I know a little bit of math but no coding.",
        "I want to be a Data Scientist."
    ]

    for inp in inputs:
        print(f"\nUser: {inp}")
        resp = thinker.process_input(inp)
        print(f"Avatar: {resp}")
        
    print("\n✅ Conversation simulation complete.")

if __name__ == "__main__":
    test_thinker()
