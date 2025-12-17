import random
from typing import List, Tuple


class PixelScrambler:
    """
    Implements pseudo-random pixel scrambling for enhanced LSB steganography security.

    Instead of embedding data sequentially in pixels, this scrambler generates a
    pseudo-random order of pixel positions based on a configurable seed. This makes
    the steganography more resistant to analysis and detection.
    """

    def __init__(self, width: int, height: int, seed: int | None = None):
        """
        Initialize the pixel scrambler.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            seed: Optional seed for reproducible randomization. If None, uses random seed.
                  The seed should be derivable from the image or password for reproducibility.
        """
        self.width = width
        self.height = height
        self.seed = seed
        self._pixel_order = None
        self._bit_positions = None

    def _generate_pixel_order(self) -> List[Tuple[int, int]]:
        """
        Generate a pseudo-random order of pixel coordinates.

        Returns:
            List of (x, y) tuples in randomized order
        """
        if self.seed is not None:
            random.seed(self.seed)

        pixels = [(x, y) for y in range(self.height) for x in range(self.width)]
        random.shuffle(pixels)
        return pixels

    def _generate_bit_positions(self) -> List[Tuple[int, int, int]]:
        """
        Generate a pseudo-random order of bit positions (x, y, channel).

        Each pixel has 3 channels (R, G, B), so this generates positions for all
        available bit positions in the image.

        Returns:
            List of (x, y, channel) tuples in randomized order
        """
        if self.seed is not None:
            random.seed(self.seed)

        positions = []
        for y in range(self.height):
            for x in range(self.width):
                for channel in range(3):  # R, G, B
                    positions.append((x, y, channel))

        random.shuffle(positions)
        return positions

    def get_pixel_order(self) -> List[Tuple[int, int]]:
        """
        Get the pseudo-random pixel order (cached after first call).

        Returns:
            List of (x, y) tuples in randomized order
        """
        if self._pixel_order is None:
            self._pixel_order = self._generate_pixel_order()
        return self._pixel_order

    def get_bit_positions(self) -> List[Tuple[int, int, int]]:
        """
        Get the pseudo-random bit positions (cached after first call).

        Returns:
            List of (x, y, channel) tuples in randomized order
        """
        if self._bit_positions is None:
            self._bit_positions = self._generate_bit_positions()
        return self._bit_positions

    def get_total_capacity(self) -> int:
        """
        Get the total number of bits that can be embedded (width * height * 3).

        Returns:
            Total bit capacity
        """
        return self.width * self.height * 3

    @staticmethod
    def generate_seed_from_password(password: str) -> int:
        """
        Generate a deterministic seed from a password string.

        Args:
            password: Password string

        Returns:
            Integer seed value
        """
        import hashlib

        hash_digest = hashlib.sha256(password.encode()).digest()
        # Convert first 8 bytes to integer
        seed = int.from_bytes(hash_digest[:8], byteorder="little")
        return seed & 0x7FFFFFFF  # Ensure positive integer

    @staticmethod
    def generate_seed_from_image(image_bytes: bytes) -> int:
        """
        Generate a deterministic seed from image data.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Integer seed value
        """
        import hashlib

        hash_digest = hashlib.sha256(image_bytes).digest()
        # Convert first 8 bytes to integer
        seed = int.from_bytes(hash_digest[:8], byteorder="little")
        return seed & 0x7FFFFFFF  # Ensure positive integer

    @staticmethod
    def generate_seed_from_combined(password: str | None, image_bytes: bytes) -> int:
        """
        Generate a deterministic seed from both password and image data.

        This provides the strongest scrambling seed as it depends on both the
        image and potentially a password.

        Args:
            password: Optional password string
            image_bytes: Raw image bytes

        Returns:
            Integer seed value
        """
        import hashlib

        combined = image_bytes
        if password:
            combined = password.encode() + image_bytes

        hash_digest = hashlib.sha256(combined).digest()
        seed = int.from_bytes(hash_digest[:8], byteorder="little")
        return seed & 0x7FFFFFFF  # Ensure positive integer
