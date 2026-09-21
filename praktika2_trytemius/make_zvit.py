from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

from crypto import TrithemiusCipher, UA_ALPHABET


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
    cipher = TrithemiusCipher()
    plain = "Алфавіт"
    linear_key = "2,5"
    enc_lin = cipher.encrypt(plain, "linear", linear_key, UA_ALPHABET)
    dec_lin = cipher.decrypt(enc_lin, "linear", linear_key, UA_ALPHABET)
    enc_nl = cipher.encrypt(plain, "nonlinear", "1,2,3", UA_ALPHABET)
    enc_m = cipher.encrypt(plain, "motto", "ключ", UA_ALPHABET)

    doc = Document()
    p = doc.add_paragraph()
    r = p.add_run("Безпека інформаційних систем")
    r.font.color.rgb = RGBColor(0x00, 0x55, 0x99)
    r.bold = True
    doc.add_paragraph("Група ТВ-33")
    doc.add_paragraph("Михайлець Артем Миколайович")
    add_title(doc, "Комп'ютерний практикум №2")
    add_title(doc, "Тема: Шифр Тритеміуса")
    doc.add_paragraph(
        "Мета: розробити криптосистему на основі шифру Тритеміуса "
        "(модифікація системи з КП №1)."
    )

    add_title(doc, "Крок 1. Лінійний ключ (A, B)")
    for line in (
        f'Ввід: "{plain}"',
        f"Ключ: {linear_key}  (k = A*p + B)",
        f'Шифротекст: "{enc_lin}"',
        f'Після розшифрування: "{dec_lin}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Print Screen лінійного режиму]")

    add_title(doc, "Крок 2. Нелінійний ключ (A, B, C)")
    for line in (
        f'Ввід: "{plain}"',
        'Ключ: 1,2,3  (k = A*p^2 + B*p + C)',
        f'Шифротекст: "{enc_nl}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Print Screen нелінійного режиму]")

    add_title(doc, "Крок 3. Гасло")
    for line in (
        f'Ввід: "{plain}"',
        'Гасло: "ключ"',
        f'Шифротекст: "{enc_m}"',
    ):
        doc.add_paragraph(line)
    add_red(doc, "[Print Screen режиму з гаслом]")

    add_title(doc, "Крок 4. Код")
    add_red(doc, "[Print Screen TrithemiusCipher / KnownPlaintextAttack]")

    doc.add_paragraph(
        "Додаткове завдання: атака за парою відкритий — шифротекст "
        "(меню Шифрування → Атака за відомою парою)."
    )
    doc.save("zvit.docx")
    print("ok")


if __name__ == "__main__":
    main()
