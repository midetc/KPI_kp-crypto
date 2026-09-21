import unittest

from crypto import KnownPlaintextAttack, TrithemiusCipher, UA_ALPHABET


class TrithemiusTests(unittest.TestCase):
    def test_linear_roundtrip(self):
        cipher = TrithemiusCipher()
        plain = "Привіт"
        enc = cipher.encrypt(plain, "linear", "2,3", UA_ALPHABET)
        self.assertEqual(cipher.decrypt(enc, "linear", "2,3", UA_ALPHABET), plain)

    def test_known_attack(self):
        cipher = TrithemiusCipher()
        plain = "абвгдеєжзи"
        enc = cipher.encrypt(plain, "linear", "1,4", UA_ALPHABET)
        key = KnownPlaintextAttack().recover(plain, enc, "linear", UA_ALPHABET)
        self.assertEqual(key, [1, 4])


if __name__ == "__main__":
    unittest.main()
