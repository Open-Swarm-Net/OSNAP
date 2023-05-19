from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)
import rsa


class SignatureUtil:
    @staticmethod
    def generate_key_pair():
        (public_key, private_key) = rsa.new_keys(512, poolsize=8)
        private_pem = private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        )
        public_pem = private_key.public_key().public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )
        return private_pem, public_pem

    @staticmethod
    def sign_data(private_key_pem, data):
        private_key = serialization.load_pem_private_key(private_key_pem, None)
        signature = private_key.sign(data.encode(), padding.PKCS1v15(), hashes.SHA256())
        return signature

    @staticmethod
    def verify_signature(public_key_pem, data, signature):
        public_key = serialization.load_pem_public_key(public_key_pem)
        try:
            public_key.verify(
                signature, data.encode(), padding.PKCS1v15(), hashes.SHA256()
            )
            return True
        except Exception as e:
            return False
