import os
import sys
import logging
import time
from core.listener import Listener
from core.thinker import Thinker
from core.speaker import Speaker
from core.avatar import Avatar

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

def main():
    logger.info("Initializing AI Avatar MVP...")
    
    # Initialize Modules
    try:
        listener = Listener(model_size="tiny") # Use 'base' or 'small' for better accuracy
        thinker = Thinker() # Use internal default model (qwen3:0.6b)
        speaker = Speaker()
        avatar = Avatar()  # Uses SadTalker (config in sadtalker_config.yaml)
        
        # Avatar image is configured in sadtalker_config.yaml
        # Default: resources/IMG_20240708_092636.jpg

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return

    logger.info("System Ready. Say 'Exit' to quit.")
    
    # Initial Greeting
    greeting = "Hello! I am Genevieve, your  Career Counselor. What would you like to learn today?"
    print(f"🤖 Avatar: {greeting}")
    speaker.speak(greeting)

    while True:
        try:
            # 1. Listen (VAD disabled due to transcription quality issues)
            print("\n🎤 Listening... (Speak now)")
            user_text = listener.listen(duration=5, use_vad=False)
            if not user_text:
                logger.info("No speech detected.")
                continue
            
            print(f"👤 User: {user_text}")
            
            if "exit" in user_text.lower() or "quit" in user_text.lower():
                print("👋 Exiting...")
                break

            # 2. Think
            print("🧠 Thinking...")
            response_text = thinker.process_input(user_text)
            # --- JSON FILTER FOR TTS ---
            # Even with Thinker logic, sometimes JSON slips through (e.g. if tool call failed).
            # We do NOT want to speak raw JSON.
            text_to_speak = response_text
            clean_text = response_text
            url_to_display = None
            
            if "{" in response_text and "}" in response_text and "action" in response_text:
                try:
                    import json
                    # Try to parse
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    json_str = response_text[start:end]
                    data = json.loads(json_str)
                    
                    # If it's a recommendation that slipped through
                    if data.get("action") == "recommend":
                        params = data.get("params", {})
                        text_to_speak = f"I recommend learning {params.get('skills', 'new skills')} to become a {params.get('career_path', 'professional')}."
                        clean_text = text_to_speak
                    else:
                        text_to_speak = "I am processing that information."
                        
                except:
                    pass # Speak original if parse fails

            # Extract URL if present (Check last line specifically)
            # The Thinker is instructed to put the URL at the VERY END on a new line.
            lines = response_text.strip().split('\n')
            last_line = lines[-1].strip()
            
            import re
            url_pattern = r'(https?://[^\s)]+)'
            urls = re.findall(url_pattern, last_line)
            
            if urls:
                url_to_display = urls[0]
                # Remove the URL line from spoken text entirely
                text_to_speak = "\n".join(lines[:-1]).strip()
                # Optional: Add a verbal cue like "Check the link below" if desired, 
                # but the prompt already handles the explanation.
                clean_text = text_to_speak 
            else:
                # Fallback: Check globally if instruction failed
                 urls = re.findall(url_pattern, response_text)
                 if urls:
                     url_to_display = urls[0]
                     text_to_speak = response_text.replace(url_to_display, "")
                     clean_text = text_to_speak

            # Fallback if text_to_speak became empty (e.g. model only output a URL)
            if not text_to_speak.strip():
                text_to_speak = "I've found a great course for you! Check the link below."
                clean_text = text_to_speak

            print(f"🤖 Avatar: {clean_text}") 
            if url_to_display:
                print(f"\n🔗 COURSE LINK: \033[94m{url_to_display}\033[0m\n")

            # FILTER EMOJIS (Prevent TTS reading them)
            # Comprehensive emoji pattern covering all Unicode emoji ranges
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U00002702-\U000027B0"  # dingbats
                "\U000024C2-\U0001F251"  # enclosed characters
                "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
                "\U0001FA00-\U0001FA6F"  # chess symbols
                "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
                "\U00002600-\U000026FF"  # miscellaneous symbols
                "\U00002700-\U000027BF"  # dingbats
                "]+", 
                flags=re.UNICODE
            )
            text_to_speak = emoji_pattern.sub(r'', text_to_speak)

            # 3. Speak & Animate
            print("🗣️ Speaking...")
            # Generate audio file
            audio_path = speaker.speak_to_file(text_to_speak)
            
            # Generate video (in parallel ideally, but sequential for MVP)
            # print("🎥 Generating Video...")
            # video_path = avatar.generate_video(audio_path, avatar_image)
            
            # Play Audio (since video generation is slow/mocked)
            # If video was real and fast, we'd play video. For now, play audio.
            speaker.speak(text_to_speak) 
            
            # Cleanup temp audio
            if os.path.exists(audio_path):
                os.remove(audio_path)

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            logger.error(f"Runtime Error: {e}")

if __name__ == "__main__":
    main()
