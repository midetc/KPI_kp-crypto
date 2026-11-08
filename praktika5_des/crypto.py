from Crypto.Cipher import AES, DES, DES3

from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


ALGOS = ["DES", "TripleDES", "AES"]
MODES = ["ECB", "CBC", "CFB", "OFB"]


class SymCipher:
    def key_size(self, algo):
        if algo == "DES":
            return 8
        if algo == "TripleDES":
            return 24
        return 16

    def block_size(self, algo):
        if algo == "AES":
            return 16
        return 8

    def fix_bytes(self, text, n):
        b = text.encode("utf-8", errors="ignore")
        if len(b) < n:
            b = b + (b"0" * (n - len(b)))
        return b[:n]

    def make_cipher(self, algo, mode, key, iv):
        if algo == "DES":
            if mode == "ECB":
                return DES.new(key, DES.MODE_ECB)
            if mode == "CBC":
                return DES.new(key, DES.MODE_CBC, iv)
            if mode == "CFB":
                return DES.new(key, DES.MODE_CFB, iv)
            return DES.new(key, DES.MODE_OFB, iv)
        if algo == "TripleDES":
            if mode == "ECB":
                return DES3.new(key, DES3.MODE_ECB)
            if mode == "CBC":
                return DES3.new(key, DES3.MODE_CBC, iv)
            if mode == "CFB":
                return DES3.new(key, DES3.MODE_CFB, iv)
            return DES3.new(key, DES3.MODE_OFB, iv)
        if mode == "ECB":
            return AES.new(key, AES.MODE_ECB)
        if mode == "CBC":
            return AES.new(key, AES.MODE_CBC, iv)
        if mode == "CFB":
            return AES.new(key, AES.MODE_CFB, iv)
        return AES.new(key, AES.MODE_OFB, iv)

    def encrypt_bytes(self, data, algo, mode, key_text, iv_text):
        if algo not in ALGOS or mode not in MODES:
            raise ValueError("bad")
        key = self.fix_bytes(key_text, self.key_size(algo))
        iv = None
        if mode != "ECB":
            iv = self.fix_bytes(iv_text, self.block_size(algo))
        c = self.make_cipher(algo, mode, key, iv)
        if mode == "ECB" or mode == "CBC":
            return c.encrypt(pad(data, self.block_size(algo)))
        return c.encrypt(data)

    def decrypt_bytes(self, data, algo, mode, key_text, iv_text):
        if algo not in ALGOS or mode not in MODES:
            raise ValueError("bad")
        key = self.fix_bytes(key_text, self.key_size(algo))
        iv = None
        if mode != "ECB":
            iv = self.fix_bytes(iv_text, self.block_size(algo))
        c = self.make_cipher(algo, mode, key, iv)
        if mode == "ECB" or mode == "CBC":
            return unpad(c.decrypt(data), self.block_size(algo))
        return c.decrypt(data)

    def encrypt_text(self, text, algo, mode, key_text, iv_text):
        if text is None or text == "":
            raise ValueError("data")
        enc = self.encrypt_bytes(text.encode("utf-8"), algo, mode, key_text, iv_text)
        return enc.hex()

    def decrypt_text(self, hex_text, algo, mode, key_text, iv_text):
        if hex_text is None or hex_text.strip() == "":
            raise ValueError("data")
        raw = bytes.fromhex(hex_text.strip().replace(" ", ""))
        dec = self.decrypt_bytes(raw, algo, mode, key_text, iv_text)
        return dec.decode("utf-8", errors="replace")
