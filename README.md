# Stegano - LSB Steganography Tool

A Python tool for hiding files in images using Least Significant Bit (LSB) steganography.

Read this in other languages:

-   [English 🇬🇧](README.md)
-   [Italiano 🇮🇹](README.it.md)

---

#### Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Requirements](#requirements)
-   [Usage](#usage)
-   [How it Works](#how-it-works)
-   [Limitations](#limitations)
-   [TODO List](#todo-list)
-   [License](#license)

---

### 📖 Overview

Stegano is a command-line tool that implements LSB steganography to hide files within PNG images. The tool provides both encoding (hiding) and decoding (extracting) functionality with data integrity verification using SHA-1 checksums.

### ✨ Features

-   **Encode**: Hide any file inside a PNG image
-   **Decode**: Extract hidden files from PNG images
-   **Data Integrity**: SHA-1 checksum verification
-   **Error Handling**: Comprehensive error messages and validation
-   **CLI Interface**: Easy-to-use command-line interface

### 📋 Requirements

-   Python 3.x
-   Pillow (PIL) library

Install dependencies:

```bash
pip install -r requirements.txt
```

### 🚀 Usage

#### Encode a file into an image

```bash
python main.py encode <file_to_hide> <cover_image> <output_image> [-p PASSWORD]
```

Example:

```bash
python main.py encode secret.txt cover.png output.png
```

With encryption:

```bash
python main.py encode secret.txt cover.png output.png -p mypassword
```

#### Decode a file from an image

```bash
python main.py decode <image_with_data> <output_path_or_directory> [-p PASSWORD]
```

Example:

```bash
python main.py decode output.png ./extracted/
```

With decryption:

```bash
python main.py decode output.png ./extracted/ -p mypassword
```

### 🔍 How it Works

1. **Header Creation**: The tool creates a header containing:

    - Magic signature ("LS")
    - Original file size (8 bytes)
    - Original filename (256 bytes)
    - SHA-1 checksum (20 bytes)

2. **LSB Encoding**: The header and file data are converted to bits and embedded in the least significant bits of the RGB channels in the cover image.

3. **Extraction**: When decoding, the tool reads the LSBs, reconstructs the header and data, and verifies integrity using the SHA-1 checksum.

### ⚠️ Limitations

-   Only PNG images are supported for output
-   The cover image must be large enough to hold the hidden data
-   Password-protected encryption uses AES-256-CBC with PBKDF2 key derivation

### 📝 TODO List

-   **Scrambling pseudo-random with seed**: Implement pseudo-random pixel scrambling using configurable seed for enhanced security
-   **Automatic minimum image size calculation**: Calculate and validate minimum required image dimensions based on file size
-   **Resistance tests for resize/crop**: Develop robust tests to verify data survival after image transformations
-   **Multi-file support**: Add support for embedding multiple files in a single image
-   **GUI application**: Create a graphical user interface for easier use

### 📄 License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.
