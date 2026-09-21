import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto import EN_ALPHABET, KnownPlaintextAttack, TrithemiusCipher, UA_ALPHABET
from strings import t


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(t("app_title"))
        self.geometry("820x560")
        self.path = None
        self.binary = None
        self.cipher = TrithemiusCipher()
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
        cipher_m.add_command(label=t("known_attack"), command=self.known_attack)
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

        tk.Label(top, text=t("mode")).grid(row=0, column=0, sticky="w")
        self.mode = ttk.Combobox(
            top,
            values=[t("mode_linear"), t("mode_nonlinear"), t("mode_motto")],
            state="readonly",
            width=24,
        )
        self.mode.current(0)
        self.mode.grid(row=0, column=1, sticky="w", padx=4)

        tk.Label(top, text=t("alphabet")).grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.lang = ttk.Combobox(
            top, values=[t("lang_ua"), t("lang_en")], state="readonly", width=14
        )
        self.lang.current(0)
        self.lang.grid(row=0, column=3, sticky="w", padx=4)

        tk.Label(top, text=t("key")).grid(row=1, column=0, sticky="w", pady=6)
        self.key_var = tk.StringVar(value="2,5")
        tk.Entry(top, textvariable=self.key_var, width=40).grid(
            row=1, column=1, columnspan=3, sticky="we", padx=4, pady=6
        )
        tk.Label(top, text=t("key_hint"), fg="#555").grid(
            row=2, column=1, columnspan=3, sticky="w"
        )

        tk.Label(self, text=t("text")).pack(anchor="w", padx=8)
        self.input = tk.Text(self, height=12)
        self.input.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        tk.Label(self, text=t("result")).pack(anchor="w", padx=8)
        self.output = tk.Text(self, height=10)
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _alphabet(self):
        return UA_ALPHABET if self.lang.current() == 0 else EN_ALPHABET

    def _mode_id(self) -> str:
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
        mode = self._mode_id()
        ab = self._alphabet()
        try:
            if self.binary is not None:
                out = (
                    self.cipher.encrypt_bytes(self.binary, mode, key)
                    if enc
                    else self.cipher.decrypt_bytes(self.binary, mode, key)
                )
                self.binary = out
                self.output.delete("1.0", tk.END)
                self.output.insert("1.0", f"OK, {len(out)} bytes")
                return
            text = self.input.get("1.0", tk.END).rstrip("\n")
            result = (
                self.cipher.encrypt(text, mode, key, ab)
                if enc
                else self.cipher.decrypt(text, mode, key, ab)
            )
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", result)
        except ValueError:
            messagebox.showerror(
                t("app_title"), t("err_key") if not key.strip() else t("err_data")
            )

    def known_attack(self):
        win = tk.Toplevel(self)
        win.title(t("attack_title"))
        tk.Label(win, text=t("plain")).pack(anchor="w")
        plain = tk.Text(win, height=5, width=70)
        plain.pack()
        tk.Label(win, text=t("cipher_text")).pack(anchor="w")
        cipher = tk.Text(win, height=5, width=70)
        cipher.pack()
        mode_var = ttk.Combobox(
            win,
            values=[t("mode_linear"), t("mode_nonlinear"), t("mode_motto")],
            state="readonly",
        )
        mode_var.current(0)
        mode_var.pack(pady=4)
        out = tk.Label(win, text="", justify="left")
        out.pack(pady=4)

        def go():
            mid = ["linear", "nonlinear", "motto"][mode_var.current()]
            try:
                key = KnownPlaintextAttack().recover(
                    plain.get("1.0", tk.END).rstrip("\n"),
                    cipher.get("1.0", tk.END).rstrip("\n"),
                    mid,
                    self._alphabet(),
                )
                out.config(text=f"{t('key')}: {key}")
                self.key_var.set(
                    ",".join(map(str, key)) if isinstance(key, list) else str(key)
                )
            except ValueError:
                out.config(text=t("err_data"))

        tk.Button(win, text=t("find_key"), command=go).pack(pady=6)


if __name__ == "__main__":
    App().mainloop()
