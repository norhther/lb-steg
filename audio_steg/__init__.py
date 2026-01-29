"""
Audio Steganography Library
Hide and extract images in WAV audio files using LSB technique
"""

from .core import hide_image, extract_image
from .utils import resize_image_for_audio, get_audio_capacity, compare_images

__version__ = "1.0.0"
__author__ = "Audio Steganography"
__all__ = [
    "hide_image",
    "extract_image",
    "resize_image_for_audio",
    "get_audio_capacity",
    "compare_images"
]
