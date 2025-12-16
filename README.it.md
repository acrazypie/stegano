# Stegano - Italiano

### Indice dei contenuti

-   [Panoramica](#panoramica)
-   [Caratteristiche](#caratteristiche)
-   [Requisiti](#requisiti)
-   [Utilizzo](#utilizzo)
-   [Come Funziona](#come-funziona)
-   [Limitazioni](#limitazioni)
-   [TODO List](#todo-list)
-   [Licenza](#licenza)

### Panoramica

Stegano è uno strumento a riga di comando che implementa la steganografia LSB per nascondere file all'interno di immagini PNG. Lo strumento fornisce sia funzionalità di codifica (nascondimento) che di decodifica (estrazione) con verifica dell'integrità dei dati tramite checksum SHA-1.

### Caratteristiche

-   **Encode**: Nascondi qualsiasi file all'interno di un'immagine PNG
-   **Decode**: Estrai file nascosti da immagini PNG
-   **Integrità Dati**: Verifica del checksum SHA-1
-   **Gestione Errori**: Messaggi di errore completi e validazione
-   **Interfaccia CLI**: Interfaccia a riga di comando facile da usare

### Requisiti

-   Python 3.x
-   Libreria Pillow (PIL)

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

-   Solo le immagini PNG sono supportate come output
-   L'immagine di copertura deve essere abbastanza grande da contenere i dati nascosti
-   La crittografia con password usa AES-256-CBC con derivazione chiave PBKDF2

### TODO List

-   **Scrambling pseudo-random con seed**: Implementare scrambling pseudo-random dei pixel usando seed configurabile per maggiore sicurezza
-   **Calcolo automatico dimensione minima immagine**: Calcolare e validare le dimensioni minime richieste dell'immagine basate sulla dimensione del file
-   **Test di resistenza a resize/crop**: Sviluppare test robusti per verificare la sopravvivenza dei dati dopo trasformazioni dell'immagine
-   **Supporto multi-file**: Aggiungere supporto per incorporare più file in una singola immagine
-   **Applicazione GUI**: Creare un'interfaccia grafica per un uso più semplice

### Licenza

Questo progetto è concesso in licenza sotto la Licenza MIT. Vedi il file [LICENSE](LICENSE) per i dettagli.
