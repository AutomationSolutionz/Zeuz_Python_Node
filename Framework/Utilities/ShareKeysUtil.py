"""
Utilities for sharing and fetching RSA private keys with encryption.

This module provides functions to:
- Generate secure share codes in format AkEf-B910 (avoiding confusing characters)
- Encrypt/decrypt private keys using the share code
- Send/receive encrypted keys to/from server
"""

import secrets
import base64
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


# Character set avoiding confusing characters: 0/O, 1/I/l
SAFE_CHARS = "23456789ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz"


def generate_share_code() -> str:
    """
    Generate a secure 9-character share code in format XXXX-XXXX.
    Avoids confusing characters like 0/O, 1/I/l.
    
    Returns:
        A string in format like "AkEf-B910"
    """
    # Generate 8 random characters from safe set
    code_chars = ''.join(secrets.choice(SAFE_CHARS) for _ in range(8))
    # Format as XXXX-XXXX
    return f"{code_chars[:4]}-{code_chars[4:]}"


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from the share code using PBKDF2.
    
    Args:
        password: The share code
        salt: Random salt for key derivation
        
    Returns:
        32-byte encryption key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt_data(data: str, password: str) -> str:
    """
    Encrypt data using AES-256-GCM with the share code as password.
    
    Args:
        data: The data to encrypt
        password: The share code
        
    Returns:
        Base64-encoded encrypted data with salt and nonce
    """
    # Generate random salt and nonce
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    
    # Derive encryption key
    key = derive_key(password, salt)
    
    # Encrypt using AES-256-GCM
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    
    # Combine salt, nonce, tag, and ciphertext
    encrypted_blob = salt + nonce + encryptor.tag + ciphertext
    
    # Encode as base64
    return base64.b64encode(encrypted_blob).decode('utf-8')


def decrypt_data(encrypted_b64: str, password: str) -> Optional[str]:
    """
    Decrypt data using AES-256-GCM with the share code as password.
    
    Args:
        encrypted_b64: Base64-encoded encrypted data
        password: The share code
        
    Returns:
        Decrypted data string, or None if decryption fails
    """
    try:
        # Decode from base64
        encrypted_blob = base64.b64decode(encrypted_b64)
        
        # Extract components
        salt = encrypted_blob[:16]
        nonce = encrypted_blob[16:28]
        tag = encrypted_blob[28:44]
        ciphertext = encrypted_blob[44:]
        
        # Derive decryption key
        key = derive_key(password, salt)
        
        # Decrypt using AES-256-GCM
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None


def collect_private_keys(key_folder: Path) -> List[Dict[str, str]]:
    """
    Collect all RSA private keys from the specified folder.
    
    Args:
        key_folder: Path to the folder containing .pem files
        
    Returns:
        List of dictionaries with 'filename' and 'content' keys
    """
    if not key_folder.exists():
        return []
    
    keys = []
    for pem_file in key_folder.glob("*.pem"):
        try:
            with open(pem_file, 'r') as f:
                content = f.read()
            keys.append({
                'filename': pem_file.name,
                'content': content
            })
        except Exception as e:
            print(f"Warning: Could not read {pem_file.name}: {e}")
    
    return keys


def save_private_keys(keys: List[Dict[str, str]], key_folder: Path) -> Tuple[int, int, int]:
    """
    Save private keys to the specified folder, checking for duplicates.
    
    Args:
        keys: List of dictionaries with 'filename' and 'content' keys
        key_folder: Path to the folder to save keys
        
    Returns:
        Tuple of (successful_count, skipped_count, failed_count)
    """
    from cryptography.hazmat.primitives import serialization
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    # Import the RSA utility for duplicate checking and saving
    try:
        from . import RSAKeyUtil
    except ImportError:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        import RSAKeyUtil
    
    for key_info in keys:
        try:
            filename = key_info['filename']
            content = key_info['content']
            
            # Load the private key from PEM content
            private_key = RSAKeyUtil.load_private_key_from_pem(content)
            if private_key is None:
                print(f"Warning: {filename} is not a valid RSA private key, skipping")
                failed_count += 1
                continue
            
            # Use the existing save_private_key utility which handles duplicates
            success, duplicate_filename, saved_path = RSAKeyUtil.save_private_key(
                private_key=private_key,
                key_folder=key_folder,
                filename=filename,
                format_type="pkcs8",
                check_duplicate=True
            )
            
            if success:
                success_count += 1
            elif duplicate_filename:
                print(f"Skipping {filename}: duplicate of existing key {duplicate_filename}")
                skipped_count += 1
            else:
                failed_count += 1
            
        except Exception as e:
            print(f"Warning: Could not save {key_info.get('filename', 'unknown')}: {e}")
            failed_count += 1
    
    return success_count, skipped_count, failed_count
