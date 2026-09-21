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
            value = int(key)
        except (TypeError, ValueError) as exc:
            raise ValueError("key") from exc
        return value

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


class TrithemiusCipher:
    def validate_key(self, mode: str, key):
        if mode == "motto":
            motto = str(key).strip()
            if not motto:
                raise ValueError("key")
            return motto
        parts = [p.strip() for p in str(key).replace(";", ",").split(",")]
        need = 2 if mode == "linear" else 3
        if len(parts) != need:
            raise ValueError("key")
        try:
            return [int(p) for p in parts]
        except ValueError as exc:
            raise ValueError("key") from exc

    def validate_data(self, data) -> str:
        if data is None:
            raise ValueError("data")
        text = data if isinstance(data, str) else data.decode("utf-8", errors="replace")
        if text == "":
            raise ValueError("data")
        return text

    def _shifts(self, mode: str, key, length: int, alphabet: Alphabet) -> list[int]:
        if mode == "linear":
            a, b = key
            return [(a * p + b) % alphabet.n for p in range(length)]
        if mode == "nonlinear":
            a, b, c = key
            return [(a * p * p + b * p + c) % alphabet.n for p in range(length)]
        motto = key
        stream = []
        i = 0
        while len(stream) < length:
            ch = motto[i % len(motto)].lower()
            if ch in alphabet.index:
                stream.append(alphabet.index[ch])
            i += 1
            if i > length * max(len(motto), 1) + 50:
                raise ValueError("key")
        return stream

    def _shift_char(self, ch: str, shift: int, alphabet: Alphabet) -> str:
        lower = ch.lower()
        if lower not in alphabet.index:
            return ch
        pos = (alphabet.index[lower] + shift) % alphabet.n
        out = alphabet.letters[pos]
        return out.upper() if ch.isupper() else out

    def encrypt(self, data, mode: str, key, alphabet: Alphabet | None = None) -> str:
        text = self.validate_data(data)
        parsed = self.validate_key(mode, key)
        ab = alphabet or pick_alphabet(text)
        letter_pos = [i for i, ch in enumerate(text) if ab.has(ch)]
        shifts = self._shifts(mode, parsed, len(letter_pos), ab)
        shift_at = {pos: shifts[i] for i, pos in enumerate(letter_pos)}
        return "".join(
            self._shift_char(ch, shift_at[i], ab) if i in shift_at else ch
            for i, ch in enumerate(text)
        )

    def decrypt(self, data, mode: str, key, alphabet: Alphabet | None = None) -> str:
        text = self.validate_data(data)
        parsed = self.validate_key(mode, key)
        ab = alphabet or pick_alphabet(text)
        letter_pos = [i for i, ch in enumerate(text) if ab.has(ch)]
        shifts = self._shifts(mode, parsed, len(letter_pos), ab)
        shift_at = {pos: -shifts[i] for i, pos in enumerate(letter_pos)}
        return "".join(
            self._shift_char(ch, shift_at[i], ab) if i in shift_at else ch
            for i, ch in enumerate(text)
        )

    def encrypt_bytes(self, data: bytes, mode: str, key) -> bytes:
        parsed = self.validate_key(mode, key)
        fake = Alphabet("".join(chr(i) for i in range(BYTE_N)))
        if mode == "motto":
            shifts = [(ord(parsed[i % len(parsed)]) % BYTE_N) for i in range(len(data))]
        elif mode == "linear":
            a, b = parsed
            shifts = [(a * p + b) % BYTE_N for p in range(len(data))]
        else:
            a, b, c = parsed
            shifts = [(a * p * p + b * p + c) % BYTE_N for p in range(len(data))]
        return bytes((data[i] + shifts[i]) % BYTE_N for i in range(len(data)))

    def decrypt_bytes(self, data: bytes, mode: str, key) -> bytes:
        parsed = self.validate_key(mode, key)
        if mode == "motto":
            shifts = [(ord(parsed[i % len(parsed)]) % BYTE_N) for i in range(len(data))]
        elif mode == "linear":
            a, b = parsed
            shifts = [(a * p + b) % BYTE_N for p in range(len(data))]
        else:
            a, b, c = parsed
            shifts = [(a * p * p + b * p + c) % BYTE_N for p in range(len(data))]
        return bytes((data[i] - shifts[i]) % BYTE_N for i in range(len(data)))


class BruteForceAttack:
    def __init__(self):
        self.caesar = CaesarCipher()

    def run(self, cipher_text: str, alphabet: Alphabet | None = None) -> list[tuple[int, str]]:
        text = self.caesar.validate_data(cipher_text)
        ab = alphabet or pick_alphabet(text)
        return [(k, self.caesar.decrypt(text, k, ab)) for k in range(ab.n)]


class KnownPlaintextAttack:
    def recover(self, plain: str, cipher: str, mode: str, alphabet: Alphabet | None = None):
        if len(plain) != len(cipher):
            raise ValueError("data")
        ab = alphabet or pick_alphabet(plain + cipher)
        deltas = []
        for p_ch, c_ch in zip(plain, cipher):
            if not (ab.has(p_ch) and ab.has(c_ch)):
                continue
            px = ab.index[p_ch.lower()]
            cx = ab.index[c_ch.lower()]
            deltas.append((cx - px) % ab.n)
        if mode == "motto":
            if not deltas:
                raise ValueError("data")
            return "".join(ab.letters[d] for d in deltas)
        if mode == "linear":
            if len(deltas) < 2:
                raise ValueError("data")
            for a in range(ab.n):
                b = (deltas[0] - a * 0) % ab.n
                if all(deltas[p] == (a * p + b) % ab.n for p in range(len(deltas))):
                    return [a, b]
            raise ValueError("key")
        if len(deltas) < 3:
            raise ValueError("data")
        for a in range(ab.n):
            for b in range(ab.n):
                c = (deltas[0] - a * 0 - b * 0) % ab.n
                ok = True
                for p, d in enumerate(deltas):
                    if d != (a * p * p + b * p + c) % ab.n:
                        ok = False
                        break
                if ok:
                    return [a, b, c]
        raise ValueError("key")
