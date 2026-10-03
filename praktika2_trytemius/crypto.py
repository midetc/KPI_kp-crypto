UA = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
EN = "abcdefghijklmnopqrstuvwxyz"


class Alphabet:
    def __init__(self, letters):
        self.letters = letters
        self.n = len(letters)
        self.index = {}
        for i in range(len(letters)):
            self.index[letters[i]] = i

    def has(self, ch):
        return ch.lower() in self.index


UA_ALPHABET = Alphabet(UA)
EN_ALPHABET = Alphabet(EN)


def pick_alphabet(text):
    for ch in text:
        if ch.lower() in UA_ALPHABET.index:
            return UA_ALPHABET
        if ch.lower() in EN_ALPHABET.index:
            return EN_ALPHABET
    return UA_ALPHABET


class TrithemiusCipher:
    def validate_key(self, mode, key):
        if mode == "motto":
            s = str(key).strip()
            if s == "":
                raise ValueError("key")
            return s
        parts = str(key).replace(";", ",").split(",")
        parts = [p.strip() for p in parts]
        need = 2 if mode == "linear" else 3
        if len(parts) != need:
            raise ValueError("key")
        nums = []
        for p in parts:
            nums.append(int(p))
        return nums

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

    def make_shifts(self, mode, key, length, alphabet):
        shifts = []
        if mode == "linear":
            a = key[0]
            b = key[1]
            p = 0
            while p < length:
                shifts.append((a * p + b) % alphabet.n)
                p += 1
        elif mode == "nonlinear":
            a = key[0]
            b = key[1]
            c = key[2]
            p = 0
            while p < length:
                shifts.append((a * p * p + b * p + c) % alphabet.n)
                p += 1
        else:
            i = 0
            while len(shifts) < length:
                ch = key[i % len(key)].lower()
                if ch in alphabet.index:
                    shifts.append(alphabet.index[ch])
                i += 1
                if i > 5000:
                    raise ValueError("key")
        return shifts

    def shift_char(self, ch, shift, alphabet):
        low = ch.lower()
        if low not in alphabet.index:
            return ch
        pos = (alphabet.index[low] + shift) % alphabet.n
        out = alphabet.letters[pos]
        if ch.isupper():
            return out.upper()
        return out

    def encrypt(self, data, mode, key, alphabet=None):
        text = self.validate_data(data)
        parsed = self.validate_key(mode, key)
        if alphabet is None:
            alphabet = pick_alphabet(text)
        letter_pos = []
        i = 0
        while i < len(text):
            if alphabet.has(text[i]):
                letter_pos.append(i)
            i += 1
        shifts = self.make_shifts(mode, parsed, len(letter_pos), alphabet)
        result = ""
        si = 0
        i = 0
        while i < len(text):
            if alphabet.has(text[i]):
                result += self.shift_char(text[i], shifts[si], alphabet)
                si += 1
            else:
                result += text[i]
            i += 1
        return result

    def decrypt(self, data, mode, key, alphabet=None):
        text = self.validate_data(data)
        parsed = self.validate_key(mode, key)
        if alphabet is None:
            alphabet = pick_alphabet(text)
        letter_pos = []
        i = 0
        while i < len(text):
            if alphabet.has(text[i]):
                letter_pos.append(i)
            i += 1
        shifts = self.make_shifts(mode, parsed, len(letter_pos), alphabet)
        result = ""
        si = 0
        i = 0
        while i < len(text):
            if alphabet.has(text[i]):
                result += self.shift_char(text[i], -shifts[si], alphabet)
                si += 1
            else:
                result += text[i]
            i += 1
        return result

    def encrypt_bytes(self, data, mode, key):
        parsed = self.validate_key(mode, key)
        out = bytearray()
        i = 0
        while i < len(data):
            if mode == "motto":
                sh = ord(parsed[i % len(parsed)]) % 256
            elif mode == "linear":
                sh = (parsed[0] * i + parsed[1]) % 256
            else:
                sh = (parsed[0] * i * i + parsed[1] * i + parsed[2]) % 256
            out.append((data[i] + sh) % 256)
            i += 1
        return bytes(out)

    def decrypt_bytes(self, data, mode, key):
        parsed = self.validate_key(mode, key)
        out = bytearray()
        i = 0
        while i < len(data):
            if mode == "motto":
                sh = ord(parsed[i % len(parsed)]) % 256
            elif mode == "linear":
                sh = (parsed[0] * i + parsed[1]) % 256
            else:
                sh = (parsed[0] * i * i + parsed[1] * i + parsed[2]) % 256
            out.append((data[i] - sh) % 256)
            i += 1
        return bytes(out)


class KnownPlaintextAttack:
    def recover(self, plain, cipher, mode, alphabet=None):
        if len(plain) != len(cipher):
            raise ValueError("data")
        if alphabet is None:
            alphabet = pick_alphabet(plain + cipher)
        deltas = []
        i = 0
        while i < len(plain):
            if alphabet.has(plain[i]) and alphabet.has(cipher[i]):
                px = alphabet.index[plain[i].lower()]
                cx = alphabet.index[cipher[i].lower()]
                deltas.append((cx - px) % alphabet.n)
            i += 1
        if mode == "motto":
            if len(deltas) == 0:
                raise ValueError("data")
            s = ""
            for d in deltas:
                s += alphabet.letters[d]
            return s
        if mode == "linear":
            if len(deltas) < 2:
                raise ValueError("data")
            a = 0
            while a < alphabet.n:
                b = deltas[0]
                ok = True
                p = 0
                while p < len(deltas):
                    if deltas[p] != (a * p + b) % alphabet.n:
                        ok = False
                        break
                    p += 1
                if ok:
                    return [a, b]
                a += 1
            raise ValueError("key")
        if len(deltas) < 3:
            raise ValueError("data")
        a = 0
        while a < alphabet.n:
            b = 0
            while b < alphabet.n:
                c = deltas[0]
                ok = True
                p = 0
                while p < len(deltas):
                    if deltas[p] != (a * p * p + b * p + c) % alphabet.n:
                        ok = False
                        break
                    p += 1
                if ok:
                    return [a, b, c]
                b += 1
            a += 1
        raise ValueError("key")
