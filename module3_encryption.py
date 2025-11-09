"""
AURA Module 3: AES-256-GCM Encryption Helper
Implements military-grade encryption with authentication
Based on MODULE 3 specifications
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import base64

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit encryption key from a password using PBKDF2.
    Uses 100,000 iterations to make brute force attacks extremely slow.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100000,  # 100,000 rounds as specified
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))

def encrypt_data(data: bytes, password: str) -> dict:
    """
    Encrypts data using AES-256-GCM with authentication.
    
    Returns a dictionary containing:
    - ciphertext: The encrypted data
    - nonce: The initialization vector (12 bytes for GCM)
    - tag: Authentication tag (16 bytes)
    - salt: Salt used for key derivation (16 bytes)
    """
    # Generate random salt and nonce
    salt = os.urandom(16)  # 128-bit salt
    nonce = os.urandom(12)  # 96-bit nonce (recommended for GCM)
    
    # Derive encryption key from password
    key = derive_key(password, salt)
    
    # Create AES-256-GCM cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
        backend=default_backend()
    )
    
    # Encrypt the data
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    
    # Get authentication tag
    tag = encryptor.tag
    
    return {
        'ciphertext': ciphertext,
        'nonce': nonce,
        'tag': tag,
        'salt': salt
    }

def decrypt_data(encrypted_payload: dict, password: str) -> bytes:
    """
    Decrypts data using AES-256-GCM and verifies authentication.
    
    Args:
        encrypted_payload: Dictionary from encrypt_data()
        password: The decryption password
        
    Returns:
        The original plaintext data
        
    Raises:
        Exception: If decryption fails (wrong password or tampered data)
    """
    # Extract components
    ciphertext = encrypted_payload['ciphertext']
    nonce = encrypted_payload['nonce']
    tag = encrypted_payload['tag']
    salt = encrypted_payload['salt']
    
    # Derive the same key from password and salt
    key = derive_key(password, salt)
    
    # Create AES-256-GCM cipher for decryption
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    )
    
    # Decrypt and verify authentication
    decryptor = cipher.decryptor()
    try:
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    except Exception as e:
        raise Exception(f"Decryption failed: Authentication verification failed. Wrong password or data tampering detected.") from e

def get_encryption_info() -> dict:
    """
    Returns information about the encryption implementation.
    """
    return {
        'algorithm': 'AES-256-GCM',
        'key_size': 256,
        'mode': 'Galois/Counter Mode',
        'key_derivation': 'PBKDF2-HMAC-SHA256',
        'kdf_iterations': 100000,
        'salt_size': 128,
        'nonce_size': 96,
        'tag_size': 128,
        'security_level': 'Military-grade',
        'features': [
            'Confidentiality (encryption)',
            'Authentication (tamper detection)',
            'Integrity verification',
            'Quantum-resistant (current standards)'
        ]
    }