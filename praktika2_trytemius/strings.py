STRINGS = {
    "app_title": "Шифр Тритеміуса",
    "file": "Файл",
    "cipher": "Шифрування",
    "help": "Довідка",
    "new": "Створити",
    "open": "Відкрити...",
    "save": "Зберегти",
    "save_as": "Зберегти як...",
    "print": "Друк",
    "exit": "Вихід",
    "encrypt": "Зашифрувати",
    "decrypt": "Розшифрувати",
    "known_attack": "Атака за відомою парою",
    "about": "Про розробника",
    "lang_ua": "Українська",
    "lang_en": "English",
    "mode_linear": "Лінійний (A, B)",
    "mode_nonlinear": "Нелінійний (A, B, C)",
    "mode_motto": "Гасло",
    "key": "Ключ",
    "text": "Текст",
    "result": "Результат",
    "alphabet": "Азбука",
    "mode": "Тип ключа",
    "about_text": (
        "Програма «Шифр Тритеміуса»\n"
        "Михайлець Артем Миколайович\n"
        "Група ТВ-33\n"
        "Комп'ютерний практикум №2"
    ),
    "err_key": "Невірний ключ",
    "err_data": "Немає даних для обробки",
    "err_open": "Не вдалося відкрити файл",
    "err_save": "Не вдалося зберегти файл",
    "saved": "Файл збережено",
    "untitled": "bez_nazvy.txt",
    "binary_hint": "Бінарний файл. Шифрування по байтах (mod 256).",
    "attack_title": "Відновлення ключа",
    "plain": "Відкритий текст",
    "cipher_text": "Шифротекст",
    "find_key": "Знайти ключ",
    "toolbar_encrypt": "Шифр",
    "toolbar_decrypt": "Дешифр",
    "key_hint": "лінійний: A,B | нелінійний: A,B,C | гасло: текст",
}


def t(key: str) -> str:
    return STRINGS[key]
