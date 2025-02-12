from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import json

class Encrypt:
    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key

    @staticmethod
    def encrypt(data: dict, password: str) -> str:
        salt = os.urandom(16)
        key = Encrypt.generate_key(password, salt)
        iv = os.urandom(16)
        
        # Serialize JSON to bytes
        json_data = json.dumps(data).encode('utf-8')
        
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        return base64.b64encode(salt + iv + encrypted_data).decode('utf-8')


class decrypt:
    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key

    @staticmethod
    def decryption(encrypted_data: str, password: str) -> dict:
        encrypted_data = base64.b64decode(encrypted_data)
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        encrypted_data = encrypted_data[32:]

        key = decrypt.generate_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        # Deserialize bytes back to JSON
        json_data = json.loads(data.decode('utf-8'))
        return json_data
    def inData(AESCypher):
        DecryptedData = decrypt.decryption(AESCypher, 'MycardiumAI')
        return DecryptedData