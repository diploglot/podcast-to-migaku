#!/usr/bin/env python3
"""
Setup script for podcast-to-migaku
Installs dependencies and sets up ffmpeg automatically
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f"Running: {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages")

def setup_ffmpeg():
    """Set up ffmpeg automatically"""
    print("Setting up ffmpeg...")
    
    # Check if ffmpeg is already available
    if shutil.which('ffmpeg'):
        print("✅ ffmpeg is already installed and available in PATH")
        return True
    
    # Install imageio-ffmpeg and get the binary
    if not run_command(f"{sys.executable} -m pip install imageio-ffmpeg", "Installing imageio-ffmpeg"):
        return False
    
    try:
        # Get ffmpeg path from imageio
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"Found ffmpeg at: {ffmpeg_path}")
        
        # Create local bin directory
        local_bin = Path.home() / '.local' / 'bin'
        local_bin.mkdir(parents=True, exist_ok=True)
        
        # Copy ffmpeg to local bin
        local_ffmpeg = local_bin / 'ffmpeg'
        shutil.copy2(ffmpeg_path, local_ffmpeg)
        local_ffmpeg.chmod(0o755)
        
        print(f"✅ ffmpeg installed to {local_ffmpeg}")
        
        # Add to PATH in shell profiles
        path_line = f'export PATH="{local_bin}:$PATH"'
        
        for shell_profile in ['.bashrc', '.bash_profile', '.zshrc']:
            profile_path = Path.home() / shell_profile
            if profile_path.exists() or shell_profile == '.zshrc':  # Create zshrc if it doesn't exist
                try:
                    with open(profile_path, 'r') as f:
                        content = f.read()
                    
                    if str(local_bin) not in content:
                        with open(profile_path, 'a') as f:
                            f.write(f'\n{path_line}\n')
                        print(f"Added PATH to {shell_profile}")
                except Exception as e:
                    print(f"Warning: Could not update {shell_profile}: {e}")
        
        print("✅ ffmpeg setup complete")
        print(f"Please restart your terminal or run: export PATH=\"{local_bin}:$PATH\"")
        return True
        
    except Exception as e:
        print(f"Error setting up ffmpeg: {e}")
        return False

def main():
    """Main setup function"""
    print("🎵 Podcast-to-Migaku Setup Script")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Setup ffmpeg
    if not setup_ffmpeg():
        print("❌ Failed to setup ffmpeg")
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Place your audio files in this directory")
    print("2. Add an 'image.jpg' file for video generation")
    print("3. Run: python3 podcast-to-migaku.py --help")
    print("\nExample usage:")
    print("  python3 podcast-to-migaku.py --model small --language ko --formats srt vtt")

if __name__ == "__main__":
    main()