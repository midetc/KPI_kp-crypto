import unittest

from crypto import BruteForceAttack, CaesarCipher, UA_ALPHABET


class CaesarTests(unittest.TestCase):
    def test_roundtrip(self):
        c = CaesarCipher()
        plain = "Алфавіт"
        enc = c.encrypt(plain, 13, UA_ALPHABET)
        self.assertEqual(c.decrypt(enc, 13, UA_ALPHABET), plain)

    def test_brute(self):
        c = CaesarCipher()
        plain = "тест"
        enc = c.encrypt(plain, 7, UA_ALPHABET)
        variants = BruteForceAttack().run(enc, UA_ALPHABET)
        self.assertTrue(any(v == plain for _, v in variants))


if __name__ == "__main__":
    unittest.main()
