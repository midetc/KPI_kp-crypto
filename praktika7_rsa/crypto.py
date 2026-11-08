import math


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y


def modinv(a, m):
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError("no inv")
    return x % m


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def factorize(n):
    # простий перебір (атака на маленьке N)
    if n < 2:
        return []
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 2
    if n > 1:
        factors.append(n)
    return factors


class TinyRSA:
    # навчальний RSA на маленьких числах (як у вікі-прикладі)
    def generate(self, p, q, e=None):
        if not is_prime(p) or not is_prime(q):
            raise ValueError("p/q")
        n = p * q
        phi = (p - 1) * (q - 1)
        if e is None:
            e = 65537
            if math.gcd(e, phi) != 1:
                e = 3
                while e < phi and math.gcd(e, phi) != 1:
                    e += 2
        else:
            e = int(e)
            if math.gcd(e, phi) != 1:
                raise ValueError("e")
        d = modinv(e, phi)
        return {
            "p": p,
            "q": q,
            "n": n,
            "phi": phi,
            "e": e,
            "d": d,
        }

    def encrypt_num(self, m, e, n):
        m = int(m)
        if m >= n:
            raise ValueError("m>=n")
        return pow(m, e, n)

    def decrypt_num(self, c, d, n):
        return pow(int(c), int(d), int(n))

    def attack_factor(self, n, e, c):
        fac = factorize(int(n))
        if len(fac) < 2:
            raise ValueError("factor")
        p = fac[0]
        q = int(n) // p
        phi = (p - 1) * (q - 1)
        d = modinv(int(e), phi)
        m = pow(int(c), d, int(n))
        return {"p": p, "q": q, "d": d, "m": m, "factors": fac}


class BigRSA:
    def __init__(self):
        self.private_pem = None
        self.public_pem = None

    def generate(self, bits=1024):
        from Crypto.PublicKey import RSA

        if bits < 1024:
            bits = 1024
        key = RSA.generate(bits)
        self.private_pem = key.export_key().decode("utf-8")
        self.public_pem = key.publickey().export_key().decode("utf-8")
        return self.public_pem, self.private_pem

    def encrypt(self, text, public_pem):
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_v1_5

        if text is None or text == "":
            raise ValueError("data")
        key = RSA.import_key(public_pem)
        cipher = PKCS1_v1_5.new(key)
        raw = text.encode("utf-8")
        # ріжемо на шматки якщо довго
        max_len = key.size_in_bytes() - 11
        out = b""
        i = 0
        while i < len(raw):
            out += cipher.encrypt(raw[i : i + max_len])
            i += max_len
        return out.hex()

    def decrypt(self, hex_text, private_pem):
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_v1_5

        if hex_text is None or hex_text.strip() == "":
            raise ValueError("data")
        key = RSA.import_key(private_pem)
        cipher = PKCS1_v1_5.new(key)
        raw = bytes.fromhex(hex_text.strip().replace(" ", ""))
        block = key.size_in_bytes()
        out = b""
        i = 0
        while i < len(raw):
            chunk = raw[i : i + block]
            dec = cipher.decrypt(chunk, None)
            if dec is None:
                raise ValueError("data")
            out += dec
            i += block
        return out.decode("utf-8", errors="replace")
