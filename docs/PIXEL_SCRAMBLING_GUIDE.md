# Pixel Scrambling Guide

## Overview

Pixel scrambling is an advanced security feature that enhances LSB steganography by randomizing the order in which pixels are used to embed hidden data. This guide explains how it works, when to use it, and best practices for maximum security.

## Table of Contents

1. [What is Pixel Scrambling?](#what-is-pixel-scrambling)
2. [Why Use Pixel Scrambling?](#why-use-pixel-scrambling)
3. [How It Works](#how-it-works)
4. [Seed Types](#seed-types)
5. [Security Analysis](#security-analysis)
6. [Best Practices](#best-practices)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)
10. [FAQ](#faq)

## What is Pixel Scrambling?

### The Problem with Sequential LSB Embedding

Traditional LSB steganography embeds data sequentially:
- Start at pixel (0, 0), channel R (red)
- Then pixel (0, 0), channel G (green)
- Then pixel (0, 0), channel B (blue)
- Then pixel (1, 0), channel R
- And so on...

This predictable pattern creates a **statistical anomaly** that steganalysis tools can detect:
- LSB values show suspiciously low entropy in the sequential region
- The transition between embedded and non-embedded data is abrupt
- Pattern analysis reveals the exact embedding location

### Pixel Scrambling Solution

Pixel scrambling randomizes the pixel order using a seed-based pseudo-random number generator:
- Pixel positions (x, y, channel) are shuffled deterministically
- Same seed always produces the same order (reproducibility)
- Without the seed, pixel order appears random
- Statistical anomalies are distributed throughout the image

**Visual Example:**

Sequential embedding fills pixels like this:
```
Image: ████████
       ████████

Data fills: Pixel 0 → Pixel 1 → Pixel 2 → ... in strict order
LSB anomaly: Clearly visible region with modified LSBs
```

Scrambled embedding fills pixels like this:
```
Image: ██▓█▓███
       ▓█▓██▓██

Data fills: Pixel 15 → Pixel 3 → Pixel 42 → ... in random order
LSB anomaly: Scattered throughout image, hard to detect
```

## Why Use Pixel Scrambling?

### Security Benefits

1. **Resistant to Pattern-Based Analysis**
   - Sequential patterns are a major detection vector
   - Scrambling eliminates this vector entirely

2. **Distributed Statistical Anomalies**
   - Sequential embedding creates a clear "edge" where data ends
   - Scrambling spreads anomalies uniformly across the image

3. **Layered Security**
   - Encryption (optional) protects content
   - Scrambling (optional) protects embedding pattern
   - Together they provide defense-in-depth

4. **Steganalysis Resistance**
   - Defeats chi-squared steganalysis attacks
   - Resists sample pair analysis methods
   - Survives histogram analysis better than sequential

### When to Use Scrambling

| Scenario | Use Scrambling? | Reason |
|----------|---|---|
| Personal use, no threat model | No | Unnecessary complexity |
| Casual image sharing | No | Sequential embedding is often sufficient |
| Competitive/adversarial environments | **Yes** | Essential for avoiding detection |
| Sensitive information | **Yes** | Belt-and-suspenders approach |
| With password encryption | **Yes** | Complements encryption well |
| Large hidden files | **Yes** | Distributes anomalies better |
| Research/testing steganalysis | **Yes** | Provides more robust baseline |

## How It Works

### Seed-Based Randomization

The scrambler uses Python's `random.Random` class with a seed:

```python
rng = random.Random(seed)
pixel_positions = [(x, y, channel) for all combinations]
rng.shuffle(pixel_positions)  # In-place shuffling
```

### Seed Resolution Process

Different seed inputs are converted to integer seeds:

1. **Integer Seed** → Used directly
2. **Password Seed** → SHA256(password) → First 8 bytes as int
3. **Image Seed** → SHA256(image_bytes) → First 8 bytes as int
4. **String Seed** → SHA256(string) → First 8 bytes as int
5. **None** → No scrambling (sequential embedding)

### Bit Embedding

After scrambling, bits are embedded in the shuffled order:

```
Payload bits: [1, 0, 1, 1, 0, 1, ...]
Shuffled positions: [(45, 12, 0), (2, 3, 1), (67, 89, 2), ...]

Bit 0 (value 1) → Embed in pixel (45, 12), channel R (LSB = 1)
Bit 1 (value 0) → Embed in pixel (2, 3), channel G (LSB = 0)
Bit 2 (value 1) → Embed in pixel (67, 89), channel B (LSB = 1)
...
```

### Deterministic Reproducibility

The shuffle is deterministic: same seed always produces same order

```python
# Encoding
seed = 12345
order1 = get_shuffled_positions(200, 200, seed)  # Specific order

# Decoding
seed = 12345
order2 = get_shuffled_positions(200, 200, seed)  # Identical order!
```

This allows the decoder to reverse the process without storing the pixel order.

## Seed Types

### 1. Integer Seeds

**Format:** Direct integer values
```bash
python main.py encode secret.txt cover.png output.png -s 123456
python main.py decode output.png ./extracted/ -s 123456
```

**Characteristics:**
- ✅ Fast (no hashing needed)
- ✅ Reproducible
- ✅ Easy to share
- ❌ No semantic meaning
- ❌ Weak against brute-force (only 2^31 possibilities)

**Best For:** 
- Quick testing
- Scenario where seed is safely transmitted
- Simple reproducibility

**Example:**
```bash
# Use a memorable number
python main.py encode secret.txt cover.png output.png -s 19700101

# Or a random large number
python main.py encode secret.txt cover.png output.png -s $RANDOM$RANDOM
```

### 2. Password-Derived Seeds

**Format:** The string `"password"`
```bash
python main.py encode secret.txt cover.png output.png -p mypassword -s password
python main.py decode output.png ./extracted/ -p mypassword -s password
```

**Characteristics:**
- ✅ Tied to encryption password
- ✅ No separate seed to manage
- ✅ Strong if password is strong
- ❌ Requires password to be known
- ❌ Salt/derivation adds overhead

**How It Works:**
```
Password "MySecurePass123" 
  ↓ PBKDF2-HMAC-SHA256(100,000 iterations)
  ↓ 32-byte derived key
  ↓ Take first 8 bytes as integer
  ↓ Seed = deterministic value
```

**Best For:**
- Combining encryption and scrambling security
- When you don't want separate secrets to manage
- Maximum convenience with good security

**Example:**
```bash
# Encryption and scrambling both use same password
python main.py encode secret.txt cover.png output.png \
  -p "MyStrongPassword2024!" \
  -s password

# To decode, just use same password twice
python main.py decode output.png ./extracted/ \
  -p "MyStrongPassword2024!" \
  -s password
```

### 3. Image-Derived Seeds

**Format:** The string `"image"`
```bash
python main.py encode secret.txt cover.png output.png -s image
python main.py decode output.png ./extracted/ -s image
```

**Characteristics:**
- ✅ Unique per cover image
- ✅ No separate seed to manage
- ✅ Reproducible for same image
- ❌ Requires exact same cover image
- ❌ Won't work if cover image is modified

**How It Works:**
```
Cover image bytes (PNG file)
  ↓ SHA256 hash
  ↓ 32-byte digest
  ↓ Take first 8 bytes as integer
  ↓ Seed = deterministic value
```

**Best For:**
- Deterministic seeding without password
- Scenarios where cover image is safely stored
- Research or testing

**Important:** The encoder needs to read the cover image file, so it must be on disk. The decoder also needs the output image file.

**Example:**
```bash
# Encode with image-derived seed
python main.py encode secret.txt cover.png output.png -s image

# Decode with image-derived seed (uses output.png for seed)
python main.py decode output.png ./extracted/ -s image
```

### 4. Custom String Seeds

**Format:** Any string except `"password"` or `"image"`
```bash
python main.py encode secret.txt cover.png output.png -s "my-secret-phrase"
python main.py decode output.png ./extracted/ -s "my-secret-phrase"
```

**Characteristics:**
- ✅ Memorable and meaningful
- ✅ Can encode semantic information
- ✅ As strong as password (SHA256 derived)
- ❌ Requires string to be remembered/transmitted
- ❌ Vulnerable to dictionary attacks if weak phrase

**How It Works:**
```
String "my-secret-phrase"
  ↓ PBKDF2-HMAC-SHA256(100,000 iterations)
  ↓ 32-byte derived key
  ↓ Take first 8 bytes as integer
  ↓ Seed = deterministic value
```

**Best For:**
- Memorable phrases
- Multi-word passphrases
- Descriptive seed names

**Example:**
```bash
# Encode with memorable phrase
python main.py encode secret.txt cover.png output.png \
  -s "beach-vacation-2024"

# Decode with same phrase
python main.py decode output.png ./extracted/ \
  -s "beach-vacation-2024"
```

## Security Analysis

### Threat Model

This analysis assumes:
- Attacker can see output images
- Attacker uses steganalysis tools
- Attacker does NOT have passwords or seeds (standard steganography threat model)

### Effectiveness Against Different Attacks

#### 1. Chi-Squared Steganalysis
**Status:** ✅ Resistant

Chi-squared attacks look for sequential patterns:
- Sequential embedding: Very effective detection
- Scrambled embedding: Attacks fail (no sequential pattern)

#### 2. Sample Pair Analysis
**Status:** ✅ Partially Resistant

Sample pair analysis compares LSB values:
- Sequential embedding: Detectable patterns
- Scrambled embedding: Patterns distributed randomly

#### 3. Histogram Analysis
**Status:** ✅ Improved

Histogram attacks look for LSB biases:
- Sequential embedding: Biases concentrated in embedded region
- Scrambled embedding: Biases distributed uniformly

#### 4. Brute Force Seed Discovery
**Status:** ⚠️ Moderate Risk

Without seed, attacker could try multiple seeds:
- Integer seeds: 2^31 possibilities (~2 billion)
- Modern computers: Can try ~1 billion seeds per hour
- Time to exhaustive search: ~1 hour to guarantee finding seed

**Mitigation:** Use strong password-derived or image-derived seeds

#### 5. Statistical Steganalysis
**Status:** ⚠️ Vulnerable

Advanced statistical methods (machine learning):
- Sequential embedding: Highly detectable
- Scrambled embedding: Harder to detect
- However: Advanced ML might still detect any LSB embedding
- Mitigation: Combine with encryption

### Security Comparison

| Method | Detection Risk | Implementation | Recommended |
|--------|---|---|---|
| No scrambling | **High** | Easy | For non-adversarial use |
| Integer seed only | **Medium** | Easy | Quick security boost |
| Password-derived seed | **Low** | Medium | Recommended |
| Image-derived seed | **Low** | Medium | For deterministic reproducibility |
| Password + encryption | **Very Low** | Medium | Maximum security |
| Password + encryption + scrambling | **Minimal** | Medium | Paranoia mode |

## Best Practices

### 1. Seed Management

**DO:**
- ✅ Use strong passwords if using password-derived seeds
- ✅ Store seeds securely (password manager, encrypted file)
- ✅ Use different seeds for different images
- ✅ Document seed method for reproducibility

**DON'T:**
- ❌ Use weak or predictable seed strings
- ❌ Reuse same seed for many images
- ❌ Send seed with output image
- ❌ Hardcode seeds in scripts

**Example:**
```bash
# Good: Random seed stored securely
SEED=$(cat /dev/urandom | tr -cd '0-9' | head -c 10)
python main.py encode secret.txt cover.png output.png -s $SEED

# Better: Use password-derived seed
python main.py encode secret.txt cover.png output.png \
  -p "$(pass show my-secret-password)" \
  -s password

# Bad: Predictable seed
python main.py encode secret.txt cover.png output.png -s 1234567
```

### 2. Security Layering

**Minimal Security:**
```bash
python main.py encode secret.txt cover.png output.png
```
Uses sequential embedding (vulnerable to steganalysis)

**Basic Security:**
```bash
python main.py encode secret.txt cover.png output.png -s 12345
```
Adds scrambling (resistant to pattern-based attacks)

**Strong Security:**
```bash
python main.py encode secret.txt cover.png output.png \
  -p "strong-password" \
  -s password
```
Adds both encryption and scrambling (defense-in-depth)

**Maximum Security:**
```bash
# Use different seed for each image
SEED=$RANDOM
python main.py encode secret.txt cover.png output.png \
  -p "strong-password-$(date +%s)" \
  -s password

# Rotate passwords and seeds regularly
```

### 3. Cover Image Selection

**Good Cover Images:**
- ✅ High-resolution photos (more pixels = better hiding)
- ✅ Natural scenes with variation
- ✅ Professional photographs
- ✅ Complex texture/color patterns

**Poor Cover Images:**
- ❌ Simple graphics or solid colors
- ❌ Small images (<500x500)
- ❌ Highly compressed JPEG
- ❌ Images with obvious patterns

**Why it Matters:**
Scrambling distributes data throughout image, but it still modifies LSBs. Natural variation helps hide LSB changes.

### 4. Operational Security

**DO:**
- ✅ Use HTTPS for transmitting images
- ✅ Keep cover images secure
- ✅ Don't send cover + output together
- ✅ Use temporary files for intermediate data
- ✅ Shred temporary files after use

**DON'T:**
- ❌ Send unencrypted images over HTTP
- ❌ Store both cover and output images together
- ❌ Reuse same password for multiple purposes
- ❌ Leave temporary files on disk
- ❌ Assume image won't be analyzed

**Example Secure Workflow:**
```bash
# 1. Create strong password
PASSWORD=$(openssl rand -base64 32)

# 2. Encode with encryption and scrambling
python main.py encode secret.txt cover.png output.png \
  -p "$PASSWORD" \
  -s password

# 3. Securely transmit password separately
echo "$PASSWORD" | mail -s "Seed" recipient@example.com

# 4. Upload image over HTTPS
curl -F "file=@output.png" https://secure-server.com/upload

# 5. Clear sensitive data from memory
unset PASSWORD
```

### 5. Testing and Validation

**Validate Setup:**
```bash
# 1. Create test cover image
python3 << 'EOF'
from PIL import Image
img = Image.new('RGB', (800, 600), color=(100, 150, 200))
img.save('test_cover.png')
EOF

# 2. Create test secret
echo "Test secret message" > test_secret.txt

# 3. Encode
python main.py encode test_secret.txt test_cover.png test_output.png \
  -p "testpass" -s password

# 4. Decode
python main.py decode test_output.png ./test_extracted/ \
  -p "testpass" -s password

# 5. Verify
diff test_secret.txt test_extracted/test_secret.txt && echo "✓ Success"

# 6. Clean up
rm -f test_secret.txt test_cover.png test_output.png test_extracted/*
```

## Performance Considerations

### Encoding Time

**Factors Affecting Speed:**

1. **Seed Generation:** ~10-50ms per image
   - Integer: ~1ms (no hashing)
   - String/password: ~10-50ms (PBKDF2 with 100k iterations)
   - Image: ~50-100ms (file I/O + SHA256)

2. **Scrambling:** ~50-200ms per image
   - Proportional to image size
   - ~1 ms per megapixel

3. **Total Overhead:** 5-10% slower than sequential embedding

### Memory Usage

- **Sequential**: ~3MB per megapixel (pixel array)
- **Scrambled**: ~3MB + shuffled position list
- **Position List**: ~24 bytes per position (x, y, channel)
- **Extra Memory**: ~72MB per megapixel

### Optimization Tips

**For Large Images:**
```bash
# Scrambling is negligible compared to I/O
# Use it freely; performance difference is minimal
python main.py encode huge_file.bin large_image.png output.png -s password
```

**For Batch Processing:**
```bash
# Process multiple images in parallel
for image in *.png; do
  python main.py encode secret.txt "$image" "encoded_$image" -s password &
done
wait
```

**For Real-Time Applications:**
```bash
# Scrambling is fast enough for real-time use
# Typical 800x600 image: encode in <1 second
# Typical 4K image: encode in <5 seconds
```

## Troubleshooting

### Issue: "Firma non valida" (Invalid Signature)

**Cause:** Wrong seed used for decoding

**Solution:**
```bash
# Verify you're using correct seed
python main.py decode output.png ./extracted/ -s correct_seed

# If you forgot the seed:
# - Try again with password-derived seed if you used -s password
# - Try again with image-derived seed if you used -s image
# - Otherwise, you're locked out (by design!)
```

### Issue: Different Image Decodes Different Data

**Cause:** Using image-derived seed with different output image

**Solution:**
```bash
# When decoding, use the ENCODED output image, not the cover
# WRONG:
python main.py decode cover.png ./extracted/ -s image

# CORRECT:
python main.py decode output.png ./extracted/ -s image
```

### Issue: Performance Degradation with Large Seeds

**Cause:** PBKDF2 derivation takes time with large strings

**Solution:**
```bash
# Use simpler password-derived seed
python main.py encode secret.txt cover.png output.png \
  -p "password" \
  -s password

# OR pre-compute and use integer seed
SEED=$(python3 -c "from api.scrambler import PixelScrambler; \
  print(PixelScrambler.generate_seed_from_password('mypass'))")
python main.py encode secret.txt cover.png output.png -s $SEED
```

### Issue: Can't Reproduce Decoding

**Cause:** Seed not consistent

**Solution:**
```bash
# Document your seed method exactly
# If using password-derived: same password produces same seed
# If using image-derived: output.png hash must match
# If using integer: seed must match exactly

# Verify reproducibility:
python main.py encode secret.txt cover.png out1.png -s 12345
python main.py decode out1.png ./extract1/ -s 12345

python main.py encode secret.txt cover.png out2.png -s 12345
python main.py decode out2.png ./extract2/ -s 12345

# Both extractions should be identical
diff extract1/secret.txt extract2/secret.txt
```

## Advanced Usage

### Deriving Seeds Programmatically

```python
from api.scrambler import PixelScrambler

# From password
seed1 = PixelScrambler.generate_seed_from_password("mypassword")
print(f"Password-derived seed: {seed1}")

# From image file
seed2 = PixelScrambler.generate_seed_from_image(open("image.png", "rb").read())
print(f"Image-derived seed: {seed2}")

# From combined password and image
seed3 = PixelScrambler.generate_seed_from_combined("mypass", open("image.png", "rb").read())
print(f"Combined seed: {seed3}")
```

### Direct Scrambler Usage

```python
from api.scrambler import PixelScrambler

# Create scrambler for 800x600 image
scrambler = PixelScrambler(width=800, height=600, seed=12345)

# Get shuffled pixel order (pixel coordinates)
pixel_order = scrambler.get_pixel_order()
print(f"First 5 pixels: {pixel_order[:5]}")

# Get shuffled bit positions (x, y, channel)
bit_positions = scrambler.get_bit_positions()
print(f"First 5 bit positions: {bit_positions[:5]}")

# Check total capacity
capacity = scrambler.get_total_capacity()
print(f"Total bits available: {capacity}")
```

### Custom Seed Generation

```python
import hashlib
from random import Random

# Generate seed from multiple inputs
def custom_seed_generator(password, salt, timestamp):
    combined = f"{password}:{salt}:{timestamp}".encode()
    digest = hashlib.sha256(combined).digest()
    return int.from_bytes(digest[:8], byteorder='little') & 0x7FFFFFFF

seed = custom_seed_generator("mypass", "salt123", "2024-01-01")
print(f"Custom seed: {seed}")

# Verify reproducibility
seed_again = custom_seed_generator("mypass", "salt123", "2024-01-01")
assert seed == seed_again, "Reproducibility failed!"
```

## FAQ

### Q: Is scrambling encryption?
**A:** No. Scrambling randomizes the embedding pattern but does NOT encrypt the data itself. Use `-p password` for encryption. For maximum security, use both.

### Q: Can I use the same seed for multiple images?
**A:** Technically yes, but not recommended. Using same seed for different images could allow correlation analysis. Use different seeds or password-derived seeds.

### Q: What if I forget my seed?
**A:** You're locked out. The seed cannot be recovered from the output image. Store seeds securely (password manager, encrypted file).

### Q: How random is the scrambling?
**A:** Pseudo-random and reproducible. Same seed always gives same randomness. Not cryptographically random, but adequate for steganography.

### Q: Does scrambling work with encryption?
**A:** Yes! They're independent:
- Encryption protects content
- Scrambling protects pattern
- Both can be used together for defense-in-depth

### Q: Can steganalysis still detect scrambled data?
**A:** Possibly, but it's much harder:
- Sequential patterns (easy detection) are eliminated
- Statistical anomalies are distributed uniformly
- Advanced ML-based detection might still work
- For real security against determined attackers, use encryption

### Q: How do I know if my secret was found?
**A:** You'll know if:
1. Attacker successfully decodes your message (compromised password/seed)
2. You're approached asking about hidden content
3. Unusual access to your systems

Steganography provides security through obscurity. Encryption provides security through mathematics. Use both.

### Q: Is there a GUI for scrambling?
**A:** Not yet. It's on the TODO list. For now, use CLI commands or write Python scripts.

### Q: Can I use scrambling on other file types?
**A:** Scrambling works on any PNG image. JPEG support is planned. Other formats (BMP, TIFF) would be implementation-dependent.

### Q: What's the overhead of password-derived seeds?
**A:** ~10-50ms per encoding due to PBKDF2 key derivation. Negligible compared to image I/O.

### Q: Can I mix seed types (use password for encoding, image for decoding)?
**A:** No. The seed used for encoding MUST match the seed used for decoding. They must produce identical pixel ordering.
```bash
# This will FAIL:
python main.py encode secret.txt cover.png output.png -s password -p pass
python main.py decode output.png extracted/ -s image  # WRONG SEED!

# This will SUCCEED:
python main.py encode secret.txt cover.png output.png -s password -p pass
python main.py decode output.png extracted/ -s password -p pass  # SAME SEED!
```

### Q: Should I tell people I'm using scrambling?
**A:** No. Steganography security depends on the fact that hidden data is NOT known to exist. Mentioning scrambling reveals that data might be hidden, which defeats the purpose.

### Q: Can you recommend a seed value?
**A:** Use one of these methods:
1. **For reproducible testing:** Integer seeds (e.g., `42`, `12345`)
2. **For real use:** Password-derived seeds with `-s password`
3. **For maximum security:** Different seed per image

Never use predictable seeds in production.

---

## Additional Resources

- [LSB Steganography](https://en.wikipedia.org/wiki/Steganography#LSB_technique)
- [Steganalysis Methods](https://en.wikipedia.org/wiki/Steganalysis)
- [PBKDF2 Key Derivation](https://en.wikipedia.org/wiki/PBKDF2)
- [Pseudo-random Number Generation](https://en.wikipedia.org/wiki/Pseudorandom_number_generator)

---

**Last Updated:** Dec 17 2025
**Version:** 1.0
