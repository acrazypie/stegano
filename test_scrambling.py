import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from api.lsb import decode_image_to_file, encode_file_into_image
from api.scrambler import PixelScrambler


class TestPixelScrambler(unittest.TestCase):
    """Test suite for PixelScrambler class."""

    def test_scrambler_initialization(self):
        """Test basic scrambler initialization."""
        scrambler = PixelScrambler(width=100, height=100, seed=12345)
        self.assertEqual(scrambler.width, 100)
        self.assertEqual(scrambler.height, 100)
        self.assertEqual(scrambler.seed, 12345)

    def test_scrambler_with_none_seed(self):
        """Test scrambler with None seed (no scrambling)."""
        scrambler = PixelScrambler(width=100, height=100, seed=None)
        self.assertIsNone(scrambler.seed)

    def test_bit_positions_generation(self):
        """Test bit positions are generated correctly."""
        scrambler = PixelScrambler(width=10, height=10, seed=42)
        positions = scrambler.get_bit_positions()

        # Should have width * height * 3 positions (RGB channels)
        self.assertEqual(len(positions), 10 * 10 * 3)

        # All positions should be valid
        for x, y, channel in positions:
            self.assertGreaterEqual(x, 0)
            self.assertLess(x, 10)
            self.assertGreaterEqual(y, 0)
            self.assertLess(y, 10)
            self.assertIn(channel, [0, 1, 2])

    def test_bit_positions_deterministic(self):
        """Test that same seed produces same bit positions."""
        scrambler1 = PixelScrambler(width=50, height=50, seed=999)
        scrambler2 = PixelScrambler(width=50, height=50, seed=999)

        positions1 = scrambler1.get_bit_positions()
        positions2 = scrambler2.get_bit_positions()

        self.assertEqual(positions1, positions2)

    def test_bit_positions_different_seeds(self):
        """Test that different seeds produce different bit positions."""
        scrambler1 = PixelScrambler(width=50, height=50, seed=111)
        scrambler2 = PixelScrambler(width=50, height=50, seed=222)

        positions1 = scrambler1.get_bit_positions()
        positions2 = scrambler2.get_bit_positions()

        self.assertNotEqual(positions1, positions2)

    def test_pixel_order_generation(self):
        """Test pixel order generation."""
        scrambler = PixelScrambler(width=20, height=20, seed=555)
        pixel_order = scrambler.get_pixel_order()

        # Should have width * height pixels
        self.assertEqual(len(pixel_order), 20 * 20)

        # All pixels should be unique
        self.assertEqual(len(set(pixel_order)), 20 * 20)

    def test_total_capacity(self):
        """Test total capacity calculation."""
        scrambler = PixelScrambler(width=100, height=100, seed=42)
        capacity = scrambler.get_total_capacity()

        # 100 * 100 * 3 channels
        self.assertEqual(capacity, 30000)

    def test_generate_seed_from_password(self):
        """Test seed generation from password."""
        seed1 = PixelScrambler.generate_seed_from_password("mypassword")
        seed2 = PixelScrambler.generate_seed_from_password("mypassword")
        seed3 = PixelScrambler.generate_seed_from_password("different")

        # Same password should generate same seed
        self.assertEqual(seed1, seed2)

        # Different passwords should generate different seeds
        self.assertNotEqual(seed1, seed3)

        # Seeds should be positive integers
        self.assertIsInstance(seed1, int)
        self.assertGreater(seed1, 0)

    def test_generate_seed_from_image(self):
        """Test seed generation from image bytes."""
        image_bytes1 = b"some image data"
        image_bytes2 = b"some image data"
        image_bytes3 = b"different data"

        seed1 = PixelScrambler.generate_seed_from_image(image_bytes1)
        seed2 = PixelScrambler.generate_seed_from_image(image_bytes2)
        seed3 = PixelScrambler.generate_seed_from_image(image_bytes3)

        # Same image data should generate same seed
        self.assertEqual(seed1, seed2)

        # Different image data should generate different seeds
        self.assertNotEqual(seed1, seed3)

        # Seeds should be positive integers
        self.assertIsInstance(seed1, int)
        self.assertGreater(seed1, 0)

    def test_generate_seed_from_combined(self):
        """Test seed generation from combined password and image."""
        password = "mypassword"
        image_bytes = b"image data"

        seed1 = PixelScrambler.generate_seed_from_combined(password, image_bytes)
        seed2 = PixelScrambler.generate_seed_from_combined(password, image_bytes)
        seed3 = PixelScrambler.generate_seed_from_combined("different", image_bytes)
        seed4 = PixelScrambler.generate_seed_from_combined(password, b"different")
        seed5 = PixelScrambler.generate_seed_from_combined(None, image_bytes)

        # Same inputs should generate same seed
        self.assertEqual(seed1, seed2)

        # Different password should generate different seed
        self.assertNotEqual(seed1, seed3)

        # Different image should generate different seed
        self.assertNotEqual(seed1, seed4)

        # None password should generate different seed than with password
        self.assertNotEqual(seed1, seed5)


