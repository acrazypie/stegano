# Stegano - Strumento di Steganografia LSB

Uno strumento Python per nascondere file in immagini utilizzando la steganografia Least Significant Bit (LSB) con scrambling di pixel pseudo-casuale opzionale per una sicurezza migliorata.

##### Leggi questo in altre lingue:

-   [English 🇬🇧](../README.md)
-   [Italiano 🇮🇹](README.it.md)

### Indice dei contenuti

-   [Panoramica](#panoramica)
-   [Caratteristiche](#caratteristiche)
-   [Requisiti](#requisiti)
-   [Installazione](#installazione)
-   [Utilizzo](#utilizzo)
-   [Scrambling di Pixel](#scrambling-di-pixel)
-   [Come Funziona](#come-funziona)
-   [Sicurezza](#sicurezza)
-   [Limitazioni](#limitazioni)
-   [Esempi](#esempi)
-   [Documentazione](#documentazione)
-   [TODO List](#todo-list)
-   [Licenza](#licenza)

---

### Panoramica

Stegano è uno strumento a riga di comando che implementa la steganografia LSB per nascondere file all'interno di immagini PNG. Lo strumento fornisce sia funzionalità di codifica (nascondimento) che di decodifica (estrazione) con verifica dell'integrità dei dati tramite checksum SHA-1. Ora con supporto per scrambling pseudo-casuale di pixel per una sicurezza significativamente migliorata contro gli attacchi di stegananalisi.

### Caratteristiche

-   **Codifica**: Nascondi qualsiasi file all'interno di un'immagine PNG
-   **Decodifica**: Estrai file nascosti da immagini PNG
-   **Integrità Dati**: Verifica del checksum SHA-1
-   **Crittografia con Password**: Crittografia AES-256-CBC con derivazione chiave PBKDF2
-   **Scrambling di Pixel**: Scrambling pseudo-casuale di posizioni di pixel utilizzando seed configurabili
-   **Gestione Errori**: Messaggi di errore completi e validazione
-   **Interfaccia CLI**: Interfaccia a riga di comando facile da usare

### Requisiti

-   Python 3.x
-   Libreria Pillow (PIL)
-   Libreria pycryptodome

### Installazione

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

### Utilizzo

#### Codifica Base (senza scrambling)

```bash
python main.py encode <file_da_nascondere> <immagine_copertura> <immagine_output>
```

Esempio:

```bash
python main.py encode segreto.txt copertura.png output.png
```

#### Codifica con Crittografia Password

```bash
python main.py encode <file_da_nascondere> <immagine_copertura> <immagine_output> -p PASSWORD
```

Esempio:

```bash
python main.py encode segreto.txt copertura.png output.png -p miapassword
```

#### Codifica con Scrambling di Pixel

```bash
python main.py encode <file_da_nascondere> <immagine_copertura> <immagine_output> -s SEED
```

Il seed può essere:
- Un numero intero: `123456`
- La stringa `"password"`: Deriva il seed dalla password (richiede il flag `-p`)
- La stringa `"image"`: Deriva il seed dai dati dell'immagine di copertura
- Una stringa personalizzata: Verrà sottoposta a hashing per creare un seed deterministico

Esempi:

```bash
# Usa seed intero
python main.py encode segreto.txt copertura.png output.png -s 12345

# Deriva seed dalla password
python main.py encode segreto.txt copertura.png output.png -p miapass -s password

# Deriva seed dall'immagine
python main.py encode segreto.txt copertura.png output.png -s image

# Usa seed personalizzato
python main.py encode segreto.txt copertura.png output.png -s "my-custom-seed"
```

#### Codifica con Crittografia e Scrambling

```bash
python main.py encode <file_da_nascondere> <immagine_copertura> <immagine_output> -p PASSWORD -s SEED
```

Esempio:

```bash
python main.py encode segreto.txt copertura.png output.png -p miapassword -s password
```

Questo combina sia la crittografia AES-256 che lo scrambling di pixel per la massima sicurezza.

#### Decodifica Base

```bash
python main.py decode <immagine_con_dati> <percorso_output_o_directory>
```

Esempio:

```bash
python main.py decode output.png ./estratti/
```

#### Decodifica con Crittografia Password

```bash
python main.py decode <immagine_con_dati> <percorso_output_o_directory> -p PASSWORD
```

Esempio:

```bash
python main.py decode output.png ./estratti/ -p miapassword
```

#### Decodifica con Scrambling di Pixel

```bash
python main.py decode <immagine_con_dati> <percorso_output_o_directory> -s SEED
```

Lo seed **deve corrispondere** allo seed utilizzato durante la codifica. Esempi:

```bash
# Usa seed intero
python main.py decode output.png ./estratti/ -s 12345

# Usa seed derivato dalla password
python main.py decode output.png ./estratti/ -p miapass -s password

# Usa seed derivato dall'immagine
python main.py decode output.png ./estratti/ -s image

# Usa seed personalizzato
python main.py decode output.png ./estratti/ -s "my-custom-seed"
```

#### Decodifica con Crittografia e Unscrambling

```bash
python main.py decode <immagine_con_dati> <percorso_output_o_directory> -p PASSWORD -s SEED
```

Esempio:

```bash
python main.py decode output.png ./estratti/ -p miapassword -s password
```

### Scrambling di Pixel

#### Cos'è lo Scrambling di Pixel?

La steganografia LSB tradizionale incorpora i dati sequenzialmente nei pixel in ordine prevedibile. Lo scrambling di pixel randomizza l'ordine in cui le posizioni dei pixel (e i loro canali RGB) vengono utilizzate per incorporare i dati LSB. Invece di riempire i pixel sequenzialmente dall'angolo in alto a sinistra, lo scrambler genera un ordine pseudo-casuale basato su un valore di seed. Questo rende lo schema di incorporamento dei dati impredittibile e molto più difficile da rilevare tramite l'analisi steganografica.

#### Tipi di Seed

**Seed Intero (Diretto)**
- Più efficiente
- Usare un numero casuale come `12345678`
- Facile da ricordare/condividere

```bash
python main.py encode segreto.txt copertura.png output.png -s 42
```

**Seed Derivato da Password**
- Deriva il seed dalla password utilizzando PBKDF2-HMAC-SHA256
- La stessa password produce sempre lo stesso seed
- Collega la sicurezza alla password di crittografia

```bash
python main.py encode segreto.txt copertura.png output.png -p miapass -s password
```

**Seed Derivato dall'Immagine**
- Deriva il seed dal contenuto dell'immagine di copertura
- Lo seed cambia se l'immagine cambia
- Utile per la riproduzione deterministica senza memorizzare un seed separato

```bash
python main.py encode segreto.txt copertura.png output.png -s image
```

**Seed Personalizzato**
- Qualsiasi stringa che non sia "password" o "image"
- Sottoposto a hashing utilizzando SHA256 per creare un seed deterministico
- Flessibile e memorabile

```bash
python main.py encode segreto.txt copertura.png output.png -s "my-secret-phrase"
```

#### Implicazioni di Sicurezza

- **Senza Scrambling**: L'incorporamento dei dati segue un modello sequenziale prevedibile (da sinistra a destra, dall'alto al basso)
- **Con Scrambling**: L'incorporamento dei dati segue un modello pseudo-casuale basato sul seed
- **Rilevabilità**: Lo scrambling riduce significativamente l'efficacia degli attacchi di stegananalisi che cercano modelli sequenziali
- **Forza Bruta**: Con seed sconosciuto, il tentativo di decodifica richiede di provare molti seed possibili

### Come Funziona

#### Processo di Codifica

1. **Leggi File**: Carica il file da nascondere
2. **Crittografia Opzionale**: Se fornita una password, crittografa utilizzando AES-256-CBC con derivazione chiave PBKDF2
3. **Crea Header**: Genera header contenente:
    - Firma magica ("LS")
    - Dimensione file originale (8 byte)
    - Nome file originale (256 byte)
    - Checksum SHA-1 dei dati originali (20 byte)
4. **Scrambling di Pixel**: Se fornito un seed, genera un ordine pseudo-casuale di pixel
5. **Incorporamento LSB**: Converti il payload in bit e incorpora i bit LSB dei canali RGB, facoltativamente in ordine scombinato
6. **Salva Immagine**: Salva l'immagine modificata come PNG

#### Processo di Decodifica

1. **Estrai LSB**: Leggi i valori LSB dai pixel dell'immagine, facoltativamente in ordine scombinato
2. **Verifica Firma**: Controlla la firma magica ("LS")
3. **Estrai Metadati**: Leggi il nome del file e le dimensioni dal header
4. **Estrai Dati**: Leggi il numero specificato di byte
5. **Decrittografia Opzionale**: Se fornita una password, decrittografa i dati
6. **Verifica Integrità**: Controlla il checksum SHA-1 rispetto al valore memorizzato
7. **Salva File**: Scrivi i dati estratti nel percorso di output

### Sicurezza

#### Sicurezza della Crittografia

- **Algoritmo**: AES-256-CBC
- **Derivazione Chiave**: PBKDF2 con 100.000 iterazioni
- **Sale**: 16 byte casuali per crittografia
- **IV**: 16 byte casuali per crittografia
- **Sovraccarico Crittografia Totale**: 32 byte (16 salt + 16 IV) più padding

#### Sicurezza dello Scrambling

- **Algoritmo**: Shuffling casuale con seed (Python's random.shuffle con seed deterministico)
- **Opzioni di Seed**:
  - Seed interi per riproducibilità
  - Derivazione basata su SHA256 per seed di password/stringa
  - Derivazione basata su hash di immagine per seed dipendenti dall'immagine di copertura
- **Vantaggi**:
  - Rende il modello LSB impredittibile senza conoscere il seed
  - Resistente agli attacchi di stegananalisi che assumono incorporamento sequenziale
  - Si combina bene con la crittografia password per la sicurezza stratificata

#### Sicurezza Combinata

L'utilizzo sia della crittografia che dello scrambling fornisce protezione difensiva:
- **Crittografia** protegge il contenuto del file
- **Scrambling** protegge il modello di incorporamento stesso

Utilizzo sicuro consigliato:
```bash
python main.py encode segreto.txt copertura.png output.png -p miapassword -s password
```

### Limitazioni

-   Solo le immagini PNG sono supportate come output
-   L'immagine di copertura deve essere abbastanza grande da contenere i dati nascosti
-   La capacità è limitata a: `larghezza × altezza × 3 bit` (un bit per canale RGB)
-   Lo scrambling richiede la conoscenza del seed per la decodifica
-   Lo scrambling di pixel non elimina il rilevamento della steganografia, ma rende il rilevamento basato su modelli molto più difficile

### Esempi

#### Esempio 1: Messaggio Segreto Semplice

```bash
# Codifica
python main.py encode messaggio.txt copertura.jpg output.jpg

# Decodifica
python main.py decode output.jpg ./estratti/
```

#### Esempio 2: Documento Segreto Crittografato

```bash
# Codifica con crittografia
python main.py encode documento_segreto.pdf copertura.png output.png -p "MiaPasswordForte123!"

# Decodifica con decrittografia
python main.py decode output.png ./estratti/ -p "MiaPasswordForte123!"
```

#### Esempio 3: Segreto Crittografato + Scombinato

```bash
# Codifica con crittografia e scrambling
python main.py encode sensibile.zip copertura.png secure_output.png \
  -p "MiaPasswordForte123!" \
  -s password

# Decodifica con decrittografia e unscrambling
python main.py decode secure_output.png ./estratti/ \
  -p "MiaPasswordForte123!" \
  -s password
```

#### Esempio 4: Seed Basato su Immagine

```bash
# Codifica usando l'immagine di copertura come fonte di seed
python main.py encode segreto.txt copertura.png output.png -s image

# Decodifica usando la stessa immagine di copertura
python main.py decode output.png ./estratti/ -s image
```

#### Esempio 5: Seed Personalizzato

```bash
# Codifica con frase di seed personalizzata
python main.py encode segreto.txt copertura.png output.png -s "my-secret-phrase-2024"

# Decodifica con la stessa frase
python main.py decode output.png ./estratti/ -s "my-secret-phrase-2024"
```

### Test

Esegui la suite di test:

```bash
python3 -m pytest test_scrambling.py -v
```

I test coprono:
- Generazione e riproducibilità del seed
- Funzionalità di scrambling di pixel
- Codifica/decodifica con varie combinazioni
- Crittografia password con scrambling
- Casi limite e condizioni di errore

### Documentazione

Per informazioni più dettagliate, consultare:

- **[Guida allo Scrambling di Pixel](PIXEL_SCRAMBLING_GUIDE.md)** - Guida completa su come utilizzare lo scrambling di pixel per una sicurezza migliorata
  - Spiegazione tecnica di come funziona lo scrambling
  - Confronto dettagliato dei diversi tipi di seed
  - Analisi della sicurezza e migliori pratiche
  - Benchmark di prestazioni e risoluzione dei problemi

- **[Riepilogo dell'Implementazione](IMPLEMENTATION_SUMMARY.md)** - Documentazione tecnica
  - Architettura e decisioni di progettazione
  - Riferimento API e struttura del codice
  - Proprietà di sicurezza e modello di minaccia

- **[Registro dei Cambiamenti](CHANGES.md)** - Elenco completo di tutti i cambiamenti apportati
  - Nuovi file creati
  - File modificati
  - Correzioni di bug e miglioramenti

- **[Implementazione Completata](IMPLEMENTATION_COMPLETE.md)** - Stato di completamento del progetto
  - Elenco di verifica
  - Metriche di qualità
  - Guida di avvio rapido

### TODO List

- ✅ **Scrambling pseudo-random con seed**: Implementato! Scrambling di pixel basato su seed configurabile per una sicurezza migliorata
- **Calcolo automatico dimensione minima immagine**: Calcolare e validare le dimensioni minime richieste dell'immagine basate sulla dimensione del file
- **Test di resistenza a resize/crop**: Sviluppare test robusti per verificare la sopravvivenza dei dati dopo trasformazioni dell'immagine
- **Supporto multi-file**: Aggiungere supporto per incorporare più file in una singola immagine
- **Applicazione GUI**: Creare un'interfaccia grafica per un uso più semplice
- **Supporto JPEG**: Aggiungere supporto per output JPEG (con impostazioni di qualità)
- **Codifica Progressiva**: Supporto per l'incorporamento di dati su più immagini
- **Scrambling Avanzato**: Algoritmi di scrambling aggiuntivi oltre lo pseudo-casuale

### Licenza

Questo progetto è concesso in licenza sotto la Licenza MIT. Vedi il file [LICENSE](../LICENSE) per i dettagli.

### Contribuire

I contributi sono benvenuti! Si prega di sentirsi liberi di inviare richieste di pull o aprire problemi per bug e richieste di funzionalità.