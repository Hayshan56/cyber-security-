import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Storage:
    def __init__(self, master_password, filepath='passwords.json.encrypted'):
        self.filepath = filepath
        self.master_password = master_password

    def _derive_key(self, password: str, salt: bytes):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def save(self, data):
        salt = os.urandom(16)
        key = self._derive_key(self.master_password, salt)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        with open(self.filepath, 'wb') as f:
            f.write(salt + encrypted_data)

    def load(self):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath, 'rb') as f:
            file_content = f.read()

        if len(file_content) < 16:
            return None

        salt = file_content[:16]
        encrypted_data = file_content[16:]

        key = self._derive_key(self.master_password, salt)
        fernet = Fernet(key)

        try:
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except InvalidToken:
            return None
