"""
RSA Key Utility Module

Provides utilities for managing RSA private keys used for encrypting secrets.
Functions include:
- Loading private keys from PEM format
- Saving private keys with duplicate detection
- Getting public keys from private keys
- Listing existing keys in a folder
- Checking for duplicate keys
"""

from pathlib import Path
from typing import Optional, Tuple, List, Dict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def load_private_key_from_pem(pem_content: str) -> Optional[rsa.RSAPrivateKey]:
    """
    Load an RSA private key from PEM format content.
    
    Args:
        pem_content: String containing the PEM-encoded private key
        
    Returns:
        RSAPrivateKey object if successful, None otherwise
    """
    try:
        private_key = serialization.load_pem_private_key(
            pem_content.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        # Verify it's an RSA key
        if not isinstance(private_key, rsa.RSAPrivateKey):
            return None
        return private_key
    except Exception as e:
        print(f"Error loading private key from PEM: {e}")
        return None


def get_public_key_pem(private_key: rsa.RSAPrivateKey) -> str:
    """
    Extract the public key from a private key and return it as PEM string.
    
    Args:
        private_key: RSAPrivateKey object
        
    Returns:
        PEM-encoded public key as string
    """
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    return public_key_pem


def check_duplicate_key(new_private_key: rsa.RSAPrivateKey, key_folder: Path) -> Optional[str]:
    """
    Check if a private key already exists in the folder by comparing public keys.
    
    Args:
        new_private_key: The private key to check
        key_folder: Path to the folder containing existing keys
        
    Returns:
        Filename of the duplicate key if found, None otherwise
    """
    if not key_folder.exists():
        return None
    
    new_public_key_pem = get_public_key_pem(new_private_key)
    
    pem_files = list(key_folder.glob("*.pem"))
    for pem_file in pem_files:
        try:
            with open(pem_file, 'rb') as f:
                existing_private_key = serialization.load_pem_private_key(
                    f.read(), 
                    password=None,
                    backend=default_backend()
                )
            # Verify it's an RSA key
            if not isinstance(existing_private_key, rsa.RSAPrivateKey):
                continue
            existing_public_key_pem = get_public_key_pem(existing_private_key)
            
            if existing_public_key_pem == new_public_key_pem:
                return pem_file.name
        except Exception as e:
            print(f"Warning: Could not check key {pem_file.name}: {e}")
            continue
    
    return None


def save_private_key(
    private_key: rsa.RSAPrivateKey,
    key_folder: Path,
    filename: str,
    format_type: str = "pkcs8",
    check_duplicate: bool = True
) -> Tuple[bool, Optional[str], Optional[Path]]:
    """
    Save an RSA private key to a file with optional duplicate checking.
    
    Args:
        private_key: The RSAPrivateKey object to save
        key_folder: Path to the folder where the key should be saved
        filename: Name of the file (should end in .pem)
        format_type: Format for saving ("pkcs8" or "traditional_openssl")
        check_duplicate: Whether to check for duplicate keys before saving
        
    Returns:
        Tuple of (success: bool, duplicate_filename: Optional[str], saved_path: Optional[Path])
        - If successful: (True, None, path_to_saved_file)
        - If duplicate found: (False, duplicate_filename, None)
        - If error: (False, None, None)
    """
    try:
        # Ensure the folder exists
        key_folder.mkdir(parents=True, exist_ok=True)
        
        # Check for duplicates if requested
        if check_duplicate:
            duplicate = check_duplicate_key(private_key, key_folder)
            if duplicate:
                return False, duplicate, None
        
        # Determine the format
        if format_type == "pkcs8":
            format_obj = serialization.PrivateFormat.PKCS8
        elif format_type == "traditional_openssl":
            format_obj = serialization.PrivateFormat.TraditionalOpenSSL
        else:
            print(f"Warning: Unknown format type '{format_type}', using PKCS8")
            format_obj = serialization.PrivateFormat.PKCS8
        
        # Save the private key
        key_path = key_folder / filename
        with open(key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=format_obj,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return True, None, key_path
        
    except Exception as e:
        print(f"Error saving private key: {e}")
        return False, None, None


def list_existing_keys(key_folder: Path) -> List[Dict[str, str]]:
    """
    List all existing RSA private keys in a folder and extract their public keys.
    
    Args:
        key_folder: Path to the folder containing .pem files
        
    Returns:
        List of dictionaries with keys:
        - 'filename': Name of the key file
        - 'path': Full path to the key file
        - 'public_key': PEM-encoded public key (if successfully loaded)
        - 'error': Error message (if failed to load)
    """
    if not key_folder.exists():
        return []
    
    keys_info = []
    pem_files = sorted(key_folder.glob("*.pem"))
    
    for pem_file in pem_files:
        key_info = {
            'filename': pem_file.name,
            'path': str(pem_file)
        }
        
        try:
            with open(pem_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # Verify it's an RSA key
            if not isinstance(private_key, rsa.RSAPrivateKey):
                key_info['error'] = "Not an RSA private key"
                keys_info.append(key_info)
                continue
            
            # Extract public key
            public_key_pem = get_public_key_pem(private_key)
            key_info['public_key'] = public_key_pem
            
        except Exception as e:
            key_info['error'] = str(e)
        
        keys_info.append(key_info)
    
    return keys_info
