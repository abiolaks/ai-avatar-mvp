#!/usr/bin/env python3
"""Test SadTalker video generation"""
import os
import sys
from core.avatar import Avatar
from core.speaker import Speaker

def main():
    print("Testing SadTalker Video Generation...")
    print("=" * 50)
    
    # Initialize components
    speaker = Speaker()
    avatar = Avatar()
    
    # Generate test audio
    test_text = "Hello! This is a test of the SadTalker lip-sync avatar system."
    print(f"\n1. Generating audio for: '{test_text}'")
    audio_path = speaker.speak_to_file(test_text, output_path="test_audio.wav")
    print(f"✓ Audio saved to: {audio_path}")
    
    # Check if avatar image exists
    image_path = "resources/IMG_20240708_092636.jpg"
    if not os.path.exists(image_path):
        print(f"\n✗ Avatar image not found at: {image_path}")
        print("Please add an image to resources/IMG_20240708_092636.jpg")
        return 1
    
    print(f"✓ Avatar image found: {image_path}")
    
    # Generate video
    print("\n2. Generating lip-sync video with SadTalker...")
    print("   This may take a few minutes on first run...")
    video_path = avatar.generate_video(audio_path, image_path)
    print(f"✓ Video generated: {video_path}")
    
    # Check output
    if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
        print(f"\n✓ SUCCESS! Video file created ({os.path.getsize(video_path)} bytes)")
        print(f"   Location: {os.path.abspath(video_path)}")
    else:
        print("\n✗ Video file not created or is empty")
        return 1
    
    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
