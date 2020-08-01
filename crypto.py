import base64
import os
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password_bytes: bytes, salt_bytes:bytes):
    kdf = PBKDF2HMAC(
      algorithm=hashes.SHA256(),
      length=32,
      salt=salt_bytes,
      iterations=100000,
      backend=default_backend()
    )
    key = kdf.derive(password_bytes)
    return key

def encrypt(key, plaintext_bytes, associated_data):
    # Generate a random 96-bit IV.
    iv = os.urandom(12)

    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()

    ciphertext = base64.urlsafe_b64encode(ciphertext)

    return (iv, ciphertext, encryptor.tag)

def decrypt(key, associated_data, iv, ciphertext, tag):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    decryptor.authenticate_additional_data(associated_data)

    ciphertext = base64.urlsafe_b64decode(ciphertext)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return decryptor.update(ciphertext) + decryptor.finalize()

associated_data = bytes(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], 'utf-8')
# salt = b"1U\xe2\xf1\xec\xc9\xeef\xbe8\xd8\x00`<\xd8b\xa2\xb5v\x82\xd0U\xf01zP3\xf5\xb3\x12\x98\xcb"
salt = os.urandom(32)
password = b"this is my password"
key = derive_key(password, salt)
plain_text = b"a secret message!"

iv, ciphertext, tag = encrypt(
    key,
    plain_text,
    associated_data
)

print(decrypt(
    key,
    associated_data,
    iv,
    ciphertext,
    tag
))