#!/usr/bin/env python3
"""
Command-line interface for audio steganography library
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_steg import hide_image, extract_image, resize_image_for_audio, get_audio_capacity, compare_images


def cmd_hide(args):
    """Hide command handler"""
    try:
        result = hide_image(
            args.audio, 
            args.image, 
            args.output, 
            verbose=not args.quiet, 
            auto_resize=args.auto_resize
        )
        if not args.quiet:
            print(f"\n✅ Success! Capacity used: {result['capacity_usage']:.2f}%")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_extract(args):
    """Extract command handler"""
    try:
        result = extract_image(args.audio, args.output, verbose=not args.quiet)
        if not args.quiet:
            print(f"\n✅ Success! Extracted {result['image_size'][0]}x{result['image_size'][1]} image")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_resize(args):
    """Resize command handler"""
    try:
        result = resize_image_for_audio(
            args.image, 
            args.output, 
            wav_path=args.audio,
            max_bytes=args.max_bytes,
            verbose=not args.quiet
        )
        if not args.quiet:
            if result['resized']:
                print(f"\n✅ Resized from {result['original_size']} to {result['final_size']}")
            else:
                print(f"\n✅ Image already fits, copied to output")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_capacity(args):
    """Capacity command handler"""
    try:
        result = get_audio_capacity(args.audio)
        print(f"\n{'='*70}")
        print(f"Audio Capacity Information: {args.audio}")
        print(f"{'='*70}")
        print(f"Duration:      {result['duration_seconds']:.2f} seconds")
        print(f"Sample Rate:   {result['sample_rate']:,} Hz")
        print(f"Channels:      {result['channels']}")
        print(f"Sample Width:  {result['sample_width']} bytes")
        print(f"Total Samples: {result['samples']:,}")
        print(f"\nSteganography Capacity:")
        print(f"  {result['capacity_bytes']:,} bytes")
        print(f"  {result['capacity_kb']:.2f} KB")
        print(f"  {result['capacity_kb']/1024:.2f} MB")
        print(f"{'='*70}\n")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_compare(args):
    """Compare command handler"""
    try:
        result = compare_images(args.image1, args.image2, verbose=True)
        print()
        if result['identical']:
            print("✅ Images are identical!")
        else:
            print(f"Similarity: {result['similarity']:.2f}%")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Audio Steganography - Hide images in WAV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hide an image
  %(prog)s hide audio.wav secret.jpg output.wav
  
  # Extract an image
  %(prog)s extract stego.wav recovered.jpg
  
  # Check audio capacity
  %(prog)s capacity audio.wav
  
  # Resize image to fit
  %(prog)s resize -a audio.wav large.jpg resized.jpg
  
  # Compare images
  %(prog)s compare original.jpg extracted.jpg
        """
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # Hide command
    hide_parser = subparsers.add_parser('hide', help='Hide an image in a WAV file')
    hide_parser.add_argument('audio', help='Input WAV file')
    hide_parser.add_argument('image', help='Image to hide')
    hide_parser.add_argument('output', help='Output WAV file')
    hide_parser.add_argument('-r', '--auto-resize', action='store_true', help='Automatically resize image if too large')
    hide_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
    hide_parser.set_defaults(func=cmd_hide)
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract an image from a WAV file')
    extract_parser.add_argument('audio', help='WAV file with hidden image')
    extract_parser.add_argument('output', help='Output image file')
    extract_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
    extract_parser.set_defaults(func=cmd_extract)
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize image to fit audio capacity')
    resize_parser.add_argument('image', help='Input image')
    resize_parser.add_argument('output', help='Output resized image')
    resize_parser.add_argument('-a', '--audio', help='WAV file to check capacity')
    resize_parser.add_argument('-b', '--max-bytes', type=int, help='Maximum bytes (alternative to --audio)')
    resize_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress output')
    resize_parser.set_defaults(func=cmd_resize)
    
    # Capacity command
    capacity_parser = subparsers.add_parser('capacity', help='Check audio file capacity')
    capacity_parser.add_argument('audio', help='WAV file to analyze')
    capacity_parser.set_defaults(func=cmd_capacity)
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two images')
    compare_parser.add_argument('image1', help='First image')
    compare_parser.add_argument('image2', help='Second image')
    compare_parser.set_defaults(func=cmd_compare)
    
    args = parser.parse_args()
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130


if __name__ == '__main__':
    sys.exit(main())
