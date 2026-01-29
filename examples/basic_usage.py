"""
Example scripts demonstrating the audio_steg library usage
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_steg import hide_image, extract_image, resize_image_for_audio, get_audio_capacity


def example_basic_usage():
    """Basic example: hide and extract an image"""
    print("="*70)
    print("Example 1: Basic Usage")
    print("="*70)
    print()
    
    # Check capacity
    print("Step 1: Check audio capacity")
    capacity = get_audio_capacity("sound.wav")
    print(f"Audio can hold up to {capacity['capacity_kb']:.1f} KB of data\n")
    
    # Resize if needed
    print("Step 2: Resize image to fit")
    resize_result = resize_image_for_audio(
        "fox.jpg",
        "fox_resized.jpg",
        wav_path="sound.wav"
    )
    print()
    
    # Hide image
    print("Step 3: Hide image in audio")
    hide_result = hide_image(
        "sound.wav",
        "fox_resized.jpg",
        "stego_output.wav"
    )
    print()
    
    # Extract image
    print("Step 4: Extract image from audio")
    extract_result = extract_image(
        "stego_output.wav",
        "extracted_output.jpg"
    )
    print()
    
    print("="*70)
    print("✅ Example complete!")
    print("="*70)


def example_programmatic():
    """Example: Using the library programmatically"""
    print("\n" + "="*70)
    print("Example 2: Programmatic Usage")
    print("="*70)
    print()
    
    try:
        # Hide with verbose=False for clean output
        result = hide_image(
            "sound.wav",
            "fox_resized.jpg",
            "stego_quiet.wav",
            verbose=False
        )
        
        print(f"✅ Image hidden successfully!")
        print(f"   Image size: {result['image_size']}")
        print(f"   Data bytes: {result['data_bytes']:,}")
        print(f"   Capacity used: {result['capacity_usage']:.2f}%")
        print(f"   Output: {result['output_file']}")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    print()


def example_error_handling():
    """Example: Proper error handling"""
    print("="*70)
    print("Example 3: Error Handling")
    print("="*70)
    print()
    
    try:
        # Try to hide a large image without resizing
        hide_image(
            "sound.wav",
            "fox.jpg",  # Original large image
            "test_output.wav",
            verbose=False
        )
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")
        print("\nSolution: Resize the image first!")
    
    print()


if __name__ == "__main__":
    # Check if required files exist
    if not os.path.exists("sound.wav"):
        print("❌ Error: sound.wav not found!")
        print("Please ensure sound.wav is in the current directory")
        sys.exit(1)
    
    if not os.path.exists("fox.jpg"):
        print("❌ Error: fox.jpg not found!")
        print("Please ensure fox.jpg is in the current directory")
        sys.exit(1)
    
    # Run examples
    example_basic_usage()
    example_programmatic()
    example_error_handling()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
