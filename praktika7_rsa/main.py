import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from crypto import BigRSA, TinyRSA, factorize


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RSA")
        self.geometry("880x640")
        self.path = None
        self.big = BigRSA()
        self.tiny = TinyRSA()
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

        cipher_menu = tk.Menu(menu, tearoff=0)
        cipher_menu.add_command(label="Згенерувати ключі", command=self.gen_keys)
        cipher_menu.add_command(label="Показати відкритий ключ", command=self.show_pub)
        cipher_menu.add_command(label="Зашифрувати", command=self.encrypt)
        cipher_menu.add_command(label="Розшифрувати", command=self.decrypt)
        cipher_menu.add_separator()
        cipher_menu.add_command(label="Навчальний приклад (wiki)", command=self.wiki_example)
        cipher_menu.add_command(label="Атака факторизацією", command=self.attack)
        menu.add_cascade(label="RSA", menu=cipher_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="Про розробника", command=self.about)
        menu.add_cascade(label="Довідка", menu=help_menu)
        self.config(menu=menu)

    def make_toolbar(self):
        bar = tk.Frame(self, bd=1, relief=tk.RAISED)
        bar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(bar, text="Ключі", command=self.gen_keys).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Pub key", command=self.show_pub).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Шифр", command=self.encrypt).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(bar, text="Дешифр", command=self.decrypt).pack(side=tk.LEFT, padx=2, pady=2)

    def make_ui(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(top, text="Біти ключа").grid(row=0, column=0)
        self.bits = ttk.Combobox(top, values=["1024", "2048"], state="readonly", width=8)
        self.bits.current(0)
        self.bits.grid(row=0, column=1, padx=4)

        tk.Label(self, text="Текст / шифротекст (hex)").pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=12)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text="Результат").pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=12)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def new_file(self):
        self.path = None
        self.input.delete("1.0", tk.END)
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
            "RSA\nМихайлець Артем Миколайович\nТВ-33\nКП №7",
        )

    def gen_keys(self):
        try:
            bits = int(self.bits.get())
            pub, priv = self.big.generate(bits)
            self.pub = pub
            self.priv = priv
            messagebox.showinfo("Ок", "Ключі згенеровано (" + str(bits) + " біт)")
            self.show_pub()
        except Exception:
            messagebox.showerror("Помилка", "Не вийшло згенерувати (постав pycryptodome)")

    def show_pub(self):
        win = tk.Toplevel(self)
        win.title("Відкритий ключ")
        win.geometry("640x420")
        tk.Label(win, text="Public key (можна скопіювати / вставити інший)").pack(anchor="w")
        box = tk.Text(win, height=18)
        box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        box.insert("1.0", self.pub)

        def save_pub():
            self.pub = box.get("1.0", tk.END).strip()
            messagebox.showinfo("Ок", "Відкритий ключ збережено в пам'яті")

        tk.Button(win, text="Застосувати", command=save_pub).pack(pady=6)

    def encrypt(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        if self.pub.strip() == "":
            messagebox.showerror("Помилка", "Спочатку згенеруй / встав відкритий ключ")
            return
        try:
            result = self.big.encrypt(text, self.pub)
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except Exception:
            messagebox.showerror("Помилка", "Не зашифрувалось")

    def decrypt(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        if self.priv.strip() == "":
            messagebox.showerror("Помилка", "Нема закритого ключа (згенеруй пару тут)")
            return
        try:
            result = self.big.decrypt(text, self.priv)
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except Exception:
            messagebox.showerror("Помилка", "Не розшифрувалось")

    def wiki_example(self):
        # класичний маленький приклад: p=61 q=53 e=17 m=65
        keys = self.tiny.generate(61, 53, 17)
        m = 65
        c = self.tiny.encrypt_num(m, keys["e"], keys["n"])
        m2 = self.tiny.decrypt_num(c, keys["d"], keys["n"])
        text = (
            "Приклад як у Вікіпедії (малі числа):\n"
            "p=61, q=53\n"
            "n=p*q=" + str(keys["n"]) + "\n"
            "phi=" + str(keys["phi"]) + "\n"
            "e=" + str(keys["e"]) + "\n"
            "d=" + str(keys["d"]) + "\n"
            "m=" + str(m) + "\n"
            "c = m^e mod n = " + str(c) + "\n"
            "m' = c^d mod n = " + str(m2) + "\n"
            "ok=" + str(m == m2)
        )
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)

    def attack(self):
        n = simpledialog.askinteger("Атака", "N =", parent=self, minvalue=2)
        if n is None:
            return
        e = simpledialog.askinteger("Атака", "e =", parent=self, minvalue=2)
        if e is None:
            return
        c = simpledialog.askinteger("Атака", "шифротекст c =", parent=self, minvalue=0)
        if c is None:
            return
        try:
            fac = factorize(n)
            res = self.tiny.attack_factor(n, e, c)
            text = (
                "Факторизація N:\n"
                + str(fac)
                + "\n"
                + "p=" + str(res["p"]) + " q=" + str(res["q"]) + "\n"
                + "d=" + str(res["d"]) + "\n"
                + "відновлене m=" + str(res["m"]) + "\n"
                + "\nАтака реальна коли N маленьке (до ~10^12 перебором швидко).\n"
                "Для 1024+ біт факторизація на звичайному ПК practically неможлива."
            )
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", text)
        except Exception:
            messagebox.showerror("Помилка", "Не розклалось / погані параметри")


if __name__ == "__main__":
    App().mainloop()
