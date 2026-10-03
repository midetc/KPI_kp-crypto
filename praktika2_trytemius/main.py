import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto import EN_ALPHABET, KnownPlaintextAttack, TrithemiusCipher, UA_ALPHABET


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Шифр Тритеміуса")
        self.geometry("820x560")
        self.path = None
        self.binary = None
        self.cipher = TrithemiusCipher()
        self.make_menu()
        self.make_toolbar()
        self.make_ui()

    def make_menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Створити", command=self.new_file)
        file_menu.add_command(label="Відкрити...", command=self.open_file)
        file_menu.add_command(label="Зберегти", command=self.save_file)
        file_menu.add_command(label="Зберегти як...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Друк", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.destroy)
        menu.add_cascade(label="Файл", menu=file_menu)

        cipher_menu = tk.Menu(menu, tearoff=0)
        cipher_menu.add_command(label="Зашифрувати", command=self.encrypt)
        cipher_menu.add_command(label="Розшифрувати", command=self.decrypt)
        cipher_menu.add_separator()
        cipher_menu.add_command(label="Атака за відомою парою", command=self.known_attack)
        menu.add_cascade(label="Шифрування", menu=cipher_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="Про розробника", command=self.about)
        menu.add_cascade(label="Довідка", menu=help_menu)
        self.config(menu=menu)

    def make_toolbar(self):
        bar = tk.Frame(self, bd=1, relief=tk.RAISED)
        bar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(bar, text="Відкрити", command=self.open_file).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Зберегти", command=self.save_file).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Шифр", command=self.encrypt).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Дешифр", command=self.decrypt).pack(side=tk.LEFT, padx=2, pady=2)

    def make_ui(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(top, text="Тип ключа").grid(row=0, column=0)
        self.mode = ttk.Combobox(
            top,
            values=["Лінійний (A,B)", "Нелінійний (A,B,C)", "Гасло"],
            state="readonly",
            width=24,
        )
        self.mode.current(0)
        self.mode.grid(row=0, column=1, padx=4)

        tk.Label(top, text="Азбука").grid(row=0, column=2, padx=(12, 0))
        self.lang = ttk.Combobox(top, values=["Українська", "English"], state="readonly", width=14)
        self.lang.current(0)
        self.lang.grid(row=0, column=3, padx=4)

        tk.Label(top, text="Ключ").grid(row=1, column=0, pady=6)
        self.key_var = tk.StringVar(value="2,5")
        tk.Entry(top, textvariable=self.key_var, width=40).grid(row=1, column=1, columnspan=3, padx=4)

        tk.Label(top, text="лінійний: 2,5 | нелінійний: 1,2,3 | гасло: текст", fg="#555").grid(
            row=2, column=1, columnspan=3, sticky="w"
        )

        tk.Label(self, text="Текст").pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=12)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text="Результат").pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=10)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def get_alphabet(self):
        if self.lang.current() == 0:
            return UA_ALPHABET
        return EN_ALPHABET

    def get_mode(self):
        return ["linear", "nonlinear", "motto"][self.mode.current()]

    def new_file(self):
        self.path = None
        self.binary = None
        self.input.delete("1.0", tk.END)
        self.output.delete("1.0", tk.END)

    def open_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            f = open(path, "rb")
            raw = f.read()
            f.close()
            try:
                text = raw.decode("utf-8")
                self.binary = None
                self.input.delete("1.0", tk.END)
                self.input.insert("1.0", text)
            except UnicodeDecodeError:
                self.binary = raw
                self.input.delete("1.0", tk.END)
                self.input.insert("1.0", "бінарний файл\n" + path)
            self.path = path
        except OSError:
            messagebox.showerror("Помилка", "Не відкрилось")

    def save_file(self):
        if self.path is None:
            self.save_as()
        else:
            self.write_file(self.path)

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            self.path = path
            self.write_file(path)

    def write_file(self, path):
        try:
            if self.binary is not None:
                f = open(path, "wb")
                f.write(self.binary)
                f.close()
            else:
                data = self.output.get("1.0", tk.END).rstrip("\n")
                if data == "":
                    data = self.input.get("1.0", tk.END).rstrip("\n")
                f = open(path, "w", encoding="utf-8")
                f.write(data)
                f.close()
            messagebox.showinfo("Ок", "Збережено")
        except OSError:
            messagebox.showerror("Помилка", "Не збереглось")

    def print_file(self):
        data = self.output.get("1.0", tk.END).strip()
        if data == "":
            data = self.input.get("1.0", tk.END)
        tmp = os.path.join(tempfile.gettempdir(), "print.txt")
        f = open(tmp, "w", encoding="utf-8")
        f.write(data)
        f.close()
        try:
            os.startfile(tmp, "print")
        except OSError:
            messagebox.showinfo("Друк", tmp)

    def about(self):
        messagebox.showinfo(
            "Про розробника",
            "Шифр Тритеміуса\nМихайлець Артем Миколайович\nТВ-33\nКП №2",
        )

    def encrypt(self):
        self.run(True)

    def decrypt(self):
        self.run(False)

    def run(self, enc):
        key = self.key_var.get()
        mode = self.get_mode()
        ab = self.get_alphabet()
        try:
            if self.binary is not None:
                if enc:
                    out = self.cipher.encrypt_bytes(self.binary, mode, key)
                else:
                    out = self.cipher.decrypt_bytes(self.binary, mode, key)
                self.binary = out
                self.output.delete("1.0", tk.END)
                self.output.insert("1.0", "готово")
                return
            text = self.input.get("1.0", tk.END).rstrip("\n")
            if enc:
                result = self.cipher.encrypt(text, mode, key, ab)
            else:
                result = self.cipher.decrypt(text, mode, key, ab)
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except ValueError:
            messagebox.showerror("Помилка", "Перевір ключ/текст")

    def known_attack(self):
        win = tk.Toplevel(self)
        win.title("Знайти ключ")
        tk.Label(win, text="Відкритий текст").pack(anchor="w")
        plain = tk.Text(win, height=5, width=70)
        plain.pack()
        tk.Label(win, text="Шифротекст").pack(anchor="w")
        cipher = tk.Text(win, height=5, width=70)
        cipher.pack()
        mode_box = ttk.Combobox(
            win,
            values=["Лінійний (A,B)", "Нелінійний (A,B,C)", "Гасло"],
            state="readonly",
        )
        mode_box.current(0)
        mode_box.pack(pady=4)
        info = tk.Label(win, text="")
        info.pack()

        def find():
            modes = ["linear", "nonlinear", "motto"]
            try:
                key = KnownPlaintextAttack().recover(
                    plain.get("1.0", tk.END).rstrip("\n"),
                    cipher.get("1.0", tk.END).rstrip("\n"),
                    modes[mode_box.current()],
                    self.get_alphabet(),
                )
                if isinstance(key, list):
                    s = ",".join(str(x) for x in key)
                else:
                    s = str(key)
                info.config(text="ключ: " + s)
                self.key_var.set(s)
            except ValueError:
                info.config(text="не вийшло")

        tk.Button(win, text="Знайти", command=find).pack(pady=6)


if __name__ == "__main__":
    App().mainloop()
