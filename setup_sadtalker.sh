#!/bin/bash
# SadTalker Setup Script for AI Avatar MVP
# This script installs SadTalker for lip-sync avatar generation

set -e  # Exit on error

echo "========================================="
echo "  SadTalker Setup for AI Avatar MVP"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on  macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}✓${NC} Detected macOS (Apple Silicon optimizations will be used)"
    IS_MAC=true
else
    echo -e "${GREEN}✓${NC} Detected Linux"
    IS_MAC=false
fi

# Check Python version
echo ""
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
    echo -e "${RED}✗${NC} Python 3.8+ required. Current: $PYTHON_VERSION"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python version OK"

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg found (system)"
else
    echo -e "${YELLOW}!${NC} FFmpeg not found in PATH"
    echo "Checking for imageio-ffmpeg (bundled FFmpeg)..."
    
    # Check if imageio-ffmpeg is installed
    if python3 -c "import imageio_ffmpeg" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} imageio-ffmpeg found (bundled FFmpeg binaries)"
        echo "SadTalker will use bundled FFmpeg from imageio-ffmpeg"
    else
        echo -e "${YELLOW}!${NC} Installing imageio-ffmpeg for bundled FFmpeg..."
        pip install imageio-ffmpeg
        echo -e "${GREEN}✓${NC} imageio-ffmpeg installed"
    fi
fi

# Clone SadTalker repository
echo ""
echo "Cloning SadTalker repository..."
SADTALKER_DIR="sadtalker_repo"

if [ -d "$SADTALKER_DIR" ]; then
    echo -e "${YELLOW}!${NC} SadTalker directory already exists. Skipping clone."
else
    git clone https://github.com/OpenTalker/SadTalker.git "$SADTALKER_DIR"
    echo -e "${GREEN}✓${NC} SadTalker repository cloned"
fi

# Install SadTalker dependencies
echo ""
echo "Installing SadTalker dependencies..."
cd "$SADTALKER_DIR"

# Install PyTorch (different for Mac vs Linux)
echo "Installing PyTorch..."
if [ "$IS_MAC" = true ]; then
    # Mac with MPS support
    pip install torch torchvision torchaudio
else
    # Linux (CPU version, user can upgrade to CUDA if needed)
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install other requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}!${NC} requirements.txt not found, installing core dependencies manually"
    pip install opencv-python imageio scikit-image yacs pyyaml face-alignment resampy
fi

# Download model weights
echo ""
echo "Downloading SadTalker model weights (~5GB)..."
echo -e "${YELLOW}!${NC} This may take several minutes..."

if [ -f "scripts/download_models.sh" ]; then
    bash scripts/download_models.sh
    echo -e "${GREEN}✓${NC} Model weights downloaded"
else
    echo -e "${RED}✗${NC} Download script not found. You may need to download models manually."
fi

cd ..

# Create config file
echo ""
echo "Creating configuration file..."
cat > sadtalker_config.yaml << 'EOF'
# SadTalker Configuration for AI Avatar MVP

enabled: false  # Set to true after successful setup
source_image: resources/IMG_20240708_092636.jpg
bbox_shift: 0   # Adjust mouth openness (positive = more open)
output_dir: outputs/videos
device: auto    # auto-detect: cuda/mps/cpu

# Advanced options
still: true     # Use still mode for single image
preprocess: crop  # crop, resize, or full
EOF

echo -e "${GREEN}✓${NC} Configuration file created: sadtalker_config.yaml"

# Test installation
echo ""
echo "Testing SadTalker installation..."
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'MPS available: {torch.backends.mps.is_available()}'); print(f'CUDA available: {torch.cuda.is_available()}')" || echo -e "${YELLOW}!${NC} Could not verify PyTorch installation"

echo ""
echo "========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Enable SadTalker in sadtalker_config.yaml (set enabled: true)"
echo "2. Run: python main.py"
echo ""
echo "Note: On first run, additional model files may be downloaded automatically."
echo ""
