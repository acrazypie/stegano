# Stegano - LSB Steganography Tool

A Python tool for hiding files in images using Least Significant Bit (LSB) steganography.

---

## [English]

### Overview

Stegano is a command-line tool that implements LSB steganography to hide files within PNG images. The tool provides both encoding (hiding) and decoding (extracting) functionality with data integrity verification using SHA-1 checksums.

### Features

- **Encode**: Hide any file inside a PNG image
- **Decode**: Extract hidden files from PNG images  
- **Data Integrity**: SHA-1 checksum verification
- **Error Handling**: Comprehensive error messages and validation
- **CLI Interface**: Easy-to-use command-line interface

### Requirements

- Python 3.x
- Pillow (PIL) library

Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

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

### How it Works

1. **Header Creation**: The tool creates a header containing:
   - Magic signature ("LS")
   - Original file size (8 bytes)
   - Original filename (256 bytes)
   - SHA-1 checksum (20 bytes)

2. **LSB Encoding**: The header and file data are converted to bits and embedded in the least significant bits of the RGB channels in the cover image.

3. **Extraction**: When decoding, the tool reads the LSBs, reconstructs the header and data, and verifies integrity using the SHA-1 checksum.

### Limitations

- Only PNG images are supported for output
- The cover image must be large enough to hold the hidden data
- Password-protected encryption uses AES-256-CBC with PBKDF2 key derivation

### TODO List

- **Scrambling pseudo-random with seed**: Implement pseudo-random pixel scrambling using configurable seed for enhanced security
- **Automatic minimum image size calculation**: Calculate and validate minimum required image dimensions based on file size
- **Resistance tests for resize/crop**: Develop robust tests to verify data survival after image transformations
- **Multi-file support**: Add support for embedding multiple files in a single image

---

## [Italiano]

### Panoramica

Stegano è uno strumento a riga di comando che implementa la steganografia LSB per nascondere file all'interno di immagini PNG. Lo strumento fornisce sia funzionalità di codifica (nascondimento) che di decodifica (estrazione) con verifica dell'integrità dei dati tramite checksum SHA-1.

### Caratteristiche

- **Encode**: Nascondi qualsiasi file all'interno di un'immagine PNG
- **Decode**: Estrai file nascosti da immagini PNG
- **Integrità Dati**: Verifica del checksum SHA-1
- **Gestione Errori**: Messaggi di errore completi e validazione
- **Interfaccia CLI**: Interfaccia a riga di comando facile da usare

### Requisiti

- Python 3.x
- Libreria Pillow (PIL)

Installa le dipendenze:
```bash
pip install -r requirements.txt
```

### Utilizzo

#### Codifica un file in un'immagine
```bash
python main.py encode <file_da_nascondere> <immagine_copertura> <immagine_output> [-p PASSWORD]
```

Esempio:
```bash
python main.py encode segreto.txt copertura.png output.png
```

Con crittografia:
```bash
python main.py encode segreto.txt copertura.png output.png -p miapassword
```

#### Decodifica un file da un'immagine
```bash
python main.py decode <immagine_con_dati> <percorso_output_o_directory> [-p PASSWORD]
```

Esempio:
```bash
python main.py decode output.png ./estratti/
```

Con decrittografia:
```bash
python main.py decode output.png ./estratti/ -p miapassword
```

### Come Funziona

1. **Creazione Header**: Lo strumento crea un header contenente:
   - Firma magica ("LS")
   - Dimensione file originale (8 byte)
   - Nome file originale (256 byte)
   - Checksum SHA-1 (20 byte)

2. **Codifica LSB**: L'header e i dati del file vengono convertiti in bit e incorporati nei bit meno significativi dei canali RGB nell'immagine di copertura.

3. **Estrazione**: Durante la decodifica, lo strumento legge i bit LSB, ricostruisce l'header e i dati, e verifica l'integrità usando il checksum SHA-1.

### Limitazioni

- Solo le immagini PNG sono supportate come output
- L'immagine di copertura deve essere abbastanza grande da contenere i dati nascosti
- La crittografia con password usa AES-256-CBC con derivazione chiave PBKDF2

### TODO List

- **Scrambling pseudo-random con seed**: Implementare scrambling pseudo-random dei pixel usando seed configurabile per maggiore sicurezza
- **Calcolo automatico dimensione minima immagine**: Calcolare e validare le dimensioni minime richieste dell'immagine basate sulla dimensione del file
- **Test di resistenza a resize/crop**: Sviluppare test robusti per verificare la sopravvivenza dei dati dopo trasformazioni dell'immagine
- **Supporto multi-file**: Aggiungere supporto per incorporare più file in una singola immagine

---

## License

This project is released under the MIT License.