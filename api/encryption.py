import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2"""
    return PBKDF2(password, salt, dkLen=32, count=100000)


def encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt data with AES-256-CBC using password-derived key"""
    salt = os.urandom(16)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC)
    
    iv = cipher.iv
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    
    # Return salt + iv + encrypted_data
    return salt + iv + encrypted_data


def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """Decrypt AES-256-CBC data using password-derived key"""
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    try:
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted_data
    except ValueError:
        raise ValueError("Invalid password or corrupted data")