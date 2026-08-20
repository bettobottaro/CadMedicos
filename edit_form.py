import tkinter as tk
from tkinter import ttk, messagebox

from models import MedicoRecord, TerceiroRecord
from ui_utils import center_window


class EditForm(tk.Toplevel):

    def _ajustar_formulario_tela(self, largura=650, altura=600):
        """Mantém o formulário dentro da área visível da tela."""
        try:
            self.update_idletasks()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            w = min(largura, max(480, sw - 30))
            h = min(altura, max(420, sh - 70))
            x = max(5, (sw - w) // 2)
            y = max(5, (sh - h) // 2)
            self.geometry("{}x{}+{}+{}".format(w, h, x, y))
            self.minsize(min(w, 480), min(h, 420))
        except Exception:
            pass

    def __init__(self, parent, record: MedicoRecord, callback, title="Editar Médico", terceiro_options=None, especialidade_options=None):
        super().__init__(parent)
        self.record = record
        self.callback = callback
        self.terceiro_options = sorted({value.strip() for value in (terceiro_options or []) if value and value.strip()})
        self.especialidade_options = sorted({value.strip() for value in (especialidade_options or []) if value and value.strip()}, key=lambda x: x.lower())
        self.title(title)
        self.geometry("560x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_data()
        center_window(self)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Terceiro*", "terceiro"),
            ("Médico*", "medico"),
            ("Especialidade", "especialidade"),
            ("Observações", "obs"),
        ]
        self.entries = {}

        for label_text, field_name in fields:
            row_frame = ttk.Frame(main_frame)
            row_frame.pack(fill=tk.X, pady=5)
            ttk.Label(row_frame, text=label_text, width=15, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))

            if field_name == "terceiro":
                widget = ttk.Combobox(row_frame, values=self.terceiro_options, width=48)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif field_name == "especialidade":
                # Combobox editável: lista as especialidades já cadastradas,
                # mas permite digitar uma nova.
                widget = ttk.Combobox(row_frame, values=self.especialidade_options, width=48, state="normal")
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif field_name == "obs":
                text_frame = ttk.Frame(row_frame)
                text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                widget = tk.Text(text_frame, height=5, width=40, wrap=tk.WORD)
                widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=widget.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                widget.configure(yscrollcommand=scrollbar.set)
            else:
                widget = ttk.Entry(row_frame, width=50)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field_name] = widget

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="Salvar", command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_data(self):
        self.entries["terceiro"].set(self.record.terceiro)
        self.entries["medico"].insert(0, self.record.medico)
        self.entries["especialidade"].set(self.record.especialidade)
        self.entries["obs"].insert("1.0", self.record.obs)

    def _on_save(self):
        novo_terceiro = self.entries["terceiro"].get().strip()
        novo_medico = self.entries["medico"].get().strip()
        nova_especialidade = self.entries["especialidade"].get().strip()

        if not novo_terceiro:
            messagebox.showerror("Erro", "Campo 'Terceiro' é obrigatório!")
            return
        if not novo_medico:
            messagebox.showerror("Erro", "Campo 'Médico' é obrigatório!")
            return

        self.record.terceiro = novo_terceiro[:150]
        self.record.medico = novo_medico[:150]
        self.record.especialidade = nova_especialidade[:100]
        self.record.obs = self.entries["obs"].get("1.0", tk.END).strip()[:250]

        self.callback(self.record)
        self.destroy()


class AddForm(EditForm):
    def __init__(self, parent, callback, terceiro_options=None, especialidade_options=None):
        record = MedicoRecord()
        super().__init__(parent, record, callback, title="Novo Médico", terceiro_options=terceiro_options,
                         especialidade_options=especialidade_options)


class TerceiroForm(tk.Toplevel):
    def __init__(self, parent, record: TerceiroRecord, callback, title="Editar Terceiro"):
        super().__init__(parent)
        self.record = record
        self.callback = callback
        self.title(title)
        self.geometry("500x330")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_data()
        center_window(self)

    def _create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Nome*", "nome"),
            ("Contato", "contato"),
            ("Email", "email"),
        ]
        self.entries = {}
        for label_text, field_name in fields:
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=5)
            ttk.Label(row, text=label_text, width=12, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))
            entry = ttk.Entry(row, width=42)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field_name] = entry

        row = ttk.Frame(frame)
        row.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(row, text="Observações", width=12, anchor=tk.NW).pack(side=tk.LEFT, padx=(0, 5))
        text_frame = ttk.Frame(row)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entries["obs"] = tk.Text(text_frame, height=6, width=42, wrap=tk.WORD)
        self.entries["obs"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.entries["obs"].yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entries["obs"].configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(button_frame, text="Salvar", command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_data(self):
        self.entries["nome"].insert(0, self.record.nome)
        self.entries["contato"].insert(0, self.record.contato)
        self.entries["email"].insert(0, self.record.email)
        self.entries["obs"].insert("1.0", self.record.obs)

    def _on_save(self):
        nome = self.entries["nome"].get().strip()
        if not nome:
            messagebox.showerror("Erro", "Campo 'Nome' é obrigatório!")
            return

        self.record.nome = nome[:150]
        self.record.contato = self.entries["contato"].get().strip()[:50]
        self.record.email = self.entries["email"].get().strip()[:100]
        self.record.obs = self.entries["obs"].get("1.0", tk.END).strip()[:250]

        self.callback(self.record)
        self.destroy()
