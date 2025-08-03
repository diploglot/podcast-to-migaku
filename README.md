# 🎵 Podcast-to-Migaku

An advanced script that converts podcast audio files to Migaku-compatible format with high-quality subtitles and video generation. Features intelligent text cleaning, duplicate detection, parallel processing, and comprehensive error handling.

## ✨ Features

### Core Functionality
- **🎯 High-Quality Subtitle Generation**: Uses OpenAI Whisper Large model with beam search and quality optimization
- **📝 Multiple Output Formats**: SRT, VTT, TSV, TXT, and JSON formats for maximum compatibility
- **🎬 Professional Video Creation**: Converts audio to 1920x1080 MKV videos with custom background images
- **⚡ Parallel Processing**: Multi-threaded processing for faster batch operations
- **🧹 Smart Text Cleaning**: Removes HTML tags, speaker labels, music annotations, and duplicates
- **📊 Progress Tracking**: Real-time progress bars and comprehensive logging

### Advanced Text Processing
- **HTML/XML Tag Removal**: Cleans `<html>`, `<b>`, and other formatting tags
- **Speaker Label Filtering**: Removes "John:", "Speaker A:", etc.
- **Music Annotation Cleanup**: Strips `[Music]`, `(applause)`, background noise markers
- **Duplicate Detection**: 85% similarity threshold prevents repetitive content
- **Segment Validation**: Filters empty, too-short, or invalid segments
- **Whitespace Normalization**: Consistent formatting across all output

### High-Quality Transcription
- **Large Model Default**: Uses Whisper Large model for maximum accuracy
- **Beam Search**: 5-beam search for optimal word selection
- **Temperature Control**: Deterministic output (temperature=0) for consistency
- **Multiple Attempts**: Best-of-5 attempts for highest quality results
- **Advanced Patience**: Optimized beam search parameters

### User Experience
- **Command-Line Interface**: Full argparse support with customizable options
- **Error Recovery**: Comprehensive error handling and helpful error messages
- **System Validation**: Checks requirements (disk space, memory, dependencies)
- **Flexible Output**: Choose from SRT, VTT, TSV, TXT, and JSON subtitle formats

## 🚀 Quick Start

### Easy Installation (Recommended)
```bash
git clone <repository-url>
cd podcast-to-migaku
python3 setup.py
```

The setup script will automatically:
- Install all Python dependencies
- Download and configure ffmpeg
- Set up PATH variables
- Verify system requirements

### Manual Installation
```bash
pip3 install -r requirements.txt
```

## 📋 Requirements

- **Python 3.8+**
- **Dependencies** (auto-installed by setup script):
  - `openai-whisper==20240930`
  - `tqdm>=4.64.0`
  - `psutil>=5.8.0` 
  - `Pillow>=8.3.0`
  - `imageio-ffmpeg>=0.4.0`
  - `torch>=1.9.0`

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
python3 podcast-to-migaku.py --model large --language en

# Custom output formats and directory
python3 podcast-to-migaku.py --formats srt vtt --output-dir ./my_output

# Parallel processing with verbose logging
python3 podcast-to-migaku.py --workers 4 --verbose

# Full customization
python3 podcast-to-migaku.py \
  --model medium \
  --language ko \
  --formats srt vtt txt json \
  --input-dir ./my-audio-files \
  --workers 2 \
  --output-dir ./complete \
  --image ./custom_image.jpg \
  --verbose
```

### Command-Line Options
- `--model` / `-m`: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) - **Default: `large`**
- `--language` / `-l`: Language code (e.g., `ko`, `en`, `ja`, `es`)
- `--formats` / `-f`: Output formats (`srt`, `vtt`, `tsv`, `txt`, `json`) - **All formats by default**
- `--input-dir`: Input directory with audio files (default: `./to-process`)
- `--workers` / `-w`: Number of parallel workers (default: 2)
- `--output-dir` / `-o`: Output directory (default: `./complete`)
- `--image` / `-i`: Background image path (default: `./image.jpg`)
- `--verbose` / `-v`: Enable detailed logging
- `--batch-size` / `-b`: Processing batch size (default: 5)

## 📤 Output

All processed files are saved to the `complete/` directory:

```
complete/
├── audio_file1.srt          # SubRip subtitles (cleaned, deduplicated)
├── audio_file1.vtt          # WebVTT format for web players
├── audio_file1.tsv          # Tab-separated values (start, end, text)
├── audio_file1.txt          # Plain text transcript
├── audio_file1.json         # Full Whisper output with metadata
├── audio_file1.mkv          # 1920x1080 video with audio and background
└── ...
```

### Text Cleaning Examples

**Before Processing:**
```
<html>John: Hello world</html>
Speaker A: This is a test
[Music] Background music playing
Hello    world   with   spaces
(applause) Thank you everyone
```

**After Processing:**
```
Hello world
This is a test
Background music playing
Hello world with spaces
Thank you everyone
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
- **CPU Intensive**: Use `--workers 1-2` for single/dual core
- **Multi-Core Systems**: Use `--workers 4-8` for faster processing
- **Memory Limited**: Use smaller models (`tiny`, `base`)

## 🐛 Troubleshooting

### Common Issues

**"ffmpeg not found"**
```bash
python3 setup.py  # Automatically installs ffmpeg
```

**"No audio files found"**
- Ensure audio files are in the `to-process/` directory
- Check file extensions are supported
- Use `--input-dir` to specify a different input directory

**Memory errors with large files**
- Use smaller Whisper model: `--model tiny` or `--model base`
- Reduce workers: `--workers 1`

**Poor subtitle quality**
- Use larger model: `--model large`
- Check audio quality and language setting

### Logs and Debugging
- Enable verbose logging: `--verbose`
- Check `podcast_processing.log` for detailed information
- System requirements validation runs automatically

## 🏗️ Architecture

### Key Components
- **`PodcastProcessor`**: Main processing class with text cleaning pipeline
- **`Config`**: Dataclass for configuration management  
- **Text Cleaning**: Regex-based filtering and normalization
- **Parallel Processing**: ThreadPoolExecutor for concurrent operations
- **Error Handling**: Comprehensive try-catch with detailed logging

### Text Processing Pipeline
1. **Raw Whisper Output** → 2. **HTML Tag Removal** → 3. **Speaker Label Filtering** → 4. **Music Annotation Cleanup** → 5. **Duplicate Detection** → 6. **Segment Validation** → 7. **Clean Output**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Made with ❤️ for language learners and content creators** 