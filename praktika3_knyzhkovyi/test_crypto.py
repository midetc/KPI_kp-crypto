import random
import unittest

from crypto import DEFAULT_POEM, VerseCipher, WordBookCipher


class VerseTests(unittest.TestCase):
    def test_roundtrip(self):
        cipher = VerseCipher()
        plain = "тест"
        enc = cipher.encrypt(plain, DEFAULT_POEM, 10, random.Random(1))
        dec = cipher.decrypt(enc, DEFAULT_POEM, 10)
        self.assertEqual(dec.lower(), plain.lower())

    def test_word_book(self):
        cipher = WordBookCipher()
        book = "Алла бере вишню дуже жарко"
        plain = "абв"
        enc = cipher.encrypt(plain, book, random.Random(2))
        dec = cipher.decrypt(enc, book)
        self.assertEqual(dec.lower(), plain.lower())


if __name__ == "__main__":
    unittest.main()
