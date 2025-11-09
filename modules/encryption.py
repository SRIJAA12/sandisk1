# modules/encryption.py
"""
AES-256-GCM Encryption Module
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import hashlib
import base64


class AESEncryption:
    """Handle AES-256-GCM encryption and decryption"""
    
    def __init__(self, password: str):
        self.password = password
        self.key = self._derive_key(password)
    
    def _derive_key(self, password: str, salt: bytes = None) -> tuple:
        """Derive a 256-bit key from password using PBKDF2"""
        if salt is None:
            salt = get_random_bytes(16)
        
        key = PBKDF2(password, salt, dkLen=32, count=100000)
        return key, salt
    
    def encrypt(self, data: bytes) -> dict:
        """
        Encrypt data using AES-256-GCM
        
        Returns dict with: nonce, tag, ciphertext, salt
        """
        key, salt = self._derive_key(self.password)
        
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        return {
            'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }
    
    def decrypt(self, encrypted_dict: dict) -> bytes:
        """Decrypt data using AES-256-GCM"""
        nonce = base64.b64decode(encrypted_dict['nonce'])
        tag = base64.b64decode(encrypted_dict['tag'])
        ciphertext = base64.b64decode(encrypted_dict['ciphertext'])
        salt = base64.b64decode(encrypted_dict['salt'])
        
        key = PBKDF2(self.password, salt, dkLen=32, count=100000)
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        return plaintext
    
    def get_encryption_details(self) -> dict:
        """Return encryption algorithm details"""
        return {
            'algorithm': 'AES-256-GCM',
            'key_size': '256 bits',
            'mode': 'Galois/Counter Mode',
            'key_derivation': 'PBKDF2',
            'iterations': '100,000',
            'salt_size': '128 bits',
            'security_level': 'Military Grade'
        }
