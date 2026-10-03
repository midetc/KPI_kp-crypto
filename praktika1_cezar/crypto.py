UA = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
EN = "abcdefghijklmnopqrstuvwxyz"


class Alphabet:
    def __init__(self, letters):
        self.letters = letters
        self.n = len(letters)
        self.index = {}
        i = 0
        while i < len(letters):
            self.index[letters[i]] = i
            i += 1


UA_ALPHABET = Alphabet(UA)
EN_ALPHABET = Alphabet(EN)


def pick_alphabet(text):
    for ch in text:
        low = ch.lower()
        if low in UA_ALPHABET.index:
            return UA_ALPHABET
        if low in EN_ALPHABET.index:
            return EN_ALPHABET
    return UA_ALPHABET


class CaesarCipher:
    def validate_key(self, key):
        try:
            return int(key)
        except Exception:
            raise ValueError("key")

    def validate_data(self, data):
        if data is None:
            raise ValueError("data")
        if isinstance(data, bytes):
            text = data.decode("utf-8", errors="replace")
        else:
            text = data
        if text == "":
            raise ValueError("data")
        return text

    def shift_char(self, ch, shift, alphabet):
        low = ch.lower()
        if low not in alphabet.index:
            return ch
        pos = (alphabet.index[low] + shift) % alphabet.n
        out = alphabet.letters[pos]
        if ch.isupper():
            return out.upper()
        return out

    def encrypt(self, data, key, alphabet=None):
        text = self.validate_data(data)
        k = self.validate_key(key)
        if alphabet is None:
            alphabet = pick_alphabet(text)
        result = ""
        for ch in text:
            result += self.shift_char(ch, k, alphabet)
        return result

    def decrypt(self, data, key, alphabet=None):
        text = self.validate_data(data)
        k = self.validate_key(key)
        if alphabet is None:
            alphabet = pick_alphabet(text)
        result = ""
        for ch in text:
            result += self.shift_char(ch, -k, alphabet)
        return result

    def encrypt_bytes(self, data, key):
        k = self.validate_key(key) % 256
        out = bytearray()
        for b in data:
            out.append((b + k) % 256)
        return bytes(out)

    def decrypt_bytes(self, data, key):
        k = self.validate_key(key) % 256
        out = bytearray()
        for b in data:
            out.append((b - k) % 256)
        return bytes(out)


class BruteForceAttack:
    def __init__(self):
        self.caesar = CaesarCipher()

    def run(self, cipher_text, alphabet=None):
        text = self.caesar.validate_data(cipher_text)
        if alphabet is None:
            alphabet = pick_alphabet(text)
        rows = []
        k = 0
        while k < alphabet.n:
            rows.append((k, self.caesar.decrypt(text, k, alphabet)))
            k += 1
        return rows
