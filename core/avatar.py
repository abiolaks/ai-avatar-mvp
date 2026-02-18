import os
import subprocess
import logging
import time
import yaml
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Avatar:
    def __init__(self, sadtalker_path="sadtalker_repo", config_path="sadtalker_config.yaml"):
        self.sadtalker_path = os.path.abspath(sadtalker_path)
        self.config_path = config_path
        self.config = self._load_config()
        self.repo_exists = os.path.exists(self.sadtalker_path)
        self.device = self._detect_device()
        
        if not self.repo_exists:
            logger.warning(f"SadTalker repo not found at {self.sadtalker_path}. Avatar will run in MOCK mode.")
            logger.info("To enable SadTalker: Run './setup_sadtalker.sh' to install")
        elif not self.config.get('enabled', False):
            logger.warning("SadTalker is installed but disabled in config. Avatar will run in MOCK mode.")
            logger.info("To enable: Set 'enabled: true' in sadtalker_config.yaml")
        else:
            logger.info(f"SadTalker repo detected. Using device: {self.device}")
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}. Using defaults.")
            return {'enabled': False, 'device': 'auto', 'bbox_shift': 0}
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config or {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {'enabled': False}
    
    def _detect_device(self):
        """Detect available compute device (CUDA/MPS/CPU)."""
        try:
            import torch
            
            # Check config preference
            config_device = self.config.get('device', 'auto')
            if config_device != 'auto':
                return config_device
            
            # Auto-detect
            if torch.cuda.is_available():
                return 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return 'mps'  # Apple Silicon
            else:
                return 'cpu'
        except ImportError:
            logger.warning("PyTorch not installed. Defaulting to CPU.")
            return 'cpu'

    def generate_video(self, audio_path, image_path=None, output_path="outputs/videos/result.mp4"):
        """
        Generate lip-synced video using SadTalker.
        Falls back to MOCK mode if SadTalker unavailable.
        """
        # Use config image if not provided
        if image_path is None:
            image_path = self.config.get('source_image', 'resources/IMG_20240708_092636.jpg')
        
        # Check if SadTalker is enabled and available
        if not self.repo_exists or not self.config.get('enabled', False):
            logger.info(f"[MOCK] Generating video for {audio_path} with {image_path} -> {output_path}")
            time.sleep(0.5)  # Simulate processing
            # Create dummy file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write("dummy video content")
            return output_path

        logger.info(f"Generating lip-sync video using SadTalker...")
        
        try:
            return self._run_sadtalker_inference(audio_path, image_path, output_path)
        except Exception as e:
            logger.error(f"SadTalker inference failed: {e}")
            logger.info("Falling back to MOCK mode")
            # Fallback to mock
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write("dummy video content")
            return output_path
    
    def _run_sadtalker_inference(self, audio_path, image_path, output_path):
        """Run SadTalker inference script."""
        # Find inference script
        inference_script = os.path.join(self.sadtalker_path, "inference.py")
        
        if not os.path.exists(inference_script):
            raise FileNotFoundError(f"Inference script not found: {inference_script}")
        
        # Prepare output directory
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Build command
        bbox_shift = self.config.get('bbox_shift', 0)
        still_mode = self.config.get('still', True)
        preprocess = self.config.get('preprocess', 'crop')
        
        cmd = [
            sys.executable, inference_script,
            "--driven_audio", audio_path,
            "--source_image", image_path,
            "--result_dir", output_dir,
            "--cpu", # Force CPU to avoid MPS hanging issues
            "--preprocess", preprocess
        ]
        
        if still_mode:
            cmd.append("--still")
        
        logger.info(f"Running SadTalker: {' '.join(cmd)}")
        
        # Run inference
        result = subprocess.run(
            cmd,
            cwd=self.sadtalker_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info("SadTalker inference completed")
        logger.info(f"STDOUT: {result.stdout}")
        logger.info(f"STDERR: {result.stderr}")
        
        # SadTalker typically creates output in result_dir
        # Find the generated video file
        generated_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
        if generated_files:
            generated_path = os.path.join(output_dir, generated_files[0])
            # Move to expected output path if different
            if generated_path != output_path:
                os.rename(generated_path, output_path)
            logger.info(f"Video generated: {output_path}")
            return output_path
        else:
            raise FileNotFoundError("SadTalker did not generate output video")

if __name__ == "__main__":
    avatar = Avatar()
    print(f"SadTalker available: {avatar.repo_exists}")
    print(f"Enabled: {avatar.config.get('enabled', False)}")
    print(f"Device: {avatar.device}")

