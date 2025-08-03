# 🎵 Podcast-to-Migaku

A reliable Python script that converts audio files to Migaku-compatible format with high-quality subtitles and video generation using OpenAI Whisper.

## ✨ Features

### Core Functionality
- **🎯 High-Quality Subtitle Generation**: Uses OpenAI Whisper Large model for accurate transcription
- **📝 Multiple Output Formats**: SRT, VTT, TSV, TXT, and JSON formats for maximum compatibility
- **🎬 Video Creation**: Converts audio to 1920x1080 MKV videos with custom background images
- **📊 Progress Tracking**: Real-time progress bars and comprehensive logging
- **🔧 System Validation**: Automatic checks for dependencies, disk space, and memory

### Transcription Quality
- **Large Model Default**: Uses Whisper Large model for maximum accuracy
- **Korean Language Optimized**: Defaults to Korean (`ko`) with customizable language support
- **Reliable Processing**: Simple, stable transcription settings to avoid loops and errors
- **Sequential Processing**: Processes files one at a time for consistent quality

### User Experience
- **Command-Line Interface**: Full argparse support with customizable options
- **Error Recovery**: Comprehensive error handling and helpful error messages
- **Automatic File Management**: Moves processed files to complete directory
- **Flexible Configuration**: Choose models, languages, formats, and directories

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/diploglot/podcast-to-migaku.git
cd podcast-to-migaku
pip install -r requirements.txt
```

## 📋 Requirements

- **Python 3.8+**
- **FFmpeg**: Required for video conversion
- **Dependencies**:
  - `openai-whisper`
  - `tqdm`
  - `psutil` 
  - `Pillow`

## 📁 Setup

1. **Add Audio Files**: Place your audio files in the `to-process/` directory
   - The script will automatically create this directory
   - Supported: `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`, `.mp4`

2. **Add Background Image**: Place `image.jpg` in the project directory
   - Used as video background
   - Any aspect ratio (automatically scaled and padded)

## 🎮 Usage

### Basic Usage
```bash
python3 podcast-to-migaku.py
```

### Advanced Options
```bash
# Use different model and language
python3 podcast-to-migaku.py --model medium --language en

# Custom output formats and directory
python3 podcast-to-migaku.py --formats srt vtt --output-dir ./my_output

# Full customization
python3 podcast-to-migaku.py \
  --model medium \
  --language ko \
  --formats srt vtt txt json \
  --input-dir ./my-audio-files \
  --output-dir ./complete \
  --image ./custom_image.jpg \
  --verbose
```

### Command-Line Options
- `--model` / `-m`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) - **Default: `large`**
- `--language` / `-l`: Language code (e.g., `ko`, `en`, `ja`, `es`) - **Default: `ko`**
- `--formats` / `-f`: Output formats (`srt`, `vtt`, `tsv`, `txt`, `json`) - **All formats by default**
- `--input-dir`: Input directory with audio files (default: `./to-process`)
- `--output-dir` / `-o`: Output directory (default: `./complete`)
- `--image` / `-i`: Background image path (default: `./image.jpg`)
- `--verbose` / `-v`: Enable detailed logging

## 📤 Output

All processed files are saved to the `complete/` directory:

```
complete/
├── audio_file1.srt          # SubRip subtitles
├── audio_file1.vtt          # WebVTT format for web players
├── audio_file1.tsv          # Tab-separated values (start, end, text)
├── audio_file1.txt          # Plain text transcript
├── audio_file1.json         # Full Whisper output with metadata
├── audio_file1.mkv          # 1920x1080 video with audio and background
├── audio_file1.mp4          # Original audio file (moved after processing)
└── ...
```

## 🔧 Advanced Configuration

### Model Selection Guide
- **`tiny`**: Fastest, least accurate (~32 MB) - For testing only
- **`base`**: Good balance (~74 MB) - For quick processing  
- **`small`**: Better accuracy (~244 MB) - Good for most use cases
- **`medium`**: High accuracy (~769 MB) - Professional quality
- **`large`**: **Best accuracy (~1550 MB) - DEFAULT for highest quality**

### Language Codes
Common languages: `ko` (Korean), `en` (English), `ja` (Japanese), `es` (Spanish), `fr` (French), `de` (German), `zh` (Chinese)

### Performance Tuning
- **Memory Limited**: Use smaller models (`tiny`, `base`, `small`)
- **High Quality**: Use `large` model (default)
- **Fast Processing**: Use `medium` or `small` models

## 🐛 Troubleshooting

### Common Issues

**"ffmpeg not found"**
- Install FFmpeg: https://ffmpeg.org/download.html
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

**"No audio files found"**
- Ensure audio files are in the `to-process/` directory
- Check file extensions are supported
- Use `--input-dir` to specify a different input directory

**Memory errors with large files**
- Use smaller Whisper model: `--model tiny` or `--model base`

**Poor subtitle quality**
- Use larger model: `--model large` (default)
- Check audio quality and language setting

### Logs and Debugging
- Enable verbose logging: `--verbose`
- Check `podcast_processing.log` for detailed information
- System requirements validation runs automatically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Made with ❤️ for language learners and content creators** 