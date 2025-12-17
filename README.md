# Stegano - LSB Steganography Tool

<p align="center"><img width="45%" alt="stegano-chameleon" src="https://github.com/acrazypie/acrazypie/blob/main/assets/stegano.png" /></p>

<br />

A Python tool for hiding files in images using Least Significant Bit (LSB) steganography with optional pixel scrambling for enhanced security.

##### Read this in other languages:

-   [English 🇬🇧](README.md)
-   [Italiano 🇮🇹](docs/README.it.md)

### Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Requirements](#requirements)
-   [Installation](#installation)
-   [Usage](#usage)
-   [Pixel Scrambling](#pixel-scrambling)
-   [How it Works](#how-it-works)
-   [Limitations](#limitations)
-   [Security](#security)
-   [Examples](#examples)
-   [Documentation](#documentation)
-   [TODO List](#todo-list)
-   [License](#license)

---

### Overview

Stegano is a command-line tool that implements LSB steganography to hide files within PNG images. The tool provides both encoding (hiding) and decoding (extracting) functionality with data integrity verification using SHA-1 checksums. Now featuring pseudo-random pixel scrambling for significantly enhanced security against steganalysis.

### ⚠️ Legal Disclaimer

**THIS TOOL IS PROVIDED FOR EDUCATIONAL AND LAWFUL PURPOSES ONLY.** Users are solely responsible for ensuring that their use of this software complies with all applicable local, state, national, and international laws and regulations. 

**Do not use this tool or code for:**
- Illegal surveillance or espionage
- Unauthorized access to systems or data
- Creating malware or assisting in cyber attacks
- Money laundering, fraud, or other financial crimes
- Copyright infringement or intellectual property theft
- Any other illegal activity

The authors and contributors of this project disclaim all responsibility for any illegal or unethical use of this software. Users assume full legal liability for any violations of law resulting from their use of this tool. If you are unsure whether your intended use is legal, consult with a qualified attorney in your jurisdiction before proceeding.

### Features

-   **Encode**: Hide any file inside a PNG image
-   **Decode**: Extract hidden files from PNG images
-   **Data Integrity**: SHA-1 checksum verification
-   **Password Encryption**: AES-256-CBC encryption with PBKDF2 key derivation
-   **Pixel Scrambling**: Pseudo-random pixel position scrambling using configurable seeds
-   **Error Handling**: Comprehensive error messages and validation
-   **CLI Interface**: Easy-to-use command-line interface

### Requirements

-   Python 3.x
-   Pillow (PIL) library
-   pycryptodome library

Install dependencies:

```bash
pip install -r requirements.txt
```

### Installation

```bash
git clone https://github.com/yourusername/stegano.git
cd stegano
pip install -r requirements.txt
```

### Usage

#### Basic Encode (without scrambling)

```bash
python main.py encode <file_to_hide> <cover_image> <output_image>
```

Example:

```bash
python main.py encode secret.txt cover.png output.png
```

#### Encode with Password Encryption

```bash
python main.py encode <file_to_hide> <cover_image> <output_image> -p PASSWORD
```

Example:

```bash
python main.py encode secret.txt cover.png output.png -p mypassword
```

#### Encode with Pixel Scrambling

```bash
python main.py encode <file_to_hide> <cover_image> <output_image> -s SEED
```

The seed can be:
- An integer: `123456`
- The string `"password"`: Derives seed from a password (requires `-p` flag)
- The string `"image"`: Derives seed from cover image data
- Any custom string: Will be hashed to create a deterministic seed

Examples:

```bash
# Use integer seed
python main.py encode secret.txt cover.png output.png -s 12345

# Derive seed from password
python main.py encode secret.txt cover.png output.png -p mypass -s password

# Derive seed from image
python main.py encode secret.txt cover.png output.png -s image

# Use custom string seed
python main.py encode secret.txt cover.png output.png -s "my-custom-seed"
```

#### Encode with Both Encryption and Scrambling

```bash
python main.py encode <file_to_hide> <cover_image> <output_image> -p PASSWORD -s SEED
```

Example:

```bash
python main.py encode secret.txt cover.png output.png -p mypassword -s password
```

This combines both AES-256 encryption AND pixel scrambling for maximum security.

#### Basic Decode

```bash
python main.py decode <image_with_data> <output_path_or_directory>
```

Example:

```bash
python main.py decode output.png ./extracted/
```

#### Decode with Password Decryption

```bash
python main.py decode <image_with_data> <output_path_or_directory> -p PASSWORD
```

Example:

```bash
python main.py decode output.png ./extracted/ -p mypassword
```

#### Decode with Pixel Unscrambling

```bash
python main.py decode <image_with_data> <output_path_or_directory> -s SEED
```

The seed **must match** the seed used during encoding. Examples:

```bash
# Using integer seed
python main.py decode output.png ./extracted/ -s 12345

# Using password-derived seed
python main.py decode output.png ./extracted/ -p mypass -s password

# Using image-derived seed
python main.py decode output.png ./extracted/ -s image

# Using custom string seed
python main.py decode output.png ./extracted/ -s "my-custom-seed"
```

#### Decode with Both Decryption and Unscrambling

```bash
python main.py decode <image_with_data> <output_path_or_directory> -p PASSWORD -s SEED
```

Example:

```bash
python main.py decode output.png ./extracted/ -p mypassword -s password
```

### Pixel Scrambling

#### What is Pixel Scrambling?

Traditional LSB steganography embeds data sequentially in pixels from left to right, top to bottom. This predictable pattern can be detected by steganalysis tools. Pixel scrambling randomizes the order in which pixels are used for embedding, making the pattern unpredictable and much harder to detect.

#### How It Works

1. **Seed-based Randomization**: The scrambler uses a deterministic pseudo-random number generator seeded with a configurable value
2. **Reproducible**: The same seed always produces the same pixel ordering, allowing correct decoding
3. **Security Enhancement**: Without knowing the seed, an attacker cannot easily identify which pixels contain hidden data
4. **No Data Loss**: All data is still embedded; only the order changes

#### Seed Types

**Integer Seed (Direct)**
- Most efficient
- Use a random number like `12345678`
- Easy to remember/share

```bash
python main.py encode secret.txt cover.png output.png -s 42
```

**Password-Derived Seed**
- Derives seed from your password using PBKDF2-HMAC-SHA256
- Same password always produces the same seed
- Link security to your encryption password

```bash
python main.py encode secret.txt cover.png output.png -p mypass -s password
```

**Image-Derived Seed**
- Derives seed from the cover image's content
- Seed changes if image changes
- Useful for deterministic reproduction without storing separate seed

```bash
python main.py encode secret.txt cover.png output.png -s image
```

**Custom String Seed**
- Any string that isn't "password" or "image"
- Hashed using SHA256 to create deterministic seed
- Flexible and memorable

```bash
python main.py encode secret.txt cover.png output.png -s "my-secret-phrase"
```

#### Security Implications

- **Without Scrambling**: Data embedding follows a predictable sequential pattern (left-to-right, top-to-bottom)
- **With Scrambling**: Data embedding follows a pseudo-random pattern based on the seed
- **Detectability**: Scrambling significantly reduces the effectiveness of steganalysis attacks that look for sequential patterns
- **Brute Force**: With unknown seed, attempting to decode requires trying many possible seeds

### How it Works

#### Encoding Process

1. **Read File**: Load the file to be hidden
2. **Optional Encryption**: If password provided, encrypt using AES-256-CBC with PBKDF2 key derivation
3. **Create Header**: Generate header containing:
    - Magic signature ("LS")
    - Original file size (8 bytes)
    - Original filename (256 bytes)
    - SHA-1 checksum of original data (20 bytes)
4. **Pixel Scrambling**: If seed provided, generate pseudo-random pixel ordering
5. **LSB Embedding**: Convert payload to bits and embed in LSBs of RGB channels, optionally in scrambled order
6. **Save Image**: Save the modified image as PNG

#### Decoding Process

1. **Extract LSBs**: Read LSB values from image pixels, optionally in scrambled order
2. **Verify Signature**: Check for magic signature ("LS")
3. **Extract Metadata**: Read filename and file size from header
4. **Extract Data**: Read specified number of bytes
5. **Optional Decryption**: If password provided, decrypt data
6. **Verify Integrity**: Check SHA-1 checksum against stored value
7. **Save File**: Write extracted data to output location

### Limitations

-   Only PNG images are supported for output
-   The cover image must be large enough to hold the hidden data
-   Capacity is limited: `width × height × 3 bits` (one bit per RGB channel)
-   Scrambling requires knowledge of the seed for decoding
-   Pixel scrambling doesn't eliminate steganography detection, but makes pattern-based detection much harder

### Security Considerations

#### Recommended Usage for Maximum Security

Combine encryption AND scrambling:

```bash
# Encode with both encryption and scrambling
python main.py encode secret.txt cover.png output.png -p strongpassword -s password

# Decode with both decryption and unscrambling
python main.py decode output.png ./extracted/ -p strongpassword -s password
```

#### What Scrambling Protects Against

- **Sequential pattern detection**: Steganalysis tools that look for sequential LSB modifications
- **Simple statistical analysis**: Tools that expect data to appear in predictable positions
- **Pattern-based attacks**: Methods that rely on the embedding pattern being sequential

#### What Scrambling Does NOT Protect Against

- **Brute force seed discovery**: If attacker has computational resources to try many seeds
- **Plaintext visibility**: The scrambled data is still visible as LSB modifications (though pattern is random)
- **Weak passwords**: Password-derived seeds are only as strong as the password
- **Known plaintext attacks**: If attacker knows part of the hidden file

#### Best Practices

1. **Use Strong Passwords**: If using password-derived seeds or encryption
2. **Don't Reuse Seeds**: Use different seeds for different images when possible
3. **Cover Image Selection**: Use high-quality cover images with natural variation
4. **Transmission Security**: Use HTTPS or encrypted channels to transmit output images
5. **Cover Image Distribution**: Don't send cover and output images together
6. **Seed Storage**: Keep seeds secure; consider using password managers for seed strings

### Examples

#### Example 1: Simple Secret Message

```bash
# Encode
python main.py encode message.txt cover.jpg output.jpg

# Decode
python main.py decode output.jpg ./extracted/
```

#### Example 2: Encrypted Secret Document

```bash
# Encode with encryption
python main.py encode secret_doc.pdf cover.png output.png -p "MyStrongPassword123!"

# Decode with decryption
python main.py decode output.png ./extracted/ -p "MyStrongPassword123!"
```

#### Example 3: Encrypted + Scrambled Secret

```bash
# Encode with both encryption and scrambling
python main.py encode sensitive.zip cover.png secure_output.png \
  -p "MyStrongPassword123!" \
  -s password

# Decode with both decryption and unscrambling
python main.py decode secure_output.png ./extracted/ \
  -p "MyStrongPassword123!" \
  -s password
```

#### Example 4: Image-Based Seed

```bash
# Encode using cover image as seed source
python main.py encode secret.txt cover.png output.png -s image

# Decode using same cover image
python main.py decode output.png ./extracted/ -s image
```

#### Example 5: Custom Seed

```bash
# Encode with custom seed phrase
python main.py encode secret.txt cover.png output.png -s "my-secret-phrase-2024"

# Decode with same phrase
python main.py decode output.png ./extracted/ -s "my-secret-phrase-2024"
```

### Testing

Run the test suite:

```bash
python3 -m pytest test_scrambling.py -v
```

Tests cover:
- Seed generation and reproducibility
- Pixel scrambling functionality
- Encode/decode with various combinations
- Password encryption with scrambling
- Edge cases and error conditions

### Documentation

For more detailed information, please refer to:

- **[Pixel Scrambling Guide](docs/PIXEL_SCRAMBLING_GUIDE.md)** - Comprehensive guide on how to use pixel scrambling for enhanced security
  - Technical explanation of how scrambling works
  - Detailed comparison of different seed types
  - Security analysis and best practices
  - Performance benchmarks and troubleshooting

- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical documentation
  - Architecture and design decisions
  - API reference and code structure
  - Security properties and threat model

- **[Changes Log](docs/CHANGES.md)** - Complete list of all changes made
  - New files created
  - Files modified
  - Bug fixes and improvements

- **[Implementation Complete](docs/IMPLEMENTATION_COMPLETE.md)** - Project completion status
  - Verification checklist
  - Quality metrics
  - Quick start guide

- **[Documentation Reorganization](docs/REORGANIZATION.md)** - Information about how documentation is organized
  - File structure and organization
  - How to navigate documentation
  - Benefits of the new structure

### TODO List

- ✅ **Scrambling pseudo-random with seed**: Implemented! Configurable seed-based pixel scrambling for enhanced security
- **Automatic minimum image size calculation**: Calculate and validate minimum required image dimensions based on file size
- **Resistance tests for resize/crop**: Develop robust tests to verify data survival after image transformations
- **Multi-file support**: Add support for embedding multiple files in a single image
- **GUI application**: Create a graphical user interface for easier use
- **JPEG support**: Add support for JPEG output (with quality settings)
- **Progressive encoding**: Support for embedding data across multiple images
- **Advanced scrambling**: Additional scrambling algorithms beyond pseudo-random

### License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.

### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
