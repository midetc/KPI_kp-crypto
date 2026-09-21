UA = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
EN = "abcdefghijklmnopqrstuvwxyz"
BYTE_N = 256


class Alphabet:
    def __init__(self, letters: str):
        self.letters = letters
        self.n = len(letters)
        self.index = {ch: i for i, ch in enumerate(letters)}

    def has(self, ch: str) -> bool:
        return ch.lower() in self.index


UA_ALPHABET = Alphabet(UA)
EN_ALPHABET = Alphabet(EN)


def pick_alphabet(text: str) -> Alphabet:
    for ch in text:
        if ch.lower() in UA_ALPHABET.index:
            return UA_ALPHABET
        if ch.lower() in EN_ALPHABET.index:
            return EN_ALPHABET
    return UA_ALPHABET


class CaesarCipher:
    def validate_key(self, key) -> int:
        try:
            return int(key)
        except (TypeError, ValueError) as exc:
            raise ValueError("key") from exc

    def validate_data(self, data) -> str:
        if data is None:
            raise ValueError("data")
        text = data if isinstance(data, str) else data.decode("utf-8", errors="replace")
        if text == "":
            raise ValueError("data")
        return text

    def _shift_char(self, ch: str, shift: int, alphabet: Alphabet) -> str:
        lower = ch.lower()
        if lower not in alphabet.index:
            return ch
        pos = (alphabet.index[lower] + shift) % alphabet.n
        out = alphabet.letters[pos]
        return out.upper() if ch.isupper() else out

    def encrypt(self, data, key, alphabet: Alphabet | None = None) -> str:
        text = self.validate_data(data)
        k = self.validate_key(key)
        ab = alphabet or pick_alphabet(text)
        return "".join(self._shift_char(ch, k, ab) for ch in text)

    def decrypt(self, data, key, alphabet: Alphabet | None = None) -> str:
        text = self.validate_data(data)
        k = self.validate_key(key)
        ab = alphabet or pick_alphabet(text)
        return "".join(self._shift_char(ch, -k, ab) for ch in text)

    def encrypt_bytes(self, data: bytes, key) -> bytes:
        k = self.validate_key(key) % BYTE_N
        return bytes((b + k) % BYTE_N for b in data)

    def decrypt_bytes(self, data: bytes, key) -> bytes:
        k = self.validate_key(key) % BYTE_N
        return bytes((b - k) % BYTE_N for b in data)


class BruteForceAttack:
    def __init__(self):
        self.caesar = CaesarCipher()

    def run(self, cipher_text: str, alphabet: Alphabet | None = None):
        text = self.caesar.validate_data(cipher_text)
        ab = alphabet or pick_alphabet(text)
        return [(k, self.caesar.decrypt(text, k, ab)) for k in range(ab.n)]
