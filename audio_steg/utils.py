"""
Utility functions for audio steganography
"""

import wave
import struct
import math
from PIL import Image
import os


def get_audio_capacity(wav_path):
    """
    Get the data capacity of a WAV file in bytes
    
    Args:
        wav_path (str): Path to the WAV file
        
    Returns:
        dict: Information about audio capacity including samples and bytes
    """
    with wave.open(wav_path, 'rb') as wav:
        n_frames = wav.getnframes()
        sampwidth = wav.getsampwidth()
        n_channels = wav.getnchannels()
        framerate = wav.getframerate()
        
        samples = n_frames * n_channels
        
        # Each sample can hold 1 bit, so capacity in bytes is samples / 8
        # Subtract 12 bytes for header (width, height, size)
        capacity_bytes = (samples // 8) - 12
        
        return {
            "samples": samples,
            "capacity_bytes": capacity_bytes,
            "capacity_kb": capacity_bytes / 1024,
            "duration_seconds": n_frames / framerate,
            "sample_rate": framerate,
            "channels": n_channels,
            "sample_width": sampwidth
        }


def resize_image_for_audio(image_path, output_path, wav_path=None, max_bytes=None, verbose=True):
    """
    Resize an image to fit within audio capacity
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path for the resized image
        wav_path (str, optional): Path to WAV file to check capacity
        max_bytes (int, optional): Maximum bytes for image data
        verbose (bool): Print progress information
        
    Returns:
        dict: Information about the resized image
        
    Note:
        Either wav_path or max_bytes must be provided
    """
    if wav_path is None and max_bytes is None:
        raise ValueError("Either wav_path or max_bytes must be provided")
    
    # Get capacity from WAV file if provided
    if wav_path is not None:
        capacity_info = get_audio_capacity(wav_path)
        max_bytes = capacity_info["capacity_bytes"]
        
        if verbose:
            print(f"[*] WAV file capacity: {max_bytes:,} bytes ({max_bytes/1024:.1f} KB)")
    
    if verbose:
        print(f"[*] Opening image: {image_path}")
    
    img = Image.open(image_path)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    orig_width, orig_height = img.size
    orig_size = orig_width * orig_height * 3
    
    if verbose:
        print(f"[*] Original size: {orig_width}x{orig_height} pixels")
        print(f"[*] Original data size: {orig_size:,} bytes ({orig_size/1024:.1f} KB)")
    
    # Check if resizing is needed
    if orig_size <= max_bytes:
        if verbose:
            print(f"[*] Image already fits! Copying to {output_path}")
        img.save(output_path)
        return {
            "resized": False,
            "original_size": (orig_width, orig_height),
            "final_size": (orig_width, orig_height),
            "original_bytes": orig_size,
            "final_bytes": orig_size,
            "output_file": output_path
        }
    
    # Calculate maximum dimensions
    max_pixels = max_bytes // 3
    
    # Maintain aspect ratio
    aspect_ratio = orig_width / orig_height
    
    # Calculate new dimensions
    new_height = int(math.sqrt(max_pixels / aspect_ratio))
    new_width = int(new_height * aspect_ratio)
    
    # Make sure we're under the limit
    while (new_width * new_height * 3) > max_bytes:
        new_width -= 1
        new_height = int(new_width / aspect_ratio)
    
    new_size = new_width * new_height * 3
    
    if verbose:
        print(f"[*] Resizing to: {new_width}x{new_height} pixels")
        print(f"[*] New data size: {new_size:,} bytes ({new_size/1024:.1f} KB)")
        print(f"[*] Size reduction: {((orig_size - new_size) / orig_size * 100):.1f}%")
    
    # Resize image
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    resized_img.save(output_path)
    
    if verbose:
        print(f"[+] Resized image saved to: {output_path}")
    
    return {
        "resized": True,
        "original_size": (orig_width, orig_height),
        "final_size": (new_width, new_height),
        "original_bytes": orig_size,
        "final_bytes": new_size,
        "reduction_percent": ((orig_size - new_size) / orig_size * 100),
        "output_file": output_path
    }


def resize_image_obj(img, max_bytes, verbose=True):
    """
    Resize a PIL Image object to fit within byte capacity
    
    Args:
        img (PIL.Image): Input Image object
        max_bytes (int): Maximum bytes for image data
        verbose (bool): Print progress information
        
    Returns:
        PIL.Image: Resized Image object
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    orig_width, orig_height = img.size
    orig_size = orig_width * orig_height * 3
    
    if orig_size <= max_bytes:
        return img
    
    if verbose:
        print(f"[*] Image too large ({orig_size:,} bytes). Auto-resizing to fit {max_bytes:,} bytes...")
    
    # Calculate maximum dimensions
    max_pixels = max_bytes // 3
    
    # Maintain aspect ratio
    aspect_ratio = orig_width / orig_height
    
    # Calculate new dimensions
    new_height = int(math.sqrt(max_pixels / aspect_ratio))
    new_width = int(new_height * aspect_ratio)
    
    # Make sure we're under the limit
    while (new_width * new_height * 3) > max_bytes:
        new_width -= 1
        new_height = int(new_width / aspect_ratio)
    
    if verbose:
        print(f"[*] Resized to: {new_width}x{new_height} pixels")
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def compare_images(img1_path, img2_path, verbose=True):
    """
    Compare two images pixel by pixel
    
    Args:
        img1_path (str): Path to first image
        img2_path (str): Path to second image
        verbose (bool): Print comparison details
        
    Returns:
        dict: Comparison results including similarity percentage
    """
    if not os.path.exists(img1_path):
        raise FileNotFoundError(f"Image not found: {img1_path}")
    
    if not os.path.exists(img2_path):
        raise FileNotFoundError(f"Image not found: {img2_path}")
    
    # Open images
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    
    # Get file sizes
    size1 = os.path.getsize(img1_path)
    size2 = os.path.getsize(img2_path)
    
    if verbose:
        print(f"[*] Image 1: {img1.size[0]}x{img1.size[1]} pixels, {img1.mode}, {size1:,} bytes")
        print(f"[*] Image 2: {img2.size[0]}x{img2.size[1]} pixels, {img2.mode}, {size2:,} bytes")
    
    # Compare dimensions
    if img1.size != img2.size:
        if verbose:
            print("❌ Images have different dimensions!")
        return {
            "identical": False,
            "similarity": 0.0,
            "reason": "Different dimensions"
        }
    
    # Convert to RGB if needed
    if img1.mode != 'RGB':
        img1 = img1.convert('RGB')
    if img2.mode != 'RGB':
        img2 = img2.convert('RGB')
    
    # Compare pixel by pixel
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())
    
    if pixels1 == pixels2:
        if verbose:
            print("✅ Images are pixel-perfect identical!")
        return {
            "identical": True,
            "similarity": 100.0,
            "different_pixels": 0,
            "total_pixels": len(pixels1)
        }
    else:
        # Count differences
        differences = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 != p2)
        total_pixels = len(pixels1)
        similarity = ((total_pixels - differences) / total_pixels) * 100
        
        if verbose:
            print(f"⚠️  Images are {similarity:.2f}% similar")
            print(f"   Different pixels: {differences:,} out of {total_pixels:,}")
        
        return {
            "identical": False,
            "similarity": similarity,
            "different_pixels": differences,
            "total_pixels": total_pixels
        }
