import os
import sys
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import logging
from tqdm import tqdm
import whisper
import json
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import psutil
from PIL import Image

@dataclass
class Config:
    """Configuration class for podcast processing"""
    model_size: str = 'large'  # Default to large for high quality
    language: str = 'ko'
    output_formats: List[str] = None
    max_workers: int = 2
    verbose: bool = False
    
    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = ['srt', 'vtt', 'tsv', 'txt', 'json']

# Supported audio file extensions
AUDIO_EXTS = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.mp4']

# Default paths
BASE_DIR = Path(__file__).parent.resolve()
TO_PROCESS_DIR = BASE_DIR / 'to-process'
COMPLETE_DIR = BASE_DIR / 'complete'
IMAGE_FILE = BASE_DIR / 'image.jpg'

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, 
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(BASE_DIR / 'podcast_processing.log')
        ]
    )

def check_system_requirements() -> Dict[str, bool]:
    """Check system requirements and available resources"""
    requirements = {
        'ffmpeg': shutil.which('ffmpeg') is not None,
        'disk_space': psutil.disk_usage(str(BASE_DIR)).free > 1_000_000_000,  # 1GB minimum
        'memory': psutil.virtual_memory().available > 2_000_000_000,  # 2GB minimum
        'image_file': IMAGE_FILE.exists()
    }
    return requirements

def validate_image_file(image_path: Path) -> bool:
    """Validate that the image file is valid"""
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception as e:
        logging.error(f"Invalid image file {image_path}: {e}")
        return False

