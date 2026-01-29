# Audio Steganography Library

Python library for hiding and extracting images in WAV audio files using LSB (Least Significant Bit) steganography.

## Features

- 🎵 **Hide images in WAV files** - Imperceptible to human hearing
- 🖼️ **Extract hidden images** - Perfect recovery of embedded data
- 📏 **Automatic image resizing** - Fits images to audio capacity
- 🔍 **Capacity checking** - Know how much data you can hide
- 🛠️ **CLI and Library** - Use as command-line tool or Python library
- ✅ **Robust error handling** - Clear error messages and validation

## Installation

### From Source

```bash
git clone https://github.com/yourusername/audio-steg.git
cd audio-steg
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Command Line Interface

```bash
# Hide an image in audio with automatic resizing
python cli/steg.py hide sound.wav secret.jpg output.wav --auto-resize

# Extract hidden image
python cli/steg.py extract output.wav recovered.jpg

# Check audio capacity
python cli/steg.py capacity sound.wav

# Resize image to fit
python cli/steg.py resize -a sound.wav large.jpg resized.jpg

# Compare two images
python cli/steg.py compare original.jpg extracted.jpg
```

### Python Library

```python
from audio_steg import hide_image, extract_image, get_audio_capacity

# Check capacity
capacity = get_audio_capacity("audio.wav")
print(f"Can hide up to {capacity['capacity_kb']:.1f} KB")

# Hide an image
result = hide_image("audio.wav", "secret.jpg", "stego.wav")
print(f"Capacity used: {result['capacity_usage']:.2f}%")

# Extract the image
extract_image("stego.wav", "recovered.jpg")
```

## Library API

### Core Functions

#### `hide_image(wav_path, image_path, output_path, verbose=True, auto_resize=False)`

Hide an image inside a WAV file.

**Parameters:**

- `wav_path` (str): Input WAV file path
- `image_path` (str): Image file to hide
- `output_path` (str): Output WAV file path
- `verbose` (bool): Print progress information
- `auto_resize` (bool): Automatically resize image if it's too large

**Returns:**

- `dict`: Operation results including capacity usage

**Raises:**

- `ValueError`: If image is too large
- `FileNotFoundError`: If input files don't exist

#### `extract_image(wav_path, output_image_path, verbose=True)`

Extract a hidden image from a WAV file.

**Parameters:**

- `wav_path` (str): WAV file containing hidden image
- `output_image_path` (str): Output image file path
- `verbose` (bool): Print progress information

**Returns:**

- `dict`: Extraction results including image dimensions

**Raises:**

- `ValueError`: If no valid image data found
- `FileNotFoundError`: If WAV file doesn't exist

### Utility Functions

#### `get_audio_capacity(wav_path)`

Get the steganography capacity of a WAV file.

**Returns:**

- `dict`: Capacity information (samples, bytes, KB, duration, etc.)

#### `resize_image_for_audio(image_path, output_path, wav_path=None, max_bytes=None, verbose=True)`

Resize an image to fit within audio capacity.

**Parameters:**

- `image_path` (str): Input image path
- `output_path` (str): Output resized image path
- `wav_path` (str, optional): WAV file to check capacity
- `max_bytes` (int, optional): Maximum bytes for image
- `verbose` (bool): Print progress information

**Returns:**

- `dict`: Resize operation results

#### `compare_images(img1_path, img2_path, verbose=True)`

Compare two images pixel by pixel.

**Returns:**

- `dict`: Comparison results including similarity percentage

## How It Works

The library uses **LSB (Least Significant Bit) steganography**:

1. **Hiding**: The least significant bit of each audio sample is replaced with one bit from the image data
2. **Header**: A 12-byte header stores image dimensions and data size
3. **Extraction**: LSBs are read from audio samples to reconstruct the image

Since only the LSB is modified, the audio quality change is imperceptible to human ears.

## Project Structure

```
audio-steg/
├── audio_steg/           # Main library package
│   ├── __init__.py       # Package initialization
│   ├── core.py           # Core hide/extract functions
│   └── utils.py          # Utility functions
├── cli/                  # Command-line interface
│   └── steg.py           # CLI entry point
├── examples/             # Example scripts
│   └── basic_usage.py    # Usage examples
├── tests/                # Test files
│   └── test_basic.py     # Basic tests
├── docs/                 # Documentation
│   └── API.md            # API documentation
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## Examples

See the `examples/` directory for complete examples:

```bash
python examples/basic_usage.py
```

## Capacity Requirements

The WAV file must be large enough to hold the image data:

**Formula:** Required samples ≥ (Image Width × Height × 3 + 12) × 8

**Example:**

- 100×100 pixel image needs ~240,000 samples
- At 44.1kHz, this is ~5.4 seconds of audio

## Limitations

- Only works with uncompressed WAV files
- Image is converted to RGB (transparency lost)
- Audio file must be large enough for the image
- LSB steganography can be detected by steganalysis tools

## Security Note

This is a steganography implementation for educational purposes. For secure communication:

- Encrypt images before hiding them
- Use additional security measures
- Be aware that LSB steganography can be detected

## Testing

Run the test suite:

```bash
python tests/test_basic.py
```

## License

MIT License - Free to use for educational and personal projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Version

1.0.0
