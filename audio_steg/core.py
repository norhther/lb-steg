"""
Core steganography functions for hiding and extracting images in WAV files
"""

import wave
import struct
from PIL import Image


from .utils import resize_image_obj


def hide_image(wav_path, image_path, output_path, verbose=True, auto_resize=False):
    """
    Hide an image inside a WAV file using LSB steganography
    
    Args:
        wav_path (str): Path to the input WAV file
        image_path (str): Path to the image to hide
        output_path (str): Path for the output WAV file with hidden image
        verbose (bool): Print progress information
        auto_resize (bool): Automatically resize image if it's too large
        
    Returns:
        dict: Information about the operation including capacity usage
        
    Raises:
        ValueError: If image is too large for the audio file
        FileNotFoundError: If input files don't exist
    """
    if verbose:
        print(f"[*] Opening WAV file: {wav_path}")
    
    # Open and read the WAV file
    with wave.open(wav_path, 'rb') as wav:
        # Get WAV parameters
        n_channels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        if verbose:
            print(f"[*] WAV Info: {n_channels} channels, {sampwidth} bytes/sample, {framerate} Hz, {n_frames} frames")
        
        # Read all frames
        frames = wav.readframes(n_frames)
    
    # Convert frames to list of samples
    if sampwidth == 1:
        fmt = f"{len(frames)}B"
    elif sampwidth == 2:
        fmt = f"{len(frames)//2}h"
    elif sampwidth == 4:
        fmt = f"{len(frames)//4}i"
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")
    
    samples = list(struct.unpack(fmt, frames))
    
    if verbose:
        print(f"[*] Total audio samples: {len(samples)}")
    
    # Open and process the image
    if verbose:
        print(f"[*] Opening image: {image_path}")
    
    img = Image.open(image_path)
    
    # Convert image to RGB if it's not
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    
    if verbose:
        print(f"[*] Image size: {width}x{height} pixels")
    
    # Get image bytes
    img_bytes = img.tobytes()
    img_size = len(img_bytes)
    
    if verbose:
        print(f"[*] Image data size: {img_size} bytes")
    
    # Create header: width (4 bytes) + height (4 bytes) + data_size (4 bytes) + image data
    header = struct.pack('<III', width, height, img_size)
    total_data = header + img_bytes
    total_bits = len(total_data) * 8
    
    if verbose:
        print(f"[*] Total bits to hide: {total_bits} (including header)")
    
    # Check if we have enough samples
    if total_bits > len(samples):
        if auto_resize:
            # We need to recalculate capacity and resize
            # Max bytes we can hide is (len(samples) // 8) - 12 (header)
            available_bytes = (len(samples) // 8) - 12
            img = resize_image_obj(img, available_bytes, verbose=verbose)
            
            # Recalculate data
            width, height = img.size
            img_bytes = img.tobytes()
            img_size = len(img_bytes)
            header = struct.pack('<III', width, height, img_size)
            total_data = header + img_bytes
            total_bits = len(total_data) * 8
        else:
            raise ValueError(
                f"Image too large! Need {total_bits} samples but only have {len(samples)}. "
                f"Try resizing the image manually or set auto_resize=True."
            )
    
    capacity_usage = (total_bits / len(samples)) * 100
    
    if verbose:
        print(f"[*] Capacity usage: {capacity_usage:.2f}%")
    
    # Hide data in LSB of samples
    if verbose:
        print("[*] Embedding image data into audio samples...")
    
    bit_index = 0
    for byte in total_data:
        for bit_position in range(8):
            # Extract bit from byte
            bit = (byte >> bit_position) & 1
            
            # Modify LSB of sample
            if bit == 1:
                samples[bit_index] = samples[bit_index] | 1
            else:
                samples[bit_index] = samples[bit_index] & ~1
            
            bit_index += 1
    
    # Convert samples back to bytes
    modified_frames = struct.pack(fmt, *samples)
    
    # Write output WAV file
    if verbose:
        print(f"[*] Writing output file: {output_path}")
    
    with wave.open(output_path, 'wb') as output_wav:
        output_wav.setnchannels(n_channels)
        output_wav.setsampwidth(sampwidth)
        output_wav.setframerate(framerate)
        output_wav.writeframes(modified_frames)
    
    if verbose:
        print("[+] Image successfully hidden in WAV file!")
        print(f"[+] Output saved to: {output_path}")
    
    return {
        "success": True,
        "image_size": (width, height),
        "data_bytes": img_size,
        "capacity_usage": capacity_usage,
        "output_file": output_path
    }


def extract_image(wav_path, output_image_path, verbose=True):
    """
    Extract a hidden image from a WAV file using LSB steganography
    
    Args:
        wav_path (str): Path to the WAV file containing hidden image
        output_image_path (str): Path where the extracted image will be saved
        verbose (bool): Print progress information
        
    Returns:
        dict: Information about the extracted image
        
    Raises:
        ValueError: If no valid image data is found
        FileNotFoundError: If WAV file doesn't exist
    """
    if verbose:
        print(f"[*] Opening WAV file: {wav_path}")
    
    # Open and read the WAV file
    with wave.open(wav_path, 'rb') as wav:
        # Get WAV parameters
        n_channels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        
        if verbose:
            print(f"[*] WAV Info: {n_channels} channels, {sampwidth} bytes/sample, {framerate} Hz, {n_frames} frames")
        
        # Read all frames
        frames = wav.readframes(n_frames)
    
    # Convert frames to list of samples
    if sampwidth == 1:
        fmt = f"{len(frames)}B"
    elif sampwidth == 2:
        fmt = f"{len(frames)//2}h"
    elif sampwidth == 4:
        fmt = f"{len(frames)//4}i"
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")
    
    samples = list(struct.unpack(fmt, frames))
    
    if verbose:
        print(f"[*] Total audio samples: {len(samples)}")
    
    # Extract header (12 bytes = 96 bits)
    if verbose:
        print("[*] Extracting header information...")
    
    header_bits = []
    for i in range(96):  # 12 bytes * 8 bits
        bit = samples[i] & 1
        header_bits.append(bit)
    
    # Convert bits to bytes
    header_bytes = bytearray()
    for i in range(0, 96, 8):
        byte = 0
        for j in range(8):
            byte |= (header_bits[i + j] << j)
        header_bytes.append(byte)
    
    # Unpack header
    width, height, img_size = struct.unpack('<III', bytes(header_bytes))
    
    if verbose:
        print(f"[*] Extracted image dimensions: {width}x{height}")
        print(f"[*] Extracted image data size: {img_size} bytes")
    
    # Validate extracted values
    if width <= 0 or height <= 0 or img_size <= 0:
        raise ValueError("Invalid header data - no image found or corrupted data")
    
    if width > 10000 or height > 10000:
        raise ValueError("Unrealistic image dimensions - possibly corrupted data")
    
    expected_size = width * height * 3  # RGB
    if img_size != expected_size:
        if verbose:
            print(f"[!] Warning: Image size mismatch. Expected {expected_size}, got {img_size}")
    
    # Extract image data
    if verbose:
        print("[*] Extracting image data from audio samples...")
    
    total_bits = img_size * 8
    bit_offset = 96  # Skip header
    
    if bit_offset + total_bits > len(samples):
        raise ValueError(f"Not enough samples to extract image. Need {bit_offset + total_bits}, have {len(samples)}")
    
    img_bits = []
    for i in range(bit_offset, bit_offset + total_bits):
        bit = samples[i] & 1
        img_bits.append(bit)
    
    # Convert bits to bytes
    img_bytes = bytearray()
    for i in range(0, len(img_bits), 8):
        byte = 0
        for j in range(8):
            if i + j < len(img_bits):
                byte |= (img_bits[i + j] << j)
        img_bytes.append(byte)
    
    # Create image from bytes
    if verbose:
        print("[*] Reconstructing image...")
    
    img = Image.frombytes('RGB', (width, height), bytes(img_bytes[:img_size]))
    
    # Save image
    if verbose:
        print(f"[*] Saving extracted image to: {output_image_path}")
    
    img.save(output_image_path)
    
    if verbose:
        print("[+] Image successfully extracted!")
        print(f"[+] Saved to: {output_image_path}")
        print(f"[+] Image size: {width}x{height} pixels")
    
    return {
        "success": True,
        "image_size": (width, height),
        "data_bytes": img_size,
        "output_file": output_image_path
    }
