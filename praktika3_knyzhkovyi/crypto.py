import random
import re

SUBSTITUTES = {
    "щ": "ш",
    "ё": "е",
    "ъ": "ь",
}

DEFAULT_POEM = (
    "Садок вишневий коло хати Хрущі над вишнями гудуть "
    "Плугатарі з плугами йдуть Дівчата пісню співають "
    "А матері вечерять ждуть Сім я і ти біля вікна "
    "Флейта грає в тиші саду Жито жовте коло шляху "
    "Цвіте щастя і любов Юність мріє про майбутнє"
)


class PoemKey:
    def __init__(self, poem: str, width: int):
        if width < 2 or width > 20:
            raise ValueError("key")
        letters = [ch for ch in poem if ch.isalpha()]
        if len(letters) < width:
            raise ValueError("key")
        self.width = width
        self.rows = []
        for i in range(0, len(letters), width):
            chunk = letters[i : i + width]
            if len(chunk) < width:
                chunk += [" "] * (width - len(chunk))
            self.rows.append(chunk)
        self.height = len(self.rows)

    def positions(self, ch: str) -> list[tuple[int, int]]:
        target = SUBSTITUTES.get(ch.lower(), ch.lower())
        found = []
        for r, row in enumerate(self.rows):
            for c, cell in enumerate(row):
                if cell.isalpha() and cell.lower() == target:
                    found.append((r + 1, c + 1))
        return found

    def at(self, row: int, col: int) -> str:
        if row < 1 or col < 1 or row > self.height or col > self.width:
            raise ValueError("data")
        ch = self.rows[row - 1][col - 1]
        if not ch.isalpha():
            raise ValueError("data")
        return ch

    def as_text(self) -> str:
        lines = ["   " + " ".join(f"{c:02d}" for c in range(1, self.width + 1))]
        for i, row in enumerate(self.rows, start=1):
            cells = "  ".join(ch if ch != " " else "·" for ch in row)
            lines.append(f"{i:02d} {cells}")
        return "\n".join(lines)


class VerseCipher:
    def validate_key(self, poem: str, width) -> PoemKey:
        try:
            w = int(width)
        except (TypeError, ValueError) as exc:
            raise ValueError("key") from exc
        return PoemKey(poem, w)

    def validate_data(self, data) -> str:
        if data is None:
            raise ValueError("data")
        text = data if isinstance(data, str) else data.decode("utf-8", errors="replace")
        if text.strip() == "":
            raise ValueError("data")
        return text

    def encrypt(self, data, poem: str, width, rng: random.Random | None = None) -> str:
        text = self.validate_data(data)
        key = self.validate_key(poem, width)
        rnd = rng or random.Random()
        codes = []
        for ch in text:
            if not ch.isalpha():
                continue
            opts = key.positions(ch)
            if not opts:
                raise ValueError("data")
            r, c = rnd.choice(opts)
            codes.append(f"{r}/{c}")
        if not codes:
            raise ValueError("data")
        return ", ".join(codes)

    def decrypt(self, data, poem: str, width) -> str:
        text = self.validate_data(data)
        key = self.validate_key(poem, width)
        tokens = re.findall(r"(\d+)\s*/\s*(\d+)", text)
        if not tokens:
            raise ValueError("data")
        return "".join(key.at(int(r), int(c)) for r, c in tokens)


class WordBookCipher:
    def validate_key(self, book: str) -> list[str]:
        words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ']+", book)
        if not words:
            raise ValueError("key")
        return words

    def validate_data(self, data) -> str:
        if data is None:
            raise ValueError("data")
        text = data if isinstance(data, str) else data.decode("utf-8", errors="replace")
        if text.strip() == "":
            raise ValueError("data")
        return text

    def encrypt(self, data, book: str, rng: random.Random | None = None) -> str:
        text = self.validate_data(data)
        words = self.validate_key(book)
        rnd = rng or random.Random()
        codes = []
        for ch in text:
            if not ch.isalpha():
                continue
            target = SUBSTITUTES.get(ch.lower(), ch.lower())
            opts = [i + 1 for i, w in enumerate(words) if w[0].lower() == target]
            if not opts:
                raise ValueError("data")
            codes.append(str(rnd.choice(opts)))
        if not codes:
            raise ValueError("data")
        return ", ".join(codes)

    def decrypt(self, data, book: str) -> str:
        text = self.validate_data(data)
        words = self.validate_key(book)
        nums = re.findall(r"\d+", text)
        if not nums:
            raise ValueError("data")
        out = []
        for n in nums:
            idx = int(n) - 1
            if idx < 0 or idx >= len(words):
                raise ValueError("data")
            out.append(words[idx][0])
        return "".join(out)
