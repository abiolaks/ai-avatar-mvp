# AI Avatar MVP with LMS Integration

A minimalist AI Avatar pipeline that listens to user speech, thinks using a local LLM (Ollama), speaks using offline TTS, and (optionally) animates using MuseTalk.

It features an LMS Integration that recommends courses based on user goals, skills, and career path.

## Prerequisites

1.  **Python 3.10+**
2.  **Ollama** (Running locally)
    -   Install from [ollama.com](https://ollama.com/)
    -   Pull the model: `ollama pull llama3`
3.  **System Dependencies** (for Audio/Video):
    -   FFmpeg
    -   PortAudio (Optional on macOS if using `sounddevice` wheel; Linux may require `sudo apt-get install portaudio19-dev`)

## Installation

1.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## MuseTalk Setup (Avatar Animation)

To enable real-time lip-sync, you must install **MuseTalk**.
The project attempts to use a cloned repository in `musetalk_repo`.

1.  Clone MuseTalk inside the project root:
    ```bash
    git clone https://github.com/TMElyralab/MuseTalk.git musetalk_repo
    ```
2.  Follow MuseTalk's installation guide to download pre-trained weights.
3.  If MuseTalk is not found or configured, the Avatar will run in **MOCK** mode (printing status only).

## Usage

Run the start script:
```bash
./run_avatar.sh
```

Or run manually:
```bash
python main.py
```

## Features

-   **Listener**: Captures microphone input and transcribes using `faster-whisper`.
-   **Thinker**: Uses `llama3` to converse and extract user parameters (Goal, Level, Skills, Career).
-   **LMS Interface**: Recommends courses based on extracted parameters.
-   **Speaker**: Synthesizes speech using `pyttsx3` (Offline).
-   **Avatar**: Wraps MuseTalk for video generation (or falls back to mock).

## Deployment (Docker)

To build and run in Docker (Note: Audio device forwarding is complex in Docker):
```bash
docker build -t ai-avatar .
# Running with audio device access requires flags like --device /dev/snd (Linux)
```
