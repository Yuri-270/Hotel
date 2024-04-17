from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64


__all__ = [
    'Cryptograthic'
]


class Cryptograthic:

    @classmethod
    async def encrypt(cls, data: bytes, key: str):
        key = bytes(key, 'utf-8')
        iv = b'\x00' * 16

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return base64.b64encode(ciphertext)

    @classmethod
    async def decrypt(cls, ciphertext: str, key: str):
        key = bytes(key, 'utf-8')

        ciphertext = base64.b64decode(ciphertext)
        cipher = Cipher(algorithms.AES(key), modes.CBC(b'\x00' * 16), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data.decode()
