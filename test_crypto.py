import unittest

from crypto import CaesarCipher, TrithemiusCipher, BruteForceAttack, KnownPlaintextAttack, UA_ALPHABET


class CryptoTests(unittest.TestCase):
    def test_caesar_roundtrip(self):
        c = CaesarCipher()
        plain = "Алфавіт"
        key = 13
        enc = c.encrypt(plain, key, UA_ALPHABET)
        self.assertEqual(c.decrypt(enc, key, UA_ALPHABET), plain)

    def test_trithemius_linear(self):
        t = TrithemiusCipher()
        plain = "Привіт"
        enc = t.encrypt(plain, "linear", "2,3", UA_ALPHABET)
        self.assertEqual(t.decrypt(enc, "linear", "2,3", UA_ALPHABET), plain)

    def test_known_attack_linear(self):
        t = TrithemiusCipher()
        plain = "абвгдеєжзи"
        enc = t.encrypt(plain, "linear", "1,4", UA_ALPHABET)
        key = KnownPlaintextAttack().recover(plain, enc, "linear", UA_ALPHABET)
        self.assertEqual(key, [1, 4])

    def test_brute_contains_plain(self):
        c = CaesarCipher()
        plain = "тест"
        enc = c.encrypt(plain, 7, UA_ALPHABET)
        variants = BruteForceAttack().run(enc, UA_ALPHABET)
        self.assertTrue(any(v == plain for _, v in variants))


if __name__ == "__main__":
    unittest.main()
