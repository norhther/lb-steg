"""
Basic tests for audio_steg library
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_steg import hide_image, extract_image, get_audio_capacity, resize_image_for_audio, compare_images


class TestAudioSteg(unittest.TestCase):
    """Test cases for audio steganography library"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_audio = "sound.wav"
        self.test_image = "fox.jpg"
        self.test_resized = "test_resized.png"
        self.test_output = "test_output.wav"
        self.test_extracted = "test_extracted.png"
    
    def tearDown(self):
        """Clean up test files"""
        for f in [self.test_resized, self.test_output, self.test_extracted]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
    
    def test_get_capacity(self):
        """Test audio capacity checking"""
        if not os.path.exists(self.test_audio):
            self.skipTest("sound.wav not found")
        
        result = get_audio_capacity(self.test_audio)
        
        self.assertIn('samples', result)
        self.assertIn('capacity_bytes', result)
        self.assertIn('capacity_kb', result)
        self.assertGreater(result['samples'], 0)
        self.assertGreater(result['capacity_bytes'], 0)
    
    def test_resize_image(self):
        """Test image resizing"""
        if not os.path.exists(self.test_audio) or not os.path.exists(self.test_image):
            self.skipTest("Test files not found")
        
        result = resize_image_for_audio(
            self.test_image,
            self.test_resized,
            wav_path=self.test_audio,
            verbose=False
        )
        
        self.assertTrue(os.path.exists(self.test_resized))
        self.assertIn('final_size', result)
        self.assertIn('final_bytes', result)
    
    def test_hide_and_extract(self):
        """Test hiding and extracting an image"""
        if not os.path.exists(self.test_audio) or not os.path.exists(self.test_image):
            self.skipTest("Test files not found")
        
        # First resize the image
        resize_result = resize_image_for_audio(
            self.test_image,
            self.test_resized,
            wav_path=self.test_audio,
            verbose=False
        )
        
        # Hide the image
        hide_result = hide_image(
            self.test_audio,
            self.test_resized,
            self.test_output,
            verbose=False
        )
        
        self.assertTrue(os.path.exists(self.test_output))
        self.assertIn('success', hide_result)
        self.assertTrue(hide_result['success'])
        
        # Extract the image
        extract_result = extract_image(
            self.test_output,
            self.test_extracted,
            verbose=False
        )
        
        self.assertTrue(os.path.exists(self.test_extracted))
        self.assertIn('success', extract_result)
        self.assertTrue(extract_result['success'])
        
        # Compare images
        compare_result = compare_images(
            self.test_resized,
            self.test_extracted,
            verbose=False
        )
        
        self.assertTrue(compare_result['identical'])
        self.assertEqual(compare_result['similarity'], 100.0)
    
    def test_image_too_large(self):
        """Test error handling for oversized images"""
        if not os.path.exists(self.test_audio) or not os.path.exists(self.test_image):
            self.skipTest("Test files not found")
        
        # Try to hide original large image without resizing
        with self.assertRaises(ValueError):
            hide_image(
                self.test_audio,
                self.test_image,
                self.test_output,
                verbose=False
            )


def run_tests():
    """Run all tests"""
    print("="*70)
    print("Running Audio Steganography Tests")
    print("="*70)
    print()
    
    # Check for required files
    if not os.path.exists("sound.wav"):
        print("⚠️  Warning: sound.wav not found - some tests will be skipped")
    
    if not os.path.exists("fox.jpg"):
        print("⚠️  Warning: fox.jpg not found - some tests will be skipped")
    
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAudioSteg)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*70)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
