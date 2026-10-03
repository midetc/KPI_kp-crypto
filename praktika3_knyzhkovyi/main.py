import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto import DEFAULT_POEM, VerseCipher, WordBookCipher


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Книжковий шифр")
        self.geometry("860x640")
        self.path = None
        self.verse = VerseCipher()
        self.word = WordBookCipher()
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
        cipher_menu.add_command(label="Показати таблицю", command=self.show_grid)
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
        tk.Button(bar, text="Таблиця", command=self.show_grid).pack(side=tk.LEFT, padx=2, pady=2)

    def make_ui(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(top, text="Режим").grid(row=0, column=0)
        self.mode = ttk.Combobox(
            top,
            values=["Віршований (рядок/стовпець)", "Книжковий (номер слова)"],
            state="readonly",
            width=32,
        )
        self.mode.current(0)
        self.mode.grid(row=0, column=1, padx=4)

        tk.Label(top, text="Ширина").grid(row=0, column=2, padx=(12, 0))
        self.width_var = tk.StringVar(value="10")
        tk.Entry(top, textvariable=self.width_var, width=6).grid(row=0, column=3, padx=4)

        tk.Label(self, text="Ключ (вірш / текст)").pack(anchor="w", padx=8)
        self.poem = tk.Text(self, height=6)
        self.poem.pack(fill=tk.X, padx=8, pady=4)
        self.poem.insert("1.0", DEFAULT_POEM)

        tk.Label(self, text="Текст").pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=10)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text="Результат").pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=8)
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
            "Книжковий шифр\nМихайлець Артем Миколайович\nТВ-33\nКП №3",
        )

    def show_grid(self):
        try:
            key = self.verse.validate_key(
                self.poem.get("1.0", tk.END).rstrip("\n"),
                self.width_var.get(),
            )
        except ValueError:
            messagebox.showerror("Помилка", "Поганий ключ")
            return
        win = tk.Toplevel(self)
        win.title("Таблиця")
        box = tk.Text(win, width=70, height=20)
        box.pack(fill=tk.BOTH, expand=True)
        box.insert("1.0", key.as_text())

    def encrypt(self):
        self.run(True)

    def decrypt(self):
        self.run(False)

    def run(self, enc):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        poem = self.poem.get("1.0", tk.END).rstrip("\n")
        try:
            if self.mode.current() == 0:
                if enc:
                    result = self.verse.encrypt(text, poem, self.width_var.get())
                else:
                    result = self.verse.decrypt(text, poem, self.width_var.get())
            else:
                if enc:
                    result = self.word.encrypt(text, poem)
                else:
                    result = self.word.decrypt(text, poem)
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except ValueError:
            messagebox.showerror("Помилка", "Щось не так з текстом/ключем")


if __name__ == "__main__":
    App().mainloop()