class TestScramblingIntegration(unittest.TestCase):
    """Integration tests for scrambling with LSB steganography."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.cover_image_path = os.path.join(self.test_dir, "cover.png")
        self.output_image_path = os.path.join(self.test_dir, "output.png")
        self.extracted_file_path = os.path.join(self.test_dir, "extracted.txt")

        # Create a test cover image (1000x1000 pixels)
        self.create_test_image(self.cover_image_path, width=1000, height=1000)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_image(self, path, width=1000, height=1000):
        """Create a test PNG image."""
        img = Image.new("RGB", (width, height), color=(100, 150, 200))
        img.save(path, "PNG")

    def create_test_file(self, path, content=b"Hello, World!"):
        """Create a test file with given content."""
        with open(path, "wb") as f:
            f.write(content)

    def test_encode_decode_no_scrambling(self):
        """Test encode and decode without scrambling (baseline)."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"This is a secret message"
        self.create_test_file(input_file, test_content)

        # Encode without scrambling
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=None,
            scramble_seed=None,
        )

        self.assertTrue(os.path.exists(self.output_image_path))

        # Decode without scrambling
        output_path = decode_image_to_file(
            self.output_image_path,
            self.test_dir,
            password=None,
            scramble_seed=None,
        )

        # Verify content
        with open(output_path, "rb") as f:
            decoded_content = f.read()

        self.assertEqual(decoded_content, test_content)

    def test_encode_decode_with_integer_seed(self):
        """Test encode and decode with integer seed."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"Secret with integer seed"
        self.create_test_file(input_file, test_content)

        seed = 123456

        # Encode with integer seed
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=None,
            scramble_seed=seed,
        )

        # Decode with same integer seed
        output_path = decode_image_to_file(
            self.output_image_path,
            self.test_dir,
            password=None,
            scramble_seed=seed,
        )

        # Verify content
        with open(output_path, "rb") as f:
            decoded_content = f.read()

        self.assertEqual(decoded_content, test_content)

    def test_encode_decode_with_password_seed(self):
        """Test encode and decode with password-derived seed."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"Secret with password seed"
        self.create_test_file(input_file, test_content)

        password_seed = PixelScrambler.generate_seed_from_password("mypassword")

        # Encode with password seed
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=None,
            scramble_seed=password_seed,
        )

        # Decode with same password seed
        output_path = decode_image_to_file(
            self.output_image_path,
            self.test_dir,
            password=None,
            scramble_seed=password_seed,
        )

        # Verify content
        with open(output_path, "rb") as f:
            decoded_content = f.read()

        self.assertEqual(decoded_content, test_content)

    def test_encode_decode_with_image_seed(self):
        """Test encode and decode with image-derived seed."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"Secret with image seed"
        self.create_test_file(input_file, test_content)

        with open(self.cover_image_path, "rb") as f:
            image_data = f.read()
        seed = PixelScrambler.generate_seed_from_image(image_data)

        # Encode with image seed
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=None,
            scramble_seed=seed,
        )

        # Decode with same image seed
        output_path = decode_image_to_file(
            self.output_image_path,
            self.test_dir,
            password=None,
            scramble_seed=seed,
        )

        # Verify content
        with open(output_path, "rb") as f:
            decoded_content = f.read()

        self.assertEqual(decoded_content, test_content)

    def test_encode_decode_with_encryption_and_scrambling(self):
        """Test encode and decode with both encryption and scrambling."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"Secret with encryption and scrambling"
        self.create_test_file(input_file, test_content)

        password = "myencryptionpassword"
        seed = 999888

        # Encode with both encryption and scrambling
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=password,
            scramble_seed=seed,
        )

        # Decode with both decryption and unscrambling
        output_path = decode_image_to_file(
            self.output_image_path,
            self.test_dir,
            password=password,
            scramble_seed=seed,
        )

        # Verify content
        with open(output_path, "rb") as f:
            decoded_content = f.read()

        self.assertEqual(decoded_content, test_content)

    def test_wrong_seed_fails(self):
        """Test that decoding with wrong seed fails."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"Secret with wrong seed test"
        self.create_test_file(input_file, test_content)

        # Encode with seed 111
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=None,
            scramble_seed=111,
        )

        # Try to decode with different seed (222) - should fail
        with self.assertRaises(ValueError):
            decode_image_to_file(
                self.output_image_path,
                self.test_dir,
                password=None,
                scramble_seed=222,
            )

    def test_large_file_with_scrambling(self):
        """Test encoding and decoding a larger file with scrambling."""
        input_file = os.path.join(self.test_dir, "large_input.bin")

        # Create a 10KB test file
        test_content = os.urandom(10240)
        self.create_test_file(input_file, test_content)

        seed = 777666

        # Encode
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            self.output_image_path,
            password=None,
            scramble_seed=seed,
        )

        # Decode
        output_path = decode_image_to_file(
            self.output_image_path,
            self.test_dir,
            password=None,
            scramble_seed=seed,
        )

        # Verify content
        with open(output_path, "rb") as f:
            decoded_content = f.read()

        self.assertEqual(decoded_content, test_content)

    def test_scrambling_vs_no_scrambling_produces_different_images(self):
        """Test that scrambling produces different output images."""
        input_file = os.path.join(self.test_dir, "input.txt")
        test_content = b"Test content for image comparison"
        self.create_test_file(input_file, test_content)

        output_no_scramble = os.path.join(self.test_dir, "output_no_scramble.png")
        output_scramble = os.path.join(self.test_dir, "output_scramble.png")

        # Encode without scrambling
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            output_no_scramble,
            password=None,
            scramble_seed=None,
        )

        # Encode with scrambling
        encode_file_into_image(
            input_file,
            self.cover_image_path,
            output_scramble,
            password=None,
            scramble_seed=12345,
        )

        # Read both output images
        with open(output_no_scramble, "rb") as f:
            data_no_scramble = f.read()

        with open(output_scramble, "rb") as f:
            data_scramble = f.read()

        # They should be different
        self.assertNotEqual(data_no_scramble, data_scramble)


class TestScramblingEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_scrambler_with_zero_seed(self):
        """Test scrambler with zero seed."""
        scrambler = PixelScrambler(width=50, height=50, seed=0)
        positions = scrambler.get_bit_positions()

        self.assertEqual(len(positions), 50 * 50 * 3)

    def test_scrambler_with_very_large_seed(self):
        """Test scrambler with very large seed value."""
        large_seed = 2**31 - 1
        scrambler = PixelScrambler(width=50, height=50, seed=large_seed)
        positions = scrambler.get_bit_positions()

        self.assertEqual(len(positions), 50 * 50 * 3)

    def test_scrambler_with_small_image(self):
        """Test scrambler with very small image."""
        scrambler = PixelScrambler(width=1, height=1, seed=42)
        positions = scrambler.get_bit_positions()

        # 1x1 image with 3 channels
        self.assertEqual(len(positions), 3)

    def test_seed_generation_with_empty_string(self):
        """Test seed generation with empty password."""
        seed1 = PixelScrambler.generate_seed_from_password("")
        seed2 = PixelScrambler.generate_seed_from_password("")

        # Should be deterministic even for empty string
        self.assertEqual(seed1, seed2)
        self.assertIsInstance(seed1, int)
        self.assertGreater(seed1, 0)

    def test_seed_generation_with_unicode_password(self):
        """Test seed generation with unicode password."""
        unicode_password = "PasswordWithUnicode_ñ_中文"
        seed1 = PixelScrambler.generate_seed_from_password(unicode_password)
        seed2 = PixelScrambler.generate_seed_from_password(unicode_password)

        # Should work with unicode
        self.assertEqual(seed1, seed2)
        self.assertIsInstance(seed1, int)


if __name__ == "__main__":
    unittest.main()
