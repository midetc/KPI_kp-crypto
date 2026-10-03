from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

from crypto import DEFAULT_POEM, VerseCipher
import random


def add_title(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_red(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)


def main():
    cipher = VerseCipher()
    plain = "Алфавіт"
    width = 10
    enc = cipher.encrypt(plain, DEFAULT_POEM, width, random.Random(13))
    dec = cipher.decrypt(enc, DEFAULT_POEM, width)
    grid = cipher.validate_key(DEFAULT_POEM, width).as_text()

    doc = Document()
    p = doc.add_paragraph()
    r = p.add_run("Безпека інформаційних систем")
    r.font.color.rgb = RGBColor(0x00, 0x55, 0x99)
    r.bold = True
    doc.add_paragraph("Група ТВ-33")
    doc.add_paragraph("Михайлець Артем Миколайович")
    add_title(doc, "Комп'ютерний практикум №3")
    add_title(doc, "Тема: Книжковий шифр")
    doc.add_paragraph(
        "Мета: розробити криптосистему на основі використання "
        "віршованого фрагменту в якості ключа шифрування."
    )

    add_title(doc, "Крок 1. Ключова таблиця")
    doc.add_paragraph(f"Ширина таблиці: {width}")
    doc.add_paragraph(grid)
    add_red(doc, "[Print Screen вікна з таблицею ключа]")

    add_title(doc, "Крок 2. Шифрування")
    for line in (
        f'Ввід: "{plain}"',
        f'Шифрограма: "{enc}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Print Screen шифрування]")

    add_title(doc, "Крок 3. Розшифрування")
    for line in (
        f'Ввід: "{enc}"',
        f'Результат: "{dec}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Print Screen розшифрування]")

    add_title(doc, "Крок 4. Код")
    add_red(doc, "[Print Screen VerseCipher / WordBookCipher]")

    doc.add_paragraph(
        "Додаткове завдання: реалізовано книжковий варіант за номером слова "
        "(перша літера слова книги → символ повідомлення)."
    )
    doc.save("zvit.docx")
    print("ok")


if __name__ == "__main__":
    main()
