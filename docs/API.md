# API Documentation

## audio_steg Package

The `audio_steg` package provides a simple API for hiding and extracting images in WAV audio files.

## Installation

```python
import audio_steg
```

## Core Functions

### hide_image()

```python
audio_steg.hide_image(wav_path, image_path, output_path, verbose=True, auto_resize=False)
```

Hide an image inside a WAV audio file using LSB steganography.

**Parameters:**

- **wav_path** (*str*): Path to the input WAV file (carrier audio)
- **image_path** (*str*): Path to the image file to hide
- **output_path** (*str*): Path where the output WAV file will be saved
- **verbose** (*bool*, optional): If True, prints progress information. Default: True
- **auto_resize** (*bool*, optional): If True, automatically resizes image if too large. Default: False

**Returns:**

*dict* with the following keys:

- `success` (*bool*): True if operation succeeded
- `image_size` (*tuple*): (width, height) of the hidden image
- `data_bytes` (*int*): Number of bytes of image data
- `capacity_usage` (*float*): Percentage of audio capacity used
- `output_file` (*str*): Path to the output file

**Raises:**

- `ValueError`: If the image is too large for the audio file
- `FileNotFoundError`: If input files don't exist

**Example:**

```python
result = audio_steg.hide_image("audio.wav", "secret.jpg", "stego.wav")
print(f"Used {result['capacity_usage']:.2f}% of capacity")
```

---

### extract_image()

```python
audio_steg.extract_image(wav_path, output_image_path, verbose=True)
```

Extract a hidden image from a WAV audio file.

**Parameters:**

- **wav_path** (*str*): Path to the WAV file containing hidden image
- **output_image_path** (*str*): Path where extracted image will be saved
- **verbose** (*bool*, optional): If True, prints progress information. Default: True

**Returns:**

*dict* with the following keys:

- `success` (*bool*): True if operation succeeded
- `image_size` (*tuple*): (width, height) of the extracted image
- `data_bytes` (*int*): Number of bytes of image data
- `output_file` (*str*): Path to the output file

**Raises:**

- `ValueError`: If no valid image data is found or data is corrupted
- `FileNotFoundError`: If WAV file doesn't exist

**Example:**

```python
result = audio_steg.extract_image("stego.wav", "recovered.jpg")
print(f"Extracted {result['image_size'][0]}x{result['image_size'][1]} image")
```

---

## Utility Functions

### get_audio_capacity()

```python
audio_steg.get_audio_capacity(wav_path)
```

Get information about the steganography capacity of a WAV file.

**Parameters:**

- **wav_path** (*str*): Path to the WAV file to analyze

**Returns:**

*dict* with the following keys:

- `samples` (*int*): Total number of audio samples
- `capacity_bytes` (*int*): Maximum bytes that can be hidden
- `capacity_kb` (*float*): Capacity in kilobytes
- `duration_seconds` (*float*): Audio duration in seconds
- `sample_rate` (*int*): Sample rate in Hz
- `channels` (*int*): Number of audio channels
- `sample_width` (*int*): Sample width in bytes

**Example:**

```python
info = audio_steg.get_audio_capacity("audio.wav")
print(f"Can hide up to {info['capacity_kb']:.1f} KB")
print(f"Audio is {info['duration_seconds']:.1f} seconds long")
```

---

### resize_image_for_audio()

```python
audio_steg.resize_image_for_audio(image_path, output_path, wav_path=None, max_bytes=None, verbose=True)
```

Resize an image to fit within the steganography capacity of an audio file.

**Parameters:**

- **image_path** (*str*): Path to the input image
- **output_path** (*str*): Path where resized image will be saved
- **wav_path** (*str*, optional): WAV file to check capacity against
- **max_bytes** (*int*, optional): Maximum bytes for image data
- **verbose** (*bool*, optional): If True, prints progress information. Default: True

**Note:** Either `wav_path` or `max_bytes` must be provided.

**Returns:**

*dict* with the following keys:

- `resized` (*bool*): True if image was resized, False if it already fit
- `original_size` (*tuple*): (width, height) of original image
- `final_size` (*tuple*): (width, height) of final image
- `original_bytes` (*int*): Original image data size
- `final_bytes` (*int*): Final image data size
- `reduction_percent` (*float*, optional): Percentage reduction if resized
- `output_file` (*str*): Path to output file

**Example:**

```python
result = audio_steg.resize_image_for_audio(
    "large.jpg",
    "resized.jpg",
    wav_path="audio.wav"
)

if result['resized']:
    print(f"Resized from {result['original_size']} to {result['final_size']}")
```

---

### compare_images()

```python
audio_steg.compare_images(img1_path, img2_path, verbose=True)
```

Compare two images pixel by pixel to verify they are identical.

**Parameters:**

- **img1_path** (*str*): Path to first image
- **img2_path** (*str*): Path to second image
- **verbose** (*bool*, optional): If True, prints comparison details. Default: True

**Returns:**

*dict* with the following keys:

- `identical` (*bool*): True if images are pixel-perfect identical
- `similarity` (*float*): Similarity percentage (0-100)
- `different_pixels` (*int*, optional): Number of different pixels
- `total_pixels` (*int*, optional): Total number of pixels
- `reason` (*str*, optional): Reason if not identical

**Example:**

```python
result = audio_steg.compare_images("original.jpg", "extracted.jpg")

if result['identical']:
    print("Images are identical!")
else:
    print(f"Similarity: {result['similarity']:.2f}%")
```

---

## Complete Example

```python
import audio_steg

# 1. Check audio capacity
capacity = audio_steg.get_audio_capacity("audio.wav")
print(f"Audio can hold {capacity['capacity_kb']:.1f} KB")

# 2. Resize image if needed
resize_result = audio_steg.resize_image_for_audio(
    "secret.jpg",
    "secret_resized.jpg",
    wav_path="audio.wav"
)

# 3. Hide the image
hide_result = audio_steg.hide_image(
    "audio.wav",
    "secret_resized.jpg",
    "stego.wav"
)
print(f"Hidden! Used {hide_result['capacity_usage']:.2f}% capacity")

# 4. Extract the image
extract_result = audio_steg.extract_image(
    "stego.wav",
    "recovered.jpg"
)

# 5. Verify extraction
compare_result = audio_steg.compare_images(
    "secret_resized.jpg",
    "recovered.jpg"
)

if compare_result['identical']:
    print("✅ Perfect extraction!")
```

## Error Handling

All functions raise appropriate exceptions:

```python
try:
    audio_steg.hide_image("audio.wav", "huge_image.jpg", "output.wav")
except ValueError as e:
    print(f"Image too large: {e}")
    # Solution: resize the image first
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

## Best Practices

1. **Always check capacity first** before hiding images
2. **Resize images** to fit within audio capacity
3. **Use verbose=False** for production code to suppress output
4. **Handle exceptions** appropriately
5. **Verify extraction** using `compare_images()`

## Technical Details

- **Method**: LSB (Least Significant Bit) steganography
- **Header**: 12 bytes (width, height, data size)
- **Format**: RGB images only (converted automatically)
- **Capacity**: ~1 byte per 8 audio samples
- **Audio Quality**: No perceptible degradation
