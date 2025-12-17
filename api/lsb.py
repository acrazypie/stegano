import hashlib
import os

from PIL import Image

from .encryption import decrypt_data, encrypt_data
from .scrambler import PixelScrambler

SIGNATURE = b"LS"
FILENAME_FIELD_LENGTH = 256
SHA1_LENGTH = 20
HEADER_LENGTH = 2 + 8 + FILENAME_FIELD_LENGTH + SHA1_LENGTH


# ----------------- helpers -----------------


def _bytes_to_bits(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def _bits_to_bytes(bits):
    out = bytearray()
    acc = 0
    count = 0

    for bit in bits:
        acc = (acc << 1) | bit
        count += 1
        if count == 8:
            out.append(acc)
            acc = 0
            count = 0

    return bytes(out)


def _create_header(
    file_bytes: bytes, filename: str, original_sha1: bytes | None = None
) -> bytes:
    """
    Create header for steganography payload.

    Args:
        file_bytes: The data to be embedded (may be encrypted)
        filename: Original filename
        original_sha1: SHA1 of original unencrypted data. If None, calculates from file_bytes.

    Returns:
        Header bytes with signature, size, filename, and SHA1 checksum
    """
    name_bytes = filename.encode("utf-8")
    if len(name_bytes) > FILENAME_FIELD_LENGTH:
        raise ValueError("Nome file troppo lungo")

    # Use provided SHA1 (of original data) or calculate from current data
    sha1 = (
        original_sha1
        if original_sha1 is not None
        else hashlib.sha1(file_bytes).digest()
    )

    header = bytearray(HEADER_LENGTH)
    header[0:2] = SIGNATURE
    header[2:10] = len(file_bytes).to_bytes(8, "little")
    header[10 : 10 + len(name_bytes)] = name_bytes
    header[10 + FILENAME_FIELD_LENGTH : 10 + FILENAME_FIELD_LENGTH + SHA1_LENGTH] = sha1

    return bytes(header)


# ----------------- public API -----------------


def encode_file_into_image(
    input_file: str,
    cover_image: str,
    output_image: str,
    password: str | None = None,
    scramble_seed: int | str | None = None,
):
    """
    Encode a file into an image using LSB steganography with optional pixel scrambling.

    Args:
        input_file: Path to file to hide
        cover_image: Path to cover image
        output_image: Path to output image
        password: Optional password for encryption
        scramble_seed: Optional seed for pixel scrambling. Can be:
                      - None: No scrambling (sequential embedding)
                      - int: Use as direct seed
                      - str: Generate seed from password or string
                      - "password": Use password as seed source if password provided
                      - "image": Generate seed from image data
    """
    with open(input_file, "rb") as f:
        file_bytes = f.read()

    # Store SHA1 of original data for integrity checking
    original_sha1 = hashlib.sha1(file_bytes).digest()

    # Encrypt if password is provided
    if password:
        file_bytes = encrypt_data(file_bytes, password)

    # Create header with SHA1 of original data and size of (potentially encrypted) data
    header = _create_header(file_bytes, os.path.basename(input_file), original_sha1)

    payload = header + file_bytes
    bits = list(_bytes_to_bits(payload))

    img = Image.open(cover_image).convert("RGB")
    pixels = img.load()
    width, height = img.size

    capacity = width * height * 3
    if len(bits) > capacity:
        raise ValueError("Immagine troppo piccola per contenere i dati")

    # Generate scrambler with appropriate seed
    seed = _resolve_scramble_seed(scramble_seed, password, cover_image)
    scrambler = PixelScrambler(width, height, seed)

    if seed is not None:
        # Use scrambled pixel order
        bit_positions = scrambler.get_bit_positions()
        bit_index = 0

        for bit_idx, bit_value in enumerate(bits):
            if bit_idx >= len(bit_positions):
                break

            x, y, channel = bit_positions[bit_idx]
            r, g, b = pixels[x, y]
            rgb = [r, g, b]

            # Set the LSB of the specified channel
            rgb[channel] = (rgb[channel] & 0b11111110) | bit_value

            pixels[x, y] = tuple(rgb)
    else:
        # Original sequential embedding (no scrambling)
        bit_index = 0

        for y in range(height):
            for x in range(width):
                if bit_index >= len(bits):
                    break

                r, g, b = pixels[x, y]
                rgb = [r, g, b]

                for i in range(3):
                    if bit_index < len(bits):
                        rgb[i] = (rgb[i] & 0b11111110) | bits[bit_index]
                        bit_index += 1

                pixels[x, y] = tuple(rgb)

            if bit_index >= len(bits):
                break

    img.save(output_image, "PNG")


def decode_image_to_file(
    input_image: str,
    output_path_or_dir: str,
    password: str | None = None,
    scramble_seed: int | str | None = None,
) -> str:
    """
    Decode a file from an image using LSB steganography with optional pixel unscrambling.

    Args:
        input_image: Path to image containing hidden data
        output_path_or_dir: Output path or directory for extracted file
        password: Optional password for decryption
        scramble_seed: Optional seed for pixel unscrambling. Must match the seed used in encoding.
                      Can be:
                      - None: No unscrambling (sequential extraction)
                      - int: Use as direct seed
                      - str: Generate seed from password or string
                      - "password": Use password as seed source if password provided
                      - "image": Generate seed from image data

    Returns:
        Path to extracted file
    """
    img = Image.open(input_image).convert("RGB")
    pixels = img.load()
    width, height = img.size

    # Generate scrambler with appropriate seed
    seed = _resolve_scramble_seed(scramble_seed, password, input_image)
    scrambler = PixelScrambler(width, height, seed)

    if seed is not None:
        # Use scrambled pixel order to extract
        bit_positions = scrambler.get_bit_positions()
        bits = []

        for x, y, channel in bit_positions:
            rgb = pixels[x, y]
            bits.append(rgb[channel] & 1)
    else:
        # Original sequential extraction (no scrambling)
        bits = []

        for y in range(height):
            for x in range(width):
                for channel in pixels[x, y]:
                    bits.append(channel & 1)

    raw = _bits_to_bytes(bits)

    if raw[0:2] != SIGNATURE:
        raise ValueError("Firma non valida")

    filesize = int.from_bytes(raw[2:10], "little")
    filename = raw[10 : 10 + FILENAME_FIELD_LENGTH].decode("utf-8").rstrip("\x00")

    sha1_stored = raw[
        10 + FILENAME_FIELD_LENGTH : 10 + FILENAME_FIELD_LENGTH + SHA1_LENGTH
    ]

    data_offset = HEADER_LENGTH
    file_data = raw[data_offset : data_offset + filesize]

    if password:
        try:
            file_data = decrypt_data(file_data, password)
        except ValueError as e:
            raise ValueError(f"Decryption failed: {e}")

    if hashlib.sha1(file_data).digest() != sha1_stored:
        raise ValueError("Checksum SHA1 non valido")

    if output_path_or_dir.endswith(os.sep) or os.path.isdir(output_path_or_dir):
        output_path = os.path.join(output_path_or_dir, filename)
    else:
        output_path = output_path_or_dir

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(file_data)

    return output_path


def _resolve_scramble_seed(
    scramble_seed: int | str | None, password: str | None, image_path: str
) -> int | None:
    """
    Resolve the actual seed value from various seed specification formats.

    Args:
        scramble_seed: User-provided seed specification
        password: Optional password
        image_path: Path to image file

    Returns:
        Resolved integer seed, or None if no scrambling should be applied
    """
    if scramble_seed is None:
        return None

    if isinstance(scramble_seed, int):
        return scramble_seed

    if isinstance(scramble_seed, str):
        if scramble_seed.lower() == "password":
            if password:
                return PixelScrambler.generate_seed_from_password(password)
            else:
                raise ValueError("'password' seed specified but no password provided")
        elif scramble_seed.lower() == "image":
            with open(image_path, "rb") as f:
                image_data = f.read()
            return PixelScrambler.generate_seed_from_image(image_data)
        else:
            # Treat as direct string seed
            return PixelScrambler.generate_seed_from_password(scramble_seed)

    raise ValueError(f"Invalid scramble_seed type: {type(scramble_seed)}")
