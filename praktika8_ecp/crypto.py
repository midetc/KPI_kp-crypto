from Crypto.Hash import SHA1
from Crypto.PublicKey import DSA, RSA
from Crypto.Signature import DSS, pkcs1_15


class RsaSign:
    def __init__(self):
        self.private_pem = ""
        self.public_pem = ""

    def generate(self, bits=1024):
        if bits < 1024:
            bits = 1024
        key = RSA.generate(bits)
        self.private_pem = key.export_key().decode("utf-8")
        self.public_pem = key.publickey().export_key().decode("utf-8")
        return self.public_pem, self.private_pem

    def hash_hex(self, text):
        if text is None:
            raise ValueError("data")
        h = SHA1.new(text.encode("utf-8"))
        return h.hexdigest()

    def sign(self, text, private_pem):
        if text is None or text == "":
            raise ValueError("data")
        if private_pem is None or private_pem.strip() == "":
            raise ValueError("key")
        key = RSA.import_key(private_pem)
        h = SHA1.new(text.encode("utf-8"))
        sig = pkcs1_15.new(key).sign(h)
        return sig.hex()

    def verify(self, text, signature_hex, public_pem):
        if text is None or text == "":
            raise ValueError("data")
        if public_pem is None or public_pem.strip() == "":
            raise ValueError("key")
        key = RSA.import_key(public_pem)
        h = SHA1.new(text.encode("utf-8"))
        raw = bytes.fromhex(signature_hex.strip().replace(" ", ""))
        try:
            pkcs1_15.new(key).verify(h, raw)
            return True
        except (ValueError, TypeError):
            return False


class DsaSign:
    def __init__(self):
        self.private_pem = ""
        self.public_pem = ""

    def generate(self, bits=1024):
        if bits < 1024:
            bits = 1024
        key = DSA.generate(bits)
        self.private_pem = key.export_key().decode("utf-8")
        self.public_pem = key.publickey().export_key().decode("utf-8")
        return self.public_pem, self.private_pem

    def sign(self, text, private_pem):
        if text is None or text == "":
            raise ValueError("data")
        key = DSA.import_key(private_pem)
        h = SHA1.new(text.encode("utf-8"))
        signer = DSS.new(key, "fips-186-3")
        sig = signer.sign(h)
        return sig.hex()

    def verify(self, text, signature_hex, public_pem):
        if text is None or text == "":
            raise ValueError("data")
        key = DSA.import_key(public_pem)
        h = SHA1.new(text.encode("utf-8"))
        raw = bytes.fromhex(signature_hex.strip().replace(" ", ""))
        verifier = DSS.new(key, "fips-186-3")
        try:
            verifier.verify(h, raw)
            return True
        except ValueError:
            return False
