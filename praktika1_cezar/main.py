import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto import BruteForceAttack, CaesarCipher, EN_ALPHABET, UA_ALPHABET
from strings import t


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(t("app_title"))
        self.geometry("780x540")
        self.path = None
        self.binary = None
        self.caesar = CaesarCipher()
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
        cipher_m.add_command(label=t("brute"), command=self.brute_force)
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
        ):
            tk.Button(frame, text=text, command=cmd).pack(side=tk.LEFT, padx=2, pady=2)

    def _body(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(top, text=t("alphabet")).grid(row=0, column=0, sticky="w")
        self.lang = ttk.Combobox(
            top, values=[t("lang_ua"), t("lang_en")], state="readonly", width=16
        )
        self.lang.current(0)
        self.lang.grid(row=0, column=1, sticky="w", padx=4)

        tk.Label(top, text=t("key")).grid(row=0, column=2, sticky="w", padx=(16, 0))
        self.key_var = tk.StringVar(value="13")
        tk.Entry(top, textvariable=self.key_var, width=10).grid(row=0, column=3, padx=4)

        tk.Label(self, text=t("text")).pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=12)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text=t("result")).pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=10)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _alphabet(self):
        return UA_ALPHABET if self.lang.current() == 0 else EN_ALPHABET

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
            with open(path, "rb") as f:
                raw = f.read()
            try:
                text = raw.decode("utf-8")
                self.binary = None
                self.input.delete("1.0", tk.END)
                self.input.insert("1.0", text)
            except UnicodeDecodeError:
                self.binary = raw
                self.input.delete("1.0", tk.END)
                self.input.insert(
                    "1.0", t("binary_hint") + f"\n[{len(raw)} bytes] {path}"
                )
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
            if self.binary is not None:
                with open(path, "wb") as f:
                    f.write(self.binary)
            else:
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

    def encrypt(self):
        self._run(True)

    def decrypt(self):
        self._run(False)

    def _run(self, enc: bool):
        key = self.key_var.get()
        ab = self._alphabet()
        try:
            if self.binary is not None:
                out = (
                    self.caesar.encrypt_bytes(self.binary, key)
                    if enc
                    else self.caesar.decrypt_bytes(self.binary, key)
                )
                self.binary = out
                self.output.delete("1.0", tk.END)
                self.output.insert("1.0", f"OK, {len(out)} bytes")
                return
            text = self.input.get("1.0", tk.END).rstrip("\n")
            result = (
                self.caesar.encrypt(text, key, ab)
                if enc
                else self.caesar.decrypt(text, key, ab)
            )
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except ValueError:
            messagebox.showerror(t("app_title"), t("err_key") if not key.strip() else t("err_data"))

    def brute_force(self):
        text = self.input.get("1.0", tk.END).rstrip("\n")
        if not text:
            messagebox.showerror(t("app_title"), t("err_data"))
            return
        win = tk.Toplevel(self)
        win.title(t("brute_title"))
        box = tk.Text(win, width=80, height=24)
        box.pack(fill=tk.BOTH, expand=True)
        for k, val in BruteForceAttack().run(text, self._alphabet()):
            box.insert(tk.END, f"k={k}: {val}\n")


if __name__ == "__main__":
    App().mainloop()
