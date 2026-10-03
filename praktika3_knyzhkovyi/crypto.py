import random
import re

DEFAULT_POEM = (
    "Садок вишневий коло хати Хрущі над вишнями гудуть "
    "Плугатарі з плугами йдуть Дівчата пісню співають "
    "А матері вечерять ждуть Сім я і ти біля вікна "
    "Флейта грає в тиші саду Жито жовте коло шляху "
    "Цвіте щастя і любов Юність мріє про майбутнє"
)


class PoemKey:
    def __init__(self, poem, width):
        width = int(width)
        if width < 2:
            raise ValueError("key")
        letters = []
        for ch in poem:
            if ch.isalpha():
                letters.append(ch)
        if len(letters) < width:
            raise ValueError("key")
        self.width = width
        self.rows = []
        i = 0
        while i < len(letters):
            row = letters[i : i + width]
            while len(row) < width:
                row.append(" ")
            self.rows.append(row)
            i += width
        self.height = len(self.rows)

    def positions(self, ch):
        target = ch.lower()
        if target == "щ":
            target = "ш"
        found = []
        r = 0
        while r < len(self.rows):
            c = 0
            while c < len(self.rows[r]):
                cell = self.rows[r][c]
                if cell.isalpha() and cell.lower() == target:
                    found.append((r + 1, c + 1))
                c += 1
            r += 1
        return found

    def at(self, row, col):
        ch = self.rows[row - 1][col - 1]
        if not ch.isalpha():
            raise ValueError("data")
        return ch

    def as_text(self):
        lines = []
        head = "   "
        c = 1
        while c <= self.width:
            head += "%02d " % c
            c += 1
        lines.append(head)
        r = 0
        while r < len(self.rows):
            line = "%02d " % (r + 1)
            for ch in self.rows[r]:
                if ch == " ":
                    line += ". "
                else:
                    line += ch + " "
            lines.append(line)
            r += 1
        return "\n".join(lines)


class VerseCipher:
    def validate_key(self, poem, width):
        return PoemKey(poem, width)

    def validate_data(self, data):
        if data is None or str(data).strip() == "":
            raise ValueError("data")
        return str(data)

    def encrypt(self, data, poem, width):
        text = self.validate_data(data)
        key = self.validate_key(poem, width)
        codes = []
        for ch in text:
            if not ch.isalpha():
                continue
            opts = key.positions(ch)
            if len(opts) == 0:
                raise ValueError("data")
            r, c = random.choice(opts)
            codes.append(str(r) + "/" + str(c))
        if len(codes) == 0:
            raise ValueError("data")
        return ", ".join(codes)

    def decrypt(self, data, poem, width):
        text = self.validate_data(data)
        key = self.validate_key(poem, width)
        tokens = re.findall(r"(\d+)\s*/\s*(\d+)", text)
        if len(tokens) == 0:
            raise ValueError("data")
        out = ""
        for r, c in tokens:
            out += key.at(int(r), int(c))
        return out


class WordBookCipher:
    def get_words(self, book):
        words = re.findall(r"[A-Za-zА-Яа-яІіЇїЄєҐґ']+", book)
        if len(words) == 0:
            raise ValueError("key")
        return words

    def encrypt(self, data, book):
        if data is None or str(data).strip() == "":
            raise ValueError("data")
        words = self.get_words(book)
        codes = []
        for ch in data:
            if not ch.isalpha():
                continue
            target = ch.lower()
            opts = []
            i = 0
            while i < len(words):
                if words[i][0].lower() == target:
                    opts.append(i + 1)
                i += 1
            if len(opts) == 0:
                raise ValueError("data")
            codes.append(str(random.choice(opts)))
        return ", ".join(codes)

    def decrypt(self, data, book):
        words = self.get_words(book)
        nums = re.findall(r"\d+", data)
        if len(nums) == 0:
            raise ValueError("data")
        out = ""
        for n in nums:
            idx = int(n) - 1
            out += words[idx][0]
        return out
