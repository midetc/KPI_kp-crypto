import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto import DEFAULT_POEM, VerseCipher, WordBookCipher
from strings import t


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(t("app_title"))
        self.geometry("860x640")
        self.path = None
        self.verse = VerseCipher()
        self.word = WordBookCipher()
        self._menu()
        self._toolbar()
        self._body()

    def _menu(self):
        bar = tk.Menu(self)
        file_m = tk.Menu(bar, tearoff=0)
        file_m.add_command(label=t("new"), command=self.new_file)
        file_m.add_command(label=t("open"), command=self.open_file)
        file_m.add_command(label=t("save"), command=self.save_file)
        file_m.add_command(label=t("save_as"), command=self.save_as)
        file_m.add_separator()
        file_m.add_command(label=t("print"), command=self.print_file)
        file_m.add_separator()
        file_m.add_command(label=t("exit"), command=self.destroy)
        bar.add_cascade(label=t("file"), menu=file_m)

        cipher_m = tk.Menu(bar, tearoff=0)
        cipher_m.add_command(label=t("encrypt"), command=self.encrypt)
        cipher_m.add_command(label=t("decrypt"), command=self.decrypt)
        cipher_m.add_separator()
        cipher_m.add_command(label=t("show_grid"), command=self.show_grid)
        bar.add_cascade(label=t("cipher"), menu=cipher_m)

        help_m = tk.Menu(bar, tearoff=0)
        help_m.add_command(label=t("about"), command=self.show_about)
        bar.add_cascade(label=t("help"), menu=help_m)
        self.config(menu=bar)

    def _toolbar(self):
        frame = tk.Frame(self, bd=1, relief=tk.RAISED)
        frame.pack(side=tk.TOP, fill=tk.X)
        for text, cmd in (
            (t("open"), self.open_file),
            (t("save"), self.save_file),
            (t("toolbar_encrypt"), self.encrypt),
            (t("toolbar_decrypt"), self.decrypt),
            (t("show_grid"), self.show_grid),
        ):
            tk.Button(frame, text=text, command=cmd).pack(side=tk.LEFT, padx=2, pady=2)

    def _body(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(top, text=t("mode")).grid(row=0, column=0, sticky="w")
        self.mode = ttk.Combobox(
            top,
            values=[t("mode_verse"), t("mode_word")],
            state="readonly",
            width=32,
        )
        self.mode.current(0)
        self.mode.grid(row=0, column=1, sticky="w", padx=4)

        tk.Label(top, text=t("width")).grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.width_var = tk.StringVar(value="10")
        tk.Entry(top, textvariable=self.width_var, width=6).grid(row=0, column=3, padx=4)

        tk.Label(self, text=t("poem")).pack(anchor="w", padx=8)
        self.poem = tk.Text(self, height=6)
        self.poem.pack(fill=tk.X, padx=8, pady=4)
        self.poem.insert("1.0", DEFAULT_POEM)

        tk.Label(self, text=t("text")).pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=10)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text=t("result")).pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=8)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _poem_text(self) -> str:
        return self.poem.get("1.0", tk.END).rstrip("\n")

    def new_file(self):
        self.path = None
        self.input.delete("1.0", tk.END)
        self.output.delete("1.0", tk.END)

    def open_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.input.delete("1.0", tk.END)
            self.input.insert("1.0", text)
            self.path = path
        except OSError:
            messagebox.showerror(t("app_title"), t("err_open"))

    def save_file(self):
        if not self.path:
            self.save_as()
            return
        self._write(self.path)

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        self.path = path
        self._write(path)

    def _write(self, path: str):
        try:
            data = self.output.get("1.0", tk.END).rstrip("\n")
            if not data:
                data = self.input.get("1.0", tk.END).rstrip("\n")
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            messagebox.showinfo(t("app_title"), t("saved"))
        except OSError:
            messagebox.showerror(t("app_title"), t("err_save"))

    def print_file(self):
        data = self.output.get("1.0", tk.END).strip() or self.input.get("1.0", tk.END)
        tmp = os.path.join(tempfile.gettempdir(), t("untitled"))
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
        try:
            os.startfile(tmp, "print")
        except OSError:
            messagebox.showinfo(t("app_title"), tmp)

    def show_about(self):
        messagebox.showinfo(t("about"), t("about_text"))

    def show_grid(self):
        try:
            key = self.verse.validate_key(self._poem_text(), self.width_var.get())
        except ValueError:
            messagebox.showerror(t("app_title"), t("err_key"))
            return
        win = tk.Toplevel(self)
        win.title(t("grid_title"))
        box = tk.Text(win, width=70, height=20, font=("Consolas", 11))
        box.pack(fill=tk.BOTH, expand=True)
        box.insert("1.0", key.as_text())

    def encrypt(self):
        self._run(True)

    def decrypt(self):
        self._run(False)

    def _run(self, enc: bool):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        poem = self._poem_text()
        try:
            if self.mode.current() == 0:
                result = (
                    self.verse.encrypt(text, poem, self.width_var.get())
                    if enc
                    else self.verse.decrypt(text, poem, self.width_var.get())
                )
            else:
                result = (
                    self.word.encrypt(text, poem)
                    if enc
                    else self.word.decrypt(text, poem)
                )
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except ValueError:
            messagebox.showerror(t("app_title"), t("err_data"))


if __name__ == "__main__":
    App().mainloop()
