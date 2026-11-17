import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto import DsaSign, RsaSign


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЕЦП RSA / DSA")
        self.geometry("900x640")
        self.path = None
        self.rsa = RsaSign()
        self.dsa = DsaSign()
        self.pub = ""
        self.priv = ""
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

        sign_menu = tk.Menu(menu, tearoff=0)
        sign_menu.add_command(label="Згенерувати ключі", command=self.gen_keys)
        sign_menu.add_command(label="Показати відкритий ключ", command=self.show_pub)
        sign_menu.add_separator()
        sign_menu.add_command(label="Підписати", command=self.sign_msg)
        sign_menu.add_command(label="Перевірити підпис", command=self.verify_msg)
        sign_menu.add_command(label="Показати SHA-1 хеш", command=self.show_hash)
        menu.add_cascade(label="Підпис", menu=sign_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="Про розробника", command=self.about)
        menu.add_cascade(label="Довідка", menu=help_menu)
        self.config(menu=menu)

    def make_toolbar(self):
        bar = tk.Frame(self, bd=1, relief=tk.RAISED)
        bar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(bar, text="Ключі", command=self.gen_keys).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Pub key", command=self.show_pub).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Підпис", command=self.sign_msg).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Перевірка", command=self.verify_msg).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Хеш", command=self.show_hash).pack(side=tk.LEFT, padx=2, pady=2)

    def make_ui(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(top, text="Алгоритм").grid(row=0, column=0)
        self.algo = ttk.Combobox(top, values=["RSA", "DSA"], state="readonly", width=8)
        self.algo.current(0)
        self.algo.grid(row=0, column=1, padx=4)

        tk.Label(top, text="Біти").grid(row=0, column=2, padx=(10, 0))
        self.bits = ttk.Combobox(top, values=["1024", "2048"], state="readonly", width=8)
        self.bits.current(0)
        self.bits.grid(row=0, column=3, padx=4)

        tk.Label(self, text="Повідомлення").pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=8)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self.input.insert("1.0", "Hello world!")

        tk.Label(self, text="Підпис (hex)").pack(anchor="w", padx=8)
        self.sign_box = tk.Text(self, height=6)
        self.sign_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text="Результат").pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=8)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def current(self):
        if self.algo.get() == "RSA":
            return self.rsa
        return self.dsa

    def new_file(self):
        self.path = None
        self.input.delete("1.0", tk.END)
        self.sign_box.delete("1.0", tk.END)
        self.output.delete("1.0", tk.END)

    def open_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            f = open(path, encoding="utf-8")
            text = f.read()
            f.close()
            self.input.delete("1.0", tk.END)
            self.input.insert("1.0", text)
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
            data = self.output.get("1.0", tk.END).rstrip("\n")
            if data == "":
                data = self.sign_box.get("1.0", tk.END).rstrip("\n")
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
            "ЕЦП RSA / DSA\nМихайлець Артем Миколайович\nТВ-33\nКП №8",
        )

    def gen_keys(self):
        try:
            bits = int(self.bits.get())
            engine = self.current()
            pub, priv = engine.generate(bits)
            self.pub = pub
            self.priv = priv
            messagebox.showinfo("Ок", "Ключі " + self.algo.get() + " згенеровано")
            self.show_pub()
        except Exception:
            messagebox.showerror("Помилка", "Не вийшло (потрібен pycryptodome)")

    def show_pub(self):
        win = tk.Toplevel(self)
        win.title("Відкритий ключ")
        win.geometry("640x420")
        tk.Label(win, text="Public key (можна вставити чужий для перевірки)").pack(anchor="w")
        box = tk.Text(win, height=18)
        box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        box.insert("1.0", self.pub)

        def apply_pub():
            self.pub = box.get("1.0", tk.END).strip()
            messagebox.showinfo("Ок", "Відкритий ключ збережено")

        tk.Button(win, text="Застосувати", command=apply_pub).pack(pady=6)

    def show_hash(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        try:
            hx = self.rsa.hash_hex(text)
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", "SHA-1:\n" + hx)
        except Exception:
            messagebox.showerror("Помилка", "Нема тексту")

    def sign_msg(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        if self.priv.strip() == "":
            messagebox.showerror("Помилка", "Спочатку згенеруй ключі")
            return
        try:
            engine = self.current()
            sig = engine.sign(text, self.priv)
            self.sign_box.delete("1.0", tk.END)
            self.sign_box.insert("1.0", sig)
            hx = self.rsa.hash_hex(text)
            self.output.delete("1.0", tk.END)
            self.output.insert(
                "1.0",
                "Підписано (" + self.algo.get() + ")\nSHA-1: " + hx + "\nпідпис у полі вище",
            )
        except Exception:
            messagebox.showerror("Помилка", "Не підписалось")

    def verify_msg(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        sig = self.sign_box.get("1.0", tk.END).rstrip("\n")
        if self.pub.strip() == "":
            messagebox.showerror("Помилка", "Нема відкритого ключа")
            return
        try:
            engine = self.current()
            ok = engine.verify(text, sig, self.pub)
            self.output.delete("1.0", tk.END)
            if ok:
                self.output.insert("1.0", "Verdict: True\nПідпис вірний")
            else:
                self.output.insert("1.0", "Verdict: False\nПідпис НЕ вірний")
        except Exception:
            messagebox.showerror("Помилка", "Помилка перевірки (ключ/підпис?)")


if __name__ == "__main__":
    App().mainloop()
