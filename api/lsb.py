import hashlib
import os

from PIL import Image
from .encryption import encrypt_data, decrypt_data

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


def _create_header(file_bytes: bytes, filename: str) -> bytes:
    name_bytes = filename.encode("utf-8")
    if len(name_bytes) > FILENAME_FIELD_LENGTH:
        raise ValueError("Nome file troppo lungo")

    sha1 = hashlib.sha1(file_bytes).digest()

    header = bytearray(HEADER_LENGTH)
    header[0:2] = SIGNATURE
    header[2:10] = len(file_bytes).to_bytes(8, "little")
    header[10 : 10 + len(name_bytes)] = name_bytes
    header[10 + FILENAME_FIELD_LENGTH : 10 + FILENAME_FIELD_LENGTH + SHA1_LENGTH] = sha1

    return bytes(header)


# ----------------- public API -----------------


def encode_file_into_image(input_file: str, cover_image: str, output_image: str, password: str | None = None):
    with open(input_file, "rb") as f:
        file_bytes = f.read()

    if password:
        file_bytes = encrypt_data(file_bytes, password)

    header = _create_header(file_bytes, os.path.basename(input_file))
    payload = header + file_bytes
    bits = list(_bytes_to_bits(payload))

    img = Image.open(cover_image).convert("RGB")
    pixels = img.load()
    width, height = img.size

    capacity = width * height * 3
    if len(bits) > capacity:
        raise ValueError("Immagine troppo piccola per contenere i dati")

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


def decode_image_to_file(input_image: str, output_path_or_dir: str, password: str | None = None) -> str:
    img = Image.open(input_image).convert("RGB")
    pixels = img.load()
    width, height = img.size

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