class PodcastProcessor:
    """Simplified processor class for high-quality Whisper transcription"""
    
    def __init__(self, config: Config, output_dir: Path):
        self.config = config
        self.output_dir = output_dir
        self.model: Optional[whisper.Whisper] = None
        self.output_dir.mkdir(exist_ok=True)
    
    def load_model(self) -> bool:
        """Load Whisper model with error handling"""
        try:
            logging.info(f"Loading Whisper model ({self.config.model_size})...")
            self.model = whisper.load_model(self.config.model_size)
            logging.info("Model loaded successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            return False
    
    def write_srt(self, segments: List[Dict], srt_path: Path) -> None:
        """Write SRT subtitle file"""
        try:
            with open(srt_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments):
                    start = segment['start']
                    end = segment['end']
                    text = segment['text'].strip()
                    f.write(f"{i+1}\n")
                    f.write(f"{self._format_srt_time(start)} --> {self._format_srt_time(end)}\n")
                    f.write(f"{text}\n\n")
            logging.info(f"SRT file written: {srt_path} ({len(segments)} segments)")
        except Exception as e:
            logging.error(f"Failed to write SRT file {srt_path}: {e}")
            raise

    def write_vtt(self, segments: List[Dict], vtt_path: Path) -> None:
        """Write VTT subtitle file"""
        try:
            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")
                for segment in segments:
                    start = self._format_vtt_time(segment['start'])
                    end = self._format_vtt_time(segment['end'])
                    text = segment['text'].strip()
                    f.write(f"{start} --> {end}\n{text}\n\n")
            logging.info(f"VTT file written: {vtt_path} ({len(segments)} segments)")
        except Exception as e:
            logging.error(f"Failed to write VTT file {vtt_path}: {e}")
            raise

    def write_tsv(self, segments: List[Dict], tsv_path: Path) -> None:
        """Write TSV (Tab-Separated Values) subtitle file"""
        try:
            with open(tsv_path, 'w', encoding='utf-8') as f:
                f.write("start\tend\ttext\n")
                for segment in segments:
                    start = f"{segment['start']:.3f}"
                    end = f"{segment['end']:.3f}"
                    text = segment['text'].strip().replace('\t', ' ').replace('\n', ' ')
                    f.write(f"{start}\t{end}\t{text}\n")
            logging.info(f"TSV file written: {tsv_path} ({len(segments)} segments)")
        except Exception as e:
            logging.error(f"Failed to write TSV file {tsv_path}: {e}")
            raise

    def write_txt(self, text: str, txt_path: Path) -> None:
        """Write plain text file"""
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text.strip() + '\n')
            logging.info(f"TXT file written: {txt_path}")
        except Exception as e:
            logging.error(f"Failed to write TXT file {txt_path}: {e}")
            raise

    def write_json(self, result: Dict[str, Any], json_path: Path) -> None:
        """Write JSON result file"""
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logging.info(f"JSON file written: {json_path}")
        except Exception as e:
            logging.error(f"Failed to write JSON file {json_path}: {e}")
            raise

    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT format"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    def _format_vtt_time(self, seconds: float) -> str:
        """Format time for VTT format"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02}.{ms:03}"

    def generate_subtitles(self, audio_path: Path) -> bool:
        """Generate high-quality subtitles for audio file"""
        if not self.model:
            logging.error("Whisper model not loaded")
            return False
        
        try:
            logging.info(f"Transcribing {audio_path.name}...")
            
            # Simple, reliable transcription settings
            result = self.model.transcribe(
                str(audio_path),
                language=self.config.language,
                verbose=False,  # Disable verbose output to prevent spam
                word_timestamps=False
                # Removed beam_size, best_of, patience, and temperature 
                # as they can cause repetition loops with certain audio
            )
            
            base_path = self.output_dir / audio_path.stem
            
            # Write all requested formats
            if 'srt' in self.config.output_formats:
                self.write_srt(result['segments'], base_path.with_suffix('.srt'))
            if 'vtt' in self.config.output_formats:
                self.write_vtt(result['segments'], base_path.with_suffix('.vtt'))
            if 'tsv' in self.config.output_formats:
                self.write_tsv(result['segments'], base_path.with_suffix('.tsv'))
            if 'txt' in self.config.output_formats:
                self.write_txt(result['text'], base_path.with_suffix('.txt'))
            if 'json' in self.config.output_formats:
                self.write_json(result, base_path.with_suffix('.json'))
            
            logging.info(f"Subtitles for {audio_path.name} completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to generate subtitles for {audio_path}: {e}")
            return False

    def _build_ffmpeg_command(self, audio_path: Path, image_path: Path, output_mkv: Path) -> List[str]:
        """Build ffmpeg command for video conversion"""
        return [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', str(image_path),
            '-i', str(audio_path),
            '-vf', 'scale=1080:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'libx264',
            '-tune', 'stillimage',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            str(output_mkv)
        ]

    def convert_audio_to_mkv(self, audio_path: Path, image_path: Path, output_mkv: Path) -> bool:
        """Convert audio to MKV video with background image"""
        try:
            logging.info(f"Converting {audio_path.name} to video...")
            cmd = self._build_ffmpeg_command(audio_path, image_path, output_mkv)
            
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            logging.info(f"Video saved: {output_mkv.name}")
            return True
            
        except subprocess.TimeoutExpired:
            logging.error(f"FFmpeg timeout for {audio_path}")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg failed for {audio_path}: {e.stderr}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error converting {audio_path}: {e}")
            return False

    def move_processed_file(self, file_path: Path) -> bool:
        """Move processed audio file to complete directory"""
        try:
            destination = self.output_dir / file_path.name
            if destination.exists():
                logging.warning(f"File {destination.name} already exists in complete directory, removing original")
                file_path.unlink()
                return True
            shutil.move(str(file_path), str(destination))
            logging.info(f"Moved {file_path.name} to complete directory")
            return True
        except Exception as e:
            logging.error(f"Failed to move {file_path.name} to complete directory: {e}")
            return False

def find_audio_files(directory: Path) -> List[Path]:
    """Find all audio files in directory"""
    audio_files = []
    for ext in AUDIO_EXTS:
        audio_files.extend(directory.glob(f"*{ext}"))
        audio_files.extend(directory.glob(f"*{ext.upper()}"))
    return sorted(audio_files)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="High-quality Whisper transcription for audio files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--model', '-m',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='large',
        help='Whisper model size (larger = better quality)'
    )
    
    parser.add_argument(
        '--language', '-l',
        default='ko',
        help='Language code for transcription'
    )
    
    parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['srt', 'vtt', 'tsv', 'txt', 'json'],
        default=['srt', 'vtt', 'tsv', 'txt', 'json'],
        help='Output subtitle formats'
    )
    
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=TO_PROCESS_DIR,
        help='Input directory containing audio files'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=COMPLETE_DIR,
        help='Output directory for processed files'
    )
    
    parser.add_argument(
        '--image', '-i',
        type=Path,
        default=IMAGE_FILE,
        help='Background image for video generation'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def process_files(processor: PodcastProcessor, files: List[Path], image_path: Path) -> Dict[str, int]:
    """Process files sequentially for best quality"""
    stats = {'success': 0, 'failed': 0, 'moved': 0}
    
    for file_path in tqdm(files, desc="Processing files"):
        try:
            # Generate subtitles
            subtitle_success = processor.generate_subtitles(file_path)
            
            # Convert to video
            mkv_path = processor.output_dir / f"{file_path.stem}.mkv"
            video_success = False
            
            if not mkv_path.exists():
                video_success = processor.convert_audio_to_mkv(file_path, image_path, mkv_path)
            else:
                logging.info(f"Video for {file_path.name} already exists, skipping")
                video_success = True
            
            # Move processed file if both operations succeeded
            if subtitle_success and video_success:
                moved = processor.move_processed_file(file_path)
                stats['success'] += 1
                if moved:
                    stats['moved'] += 1
            else:
                stats['failed'] += 1
                
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")
            stats['failed'] += 1
    
    return stats

def main():
    """Main function"""
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Check system requirements
    requirements = check_system_requirements()
    missing_reqs = [req for req, available in requirements.items() if not available]
    
    if missing_reqs:
        logging.error(f"Missing requirements: {', '.join(missing_reqs)}")
        if 'ffmpeg' in missing_reqs:
            logging.error("Install ffmpeg: https://ffmpeg.org/download.html")
        if 'disk_space' in missing_reqs:
            logging.error("Insufficient disk space (need at least 1GB)")
        if 'memory' in missing_reqs:
            logging.error("Insufficient memory (need at least 2GB)")
        if 'image_file' in missing_reqs:
            logging.error(f"Image file not found: {args.image}")
        return 1
    
    # Validate image file
    if not validate_image_file(args.image):
        logging.error(f"Invalid or corrupted image file: {args.image}")
        return 1
    
    # Ensure input directory exists
    args.input_dir.mkdir(exist_ok=True)
    
    # Find audio files
    files = find_audio_files(args.input_dir)
    if not files:
        logging.info(f"No audio files found in {args.input_dir}")
        logging.info(f"Please place your audio files in the '{args.input_dir.name}' directory")
        return 0
    
    logging.info(f"Found {len(files)} audio files to process")
    for file in files:
        logging.info(f"  - {file.name}")
    
    # Create config and processor
    config = Config(
        model_size=args.model,
        language=args.language,
        output_formats=args.formats,
        verbose=args.verbose
    )
    
    processor = PodcastProcessor(config, args.output_dir)
    
    # Load Whisper model
    if not processor.load_model():
        logging.error("Failed to load Whisper model")
        return 1
    
    # Process files
    try:
        stats = process_files(processor, files, args.image)
        
        # Print summary
        logging.info("Processing complete:")
        logging.info(f"  Successful: {stats['success']}")
        logging.info(f"  Failed: {stats['failed']}")
        logging.info(f"  Files moved to complete: {stats['moved']}")
        
        return 0 if stats['failed'] == 0 else 1
        
    except KeyboardInterrupt:
        logging.info("Processing interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())