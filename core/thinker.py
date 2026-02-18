import ollama
import json
import logging
from core.lms_interface import LMSInterface
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Thinker:
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
        # Using smallest model for fastest inference
        self.model = "qwen3:1.7b"
        self.lms = LMSInterface()
        self.history = []

        # Explicit State Tracking (to prevent hallucination)
        self.collected_info = {
            "goal": None,
            "level": None,
            "skills": None,
            "career_path": None,
        }

        self.system_prompt = """
You are a friendly and enthusiastic AI Career Counselor.
Your goal is to help the user find the perfect course.
You need to collect 4 items: [Goal, Level, Skills, Career Path].

RULES:
1. Be conversational and professional!
2. Ask ONE question at a time to keep it simple.
3. ACKNOWLEDGE what the user just said before asking the next question.
4. CHECK the 'Current State of Information' below. Ask ONLY for what is MISSING.
5. Do NOT ask about topics outside the 4 items (e.g. do not ask about Front-end vs Back-end).
6. Do NOT output JSON until you have ALL 4 items.
6. Do NOT say "Ask the user..." or add "ASK:". Just output the question.
7. Do NOT output "Action:" or "Params:" for intermediate steps. Just talk.

EXAMPLE FLOW:
User: "I want to be a Web Developer."
AI: "That's an exciting career choice! To help you start, are you a beginner or do you have some experience?"
User: "I am a beginner."
AI: "Got it! Do you have any existing technical skills like HTML or Python?"
User: "I know a little HTML."
AI: (Now you have all 4 items)

FINAL OUTPUT FORMAT (only when ready):
{
  "action": "recommend",
  "params": {
    "goal": "...",
    "level": "...",
    "skills": "...",
    "career_path": "..."
  }
}
"""
        # Initialize history
        self.history.append({"role": "system", "content": self.system_prompt})

    def _update_collected_info(self, user_text):
        """
        Extract information from user text and update collected_info.
        Simple keyword-based extraction.
        """
        text_lower = user_text.lower()

        # Career path / Goal detection
        # If user switches career, we might need to reset fields, but for now just update
        if "web developer" in text_lower or "web development" in text_lower:
            self.collected_info["career_path"] = "Web Developer"
            self.collected_info["goal"] = "Learn Web Development"
        elif (
            "data scientist" in text_lower
            or "data science" in text_lower
            or "detached scientist" in text_lower
            or "data size" in text_lower
        ):  # Handle mishearing
            self.collected_info["career_path"] = "Data Scientist"
            self.collected_info["goal"] = "Learn Data Science"
        elif "ai engineer" in text_lower:
            self.collected_info["career_path"] = "AI Engineer"
            self.collected_info["goal"] = "Learn AI"

        # Level detection
        if any(
            w in text_lower
            for w in [
                "beginner",
                "new",
                "scratch",
                "starting",
                "begin",
                "novice",
                "no experience",
            ]
        ):
            self.collected_info["level"] = "Beginner"
        elif "intermediate" in text_lower:
            self.collected_info["level"] = "Intermediate"
        elif "advanced" in text_lower:
            self.collected_info["level"] = "Advanced"

        # Skills detection (look for common tech terms)
        skills = []
        common_skills = [
            "python",
            "html",
            "css",
            "javascript",
            "react",
            "java",
            "tensorflow",
            "sql",
            "git",
        ]
        for skill in common_skills:
            # Simple negation check
            if f"no {skill}" in text_lower or f"not {skill}" in text_lower:
                continue
            if skill in text_lower:
                skills.append(
                    skill.upper()
                    if skill in ["html", "css", "sql", "git"]
                    else skill.capitalize()
                )

        if skills:
            self.collected_info["skills"] = ", ".join(skills)
        elif "none" in text_lower or "no" in text_lower or "nothing" in text_lower:
            self.collected_info["skills"] = "none"
            # Auto-inferred Level=Beginner if not set
            if not self.collected_info["level"]:
                self.collected_info["level"] = "Beginner"
                logger.info("Auto-inferred Level='Beginner' from 'no skills'")

        logger.info(f"Updated collected_info: {self.collected_info}")

    def process_input(self, user_text):
        """
        Process user text, query LLM, handle tool calls with robust retry loop.
        """
        logger.info(f"User: {user_text}")
        self.history.append({"role": "user", "content": user_text})

        # Extract information from user's message
        self._update_collected_info(user_text)

        # DYNAMIC SYSTEM PROMPT: Inject current state so LLM knows what it has
        missing_items = [k for k, v in self.collected_info.items() if v is None]

        force_recommendation = False
        if not missing_items:
            # We have everything! FORCE recommendation immediately.
            status_msg = "STATUS: COMPLETE. Proceeding to recommendation."
            force_recommendation = True
        else:
            status_msg = f"MISSING items: {missing_items}"

        current_state_str = f"""
Current State of Information:
- Goal: {self.collected_info["goal"]}
- Level: {self.collected_info["level"]}
- Skills: {self.collected_info["skills"]}
- Career Path: {self.collected_info["career_path"]}

{status_msg}
"""
        # Update the system message (always the first one)
        self.history[0]["content"] = self.system_prompt + "\n" + current_state_str

        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            attempt += 1

            # Short-circuit: If we have all info, skip LLM thinking and force recommendation
            if force_recommendation:
                content = '{"action": "recommend", "params": {}}'
                logger.info("Auto-triggering recommendation (all fields collected).")
            else:
                try:
                    # Add temperature to encourage variety? Default is 0.8 usually.
                    response = ollama.chat(model=self.model, messages=self.history)
                    content = response["message"]["content"]
                except Exception as e:
                    logger.error(f"Ollama Error: {e}")
                    return "I'm having trouble thinking right now. Is Ollama running?"

            # Check if content looks like JSON
            is_json_action = False
            json_data = {}

            if "{" in content and "}" in content and "action" in content:
                try:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                    json_data = json.loads(json_str)
                    if isinstance(json_data, dict):
                        is_json_action = True
                except:
                    pass

            # CASE 1: Natural Language (Good!)
            if not is_json_action:
                # BAD PHRASE FILTER (Fix for small model regression)
                if "ask the user" in content.lower():
                    logger.warning("Detected bad phrasing: 'Ask the user'. Retrying...")
                    self.history.append({"role": "assistant", "content": content})
                    # Stronger correction
                    self.history.append(
                        {
                            "role": "system",
                            "content": "SYSTEM: You failed the rule. Do NOT describe the question. ASK it directly. Example: 'What are your skills?'",
                        }
                    )
                    continue

                # INTERNAL STATE LEAKAGE FILTER
                if "action:" in content.lower() or "params:" in content.lower():
                    logger.warning(
                        "Detected internal state leakage (Action/Params). Retrying..."
                    )
                    self.history.append({"role": "assistant", "content": content})
                    self.history.append(
                        {
                            "role": "system",
                            "content": "SYSTEM: You are outputting internal debug text. STOP. Just ask the question in natural English.",
                        }
                    )
                    continue

                # Filter out debug information patterns
                if any(
                    phrase in content
                    for phrase in [
                        "Current State of Information",
                        "MISSING items:",
                        "collected_info:",
                        "- Goal:",
                        "- Level:",
                        "- Skills:",
                        "- Career Path:",
                    ]
                ):
                    logger.warning("Detected debug info in response. Filtering...")
                    # Extract only the first line/sentence (the actual question)
                    lines = content.split("\n")
                    content = lines[0].strip()
                    if not content or len(content) < 10:
                        # If first line is empty or too short, retry
                        self.history.append({"role": "assistant", "content": content})
                        self.history.append(
                            {
                                "role": "system",
                                "content": "SYSTEM: Do NOT output debug info about state. Just ask the question naturally.",
                            }
                        )
                        continue

                # Strip "ASK:" prefix if present
                if content.startswith("ASK:"):
                    content = content[4:].strip().replace('"', "")

                self.history.append({"role": "assistant", "content": content})
                return content

            # CASE 2: JSON Action Handling
            action = json_data.get("action")

            if action == "recommend":
                # CHECK HISTORY LENGTH (Prevent premature guessing), UNLESS triggered manually
                if (
                    not force_recommendation and len(self.history) < 10
                ):  # Increased from 6 to 10
                    logger.warning("Recommendation rejected: Conversation too short.")
                    retry_msg = "SYSTEM: Too soon. You need to collect more info. Reply to the user with a QUESTION about their Level or Skills. Do NOT output JSON."
                    self.history.append({"role": "assistant", "content": content})
                    self.history.append({"role": "system", "content": retry_msg})
                    continue

                params = json_data.get("params", {})

                # STRICT VALIDATION: Check self.collected_info (what user actually told us)
                # NOT params (which the model might hallucinate)
                collected_count = sum(
                    1 for v in self.collected_info.values() if v is not None
                )

                if collected_count < 4:
                    # Model is hallucinating! Reject hard.
                    missing_fields = [
                        k for k, v in self.collected_info.items() if v is None
                    ]
                    logger.warning(
                        f"HALLUCINATION DETECTED. User only provided {collected_count}/4 fields. Missing: {missing_fields}"
                    )
                    retry_msg = f"SYSTEM: STOP. The user has NOT told you about: {missing_fields}. You MUST ASK them first. Use the question templates. Do NOT output JSON."
                    self.history.append({"role": "assistant", "content": content})
                    self.history.append({"role": "system", "content": retry_msg})
                    continue

                # VALID: We have all 4 fields from user
                logger.info("Tool Call Valid: recommend_courses")
                # Use collected_info instead of params (to avoid using hallucinated data)
                recommendations = self.lms.recommend_courses(
                    self.collected_info["goal"],
                    self.collected_info["level"],
                    self.collected_info["skills"],
                    self.collected_info["career_path"],
                )

                # RESET STATE so we don't loop forever
                self.collected_info = {
                    "goal": None,
                    "level": None,
                    "skills": None,
                    "career_path": None,
                }
                # Also reset history? Maybe keep context but start fresh with new goal?
                # For now just reset collected info so it doesn't auto-trigger again immediately.

                # Create a clear instruction for the model to explain the result
                tool_msg = (
                    f"SYSTEM: Good job. You found these courses: {json.dumps(recommendations)}.\n"
                    "NOW: Write a short, friendly message to the user recommending the best course.\n"
                    "- FIRST: Write a paragraph explaining WHY this course is perfect.\n"
                    "- SECOND: Say 'I found a great course for you!'\n"
                    "- FINALLY: Place the URL on a separate line at the very END.\n\n"
                    "Example:\n"
                    '"This Python course is perfect for beginners because... I found a great course for you!\n'
                    'https://url..."\n\n'
                    "Do NOT use emojis. Do NOT output JSON. Just talk."
                )
                self.history.append({"role": "assistant", "content": content})
                self.history.append({"role": "system", "content": tool_msg})

                # Final pass to get natural language explanation
                max_final_retries = 2
                final_text = "Here is a recommendation..."

                for _ in range(max_final_retries):
                    final_resp = ollama.chat(model=self.model, messages=self.history)
                    final_text = final_resp["message"]["content"]

                    # Sanity check: If it outputs JSON again, force it to stop
                    if (
                        "{" in final_text
                        and "}" in final_text
                        and "action" in final_text
                    ):
                        logger.warning("Final response was still JSON. Retrying...")
                        self.history.append(
                            {"role": "assistant", "content": final_text}
                        )
                        self.history.append(
                            {
                                "role": "system",
                                "content": "SYSTEM: STOP. Do NOT output JSON. Just write a friendly message to the user.",
                            }
                        )
                        continue
                    else:
                        break

                self.history.append({"role": "assistant", "content": final_text})
                return final_text

            else:
                # Unauthorized Action (e.g. "collect_info")
                logger.warning(f"Ignored unauthorized action: {action}")
                retry_msg = (
                    "Do NOT output JSON. Ask the user a question in natural English."
                )
                self.history.append({"role": "assistant", "content": content})
                self.history.append({"role": "system", "content": retry_msg})
                continue  # Loop again

        # Fallback if retries exhausted
        fallback = "Could you tell me a bit more about what you'd like to learn?"
        self.history.append({"role": "assistant", "content": fallback})
        return fallback


if __name__ == "__main__":
    thinker = Thinker()
    print("Thinker initialized. Type 'quit' to exit.")
    while True:
        user_in = input("You: ")
        if user_in == "quit":
            break
        reply = thinker.process_input(user_in)
        print(f"Avatar: {reply}")
