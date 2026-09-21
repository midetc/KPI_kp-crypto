from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

from crypto import CaesarCipher, UA_ALPHABET


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
    c = CaesarCipher()
    key = 13
    plain = "Алфавіт"
    enc = c.encrypt(plain, key, UA_ALPHABET)
    dec = c.decrypt(enc, key, UA_ALPHABET)

    doc = Document()
    p = doc.add_paragraph()
    r = p.add_run("Безпека інформаційних систем")
    r.font.color.rgb = RGBColor(0x00, 0x55, 0x99)
    r.bold = True
    doc.add_paragraph("Група ТВ-33")
    doc.add_paragraph("Михайлець Артем Миколайович")
    add_title(doc, "Комп'ютерний практикум №1")
    add_title(doc, "Тема: Шифр Цезаря")
    doc.add_paragraph("Мета: розробити криптосистему на основі шифру Цезаря.")

    add_title(doc, "Крок 1. Шифрування")
    for line in (
        'Інтерфейс програми "Шифр Цезаря" (Михайлець А.М.)',
        f'Ввід: "{plain}"',
        f"Ключ (номер у списку): {key}",
        f'Результат: "{enc}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Сюди вставити Print Screen вікна з шифруванням]")

    add_title(doc, "Крок 2. Фрагмент коду")
    add_red(doc, "[Print Screen: validate_key / encrypt / decrypt]")

    add_title(doc, "Крок 3. Розшифрування")
    for line in (
        'Інтерфейс програми "Шифр Цезаря"',
        f'Ввід: "{enc}"',
        f"Ключ: {key}",
        f'Результат: "{dec}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Сюди вставити Print Screen вікна з розшифруванням]")

    doc.add_paragraph(
        "Додатково: атака грубою силою та шифрування бінарних файлів (mod 256)."
    )
    add_red(doc, "Решта лабораторних — аналогічно.")
    doc.save("zvit.docx")
    print("ok")


if __name__ == "__main__":
    main()
