# AI Avatar MVP

A minimalist, modular AI Avatar pipeline MVP featuring Speech-to-Text, LLM-powered career counseling, Text-to-Speech, and optional lip-sync video generation with SadTalker.

## Features

- **Speech-to-Text (STT)**: Faster-Whisper for accurate transcription
- **LLM Reasoning**: Ollama-powered career counseling with course recommendations
- **Text-to-Speech (TTS)**: Cross-platform TTS (macOS `say` + Linux gTTS)
- **Avatar (Optional)**: SadTalker lip-sync integration for M2 Mac and Linux
- **Course Database**: 20+ curated courses across tech, leadership, sales, and personal development

## Architecture

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Listener   │──▶│   Thinker   │──▶│   Speaker   │──▶│   Avatar    │
│  (Whisper)  │   │   (Ollama)  │   │  (gTTS/say) │   │ (SadTalker) │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

## Prerequisites

### Core Requirements
- Python 3.9+
- FFmpeg
- Ollama (with qwen3:0.6b model)
- PortAudio (for audio recording)

### For SadTalker (Optional)
- **Mac**: M1/M2 Apple Silicon
- **Linux**: NVIDIA GPU (optional, CPU works but slower)
- ~5GB disk space for models

## Quick Start

### 1. Install Dependencies

```bash
# Install system dependencies
# macOS:
brew install portaudio ffmpeg

# Linux:
sudo apt-get install portaudio19-dev ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Install and run Ollama
ollama pull qwen3:0.6b
```

### 2. Run the Avatar (Audio-Only Mode)

```bash
python main.py
```

The system will run in audio-only mode by default. SadTalker is disabled until you set it up.

### 3. Enable SadTalker (Optional)

To enable lip-sync video generation:

```bash
# Run setup script (Mac or Linux)
./setup_sadtalker.sh

# Enable in config
# Edit sadtalker_config.yaml and set: enabled: true

# Run again
python main.py
```

## Configuration

###SadTalker Configuration (`sadtalker_config.yaml`)

```yaml
enabled: false  # Set to true after setup
source_image: resources/IMG_20240708_092636.jpg
bbox_shift: 0   # Adjust mouth openness
device: auto    # auto-detect: cuda/mps/cpu
```

## Docker Deployment

### Build

```bash
docker build -t ai-avatar .
```

### Run

```bash
# Audio-only mode (no SadTalker)
docker run -it --rm ai-avatar

# With SadTalker (mount sadtalker_repo)
docker run -it --rm \
  -v ./sadtalker_repo:/app/sadtalker_repo \
  -v ./outputs:/app/outputs \
  ai-avatar
```

## Project Structure

```
ai-avatar-mvp/
├── core/
│   ├── listener.py    # STT with Faster-Whisper
│   ├── thinker.py     # LLM reasoning with Ollama
│   ├── speaker.py     # Cross-platform TTS
│   ├── avatar.py      # SadTalker integration
│   └── lms_interface.py  # Course database
├── resources/
│   └── IMG_20240708_092636.jpg  # User avatar image
├── outputs/
│   └── videos/         # Generated lip-sync videos
├── setup_sadtalker.sh  # SadTalker installation script
├── sadtalker_config.yaml
├── requirements.txt
├── Dockerfile
└── main.py
```

## Development Notes

- **TTS**: Uses macOS `say` on Mac, gTTS on Linux
- **SadTalker**: Auto-detects MPS (Mac), CUDA (Linux GPU), or CPU
- **MOCK Mode**: Avatar falls back to MOCK if SadTalker unavailable
- **Model**: Uses qwen3:0.6b for fastest inference

## Troubleshooting

### "gTTS not found" on Linux
```bash
pip install gTTS
```

### "SadTalker repo not found"
Run `./setup_sadtalker.sh` to install

### Docker TTS silent
Docker runs headless - audio is saved to files, not played

## License

MIT
