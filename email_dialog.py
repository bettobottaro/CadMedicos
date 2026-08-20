import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from email_sender import EmailSender
from email_config import EmailConfigForm
from ui_utils import center_window


class EmailConfigDialog(tk.Toplevel):
    """Diálogo para configurar credenciais de e-mail."""
    

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

    def __init__(self, parent, on_config=None):
        super().__init__(parent)
        self.title("Configuração de E-mail")
        self.geometry("400x200")
        self.resizable(False, False)
        self.on_config = on_config
        self.result = None
        
        # E-mail do remetente
        ttk.Label(self, text="E-mail:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var, width=40).grid(row=0, column=1, padx=10, pady=10)
        
        # Senha/Token
        ttk.Label(self, text="Senha/Token:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.password_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.password_var, width=40, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        # Servidor SMTP
        ttk.Label(self, text="Servidor SMTP:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(self, textvariable=self.server_var, width=40).grid(row=2, column=1, padx=10, pady=10)
        
        # Botões
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Salvar", command=self._on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self.transient(parent)
        self.grab_set()
    
    def _on_save(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        server = self.server_var.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Campos vazios", "Preencha e-mail e senha/token.")
            return
        
        self.result = (email, password, server)
        if self.on_config:
            self.on_config(self.result)
        self.destroy()


class EmailDialog(tk.Toplevel):
    """Diálogo para enviar e-mail com template e anexos."""
    
    def __init__(self, parent, recipient_email: str, terceiro_name: str = "", valor_bruto: str = ""):
        super().__init__(parent)
        self.title(f"Enviar E-mail para {recipient_email}")
        self.geometry("700x600")
        self.resizable(True, True)
        
        self.recipient_email = recipient_email
        self.terceiro_name = terceiro_name
        self.valor_bruto = valor_bruto
        self.attachments = []
        
        # Carregar configuração
        from email_config import EmailConfigForm
        self.config = EmailConfigForm.get_config()
        
        # Se não há configuração, solicitar
        if not self.config or not self.config.get("sender_email"):
            messagebox.showwarning("Configuração", "Configure suas credenciais de e-mail primeiro.")
            self.destroy()
            return
        
        self._create_widgets()
        self._load_template()
        
        self.transient(parent)
        self.grab_set()
        
        # Centralizar janela
        center_window(self)
    
    def _create_widgets(self):
        """Cria os widgets do diálogo."""
        # Assunto
        ttk.Label(self, text="Assunto:").pack(fill=tk.X, padx=10, pady=(10, 0))
        self.subject_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.subject_var, width=80).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Corpo do e-mail
        ttk.Label(self, text="Mensagem:").pack(fill=tk.X, padx=10, pady=(10, 0))
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_var = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15)
        self.text_var.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_var.yview)

        copy_frame = ttk.Frame(self)
        copy_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        ttk.Button(copy_frame, text="Copiar", command=self._copy_body).pack(side=tk.LEFT)
        
        # Anexos
        ttk.Label(self, text="Anexos:").pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.attachments_frame = ttk.Frame(self)
        self.attachments_frame.pack(fill=tk.BOTH, padx=10, pady=(0, 5))
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="Adicionar Anexo", command=self._add_attachment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar Anexos", command=self._clear_attachments).pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(action_frame, text="Enviar", command=self._send_email).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self._update_attachments_display()
    
    def _load_template(self):
        """Carrega o template de e-mail da configuração."""
        from datetime import datetime
        
        subject_template = self.config.get("subject_template", "")
        text_template = self.config.get("text_template", "")
        
        # Processar variável [Terceiro]
        subject = subject_template.replace("[Terceiro]", self.terceiro_name)
        text = text_template.replace("[Terceiro]", self.terceiro_name)
        
        # Processar variável [Valor_bruto]
        if self.valor_bruto:
            text = text.replace("[Valor_bruto]", self.valor_bruto)
        
        # Determinar saudação conforme hora
        hora = datetime.now().hour
        if 0 <= hora < 12:
            saudacao = f"Bom dia, {self.terceiro_name}."
        elif 12 <= hora < 18:
            saudacao = f"Boa tarde, {self.terceiro_name}."
        else:
            saudacao = f"Boa noite, {self.terceiro_name}."
        
        # Adicionar saudação no início se o texto não começar com ela
        if not text.startswith(("Bom dia", "Boa tarde", "Boa noite")):
            text = saudacao + "\n\n" + text
        
        self.subject_var.set(subject)
        self.text_var.insert(tk.END, text)
    
    def _process_template(self, text: str) -> str:
        """Processa variáveis no template de texto."""
        # [Valor_bruto] já foi processado em _load_template
        # Apenas certificar que não há placeholders não preenchidos
        if "[Valor_bruto]" in text and not self.valor_bruto:
            messagebox.showwarning("Valor ausente", "Preencha o valor para [Valor_bruto] antes de enviar.")
            return None
        
        return text
    
    def _copy_body(self):
        """Copia o texto completo da mensagem para a área de transferência."""
        try:
            body = self.text_var.get("1.0", tk.END).rstrip("\n")
            self.clipboard_clear()
            self.clipboard_append(body)
            self.update()
            messagebox.showinfo("Copiar", "Texto do e-mail copiado para a área de transferência.")
        except Exception as e:
            messagebox.showerror("Copiar", "Não foi possível copiar o texto: " + str(e))

    def _add_attachment(self):
        file_path = filedialog.askopenfilename(title="Selecionar arquivo para anexar")
        if file_path:
            self.attachments.append(file_path)
            self._update_attachments_display()
    
    def _clear_attachments(self):
        self.attachments.clear()
        self._update_attachments_display()
    
    def _update_attachments_display(self):
        for widget in self.attachments_frame.winfo_children():
            widget.destroy()
        
        if not self.attachments:
            ttk.Label(self.attachments_frame, text="Nenhum anexo").pack(anchor=tk.W)
        else:
            for i, file_path in enumerate(self.attachments):
                frame = ttk.Frame(self.attachments_frame)
                frame.pack(fill=tk.X, pady=2)
                ttk.Label(frame, text=f"• {file_path}").pack(side=tk.LEFT, expand=True)
                ttk.Button(
                    frame,
                    text="Remover",
                    width=8,
                    command=lambda idx=i: self._remove_attachment(idx)
                ).pack(side=tk.RIGHT)
    
    def _remove_attachment(self, index: int):
        if 0 <= index < len(self.attachments):
            self.attachments.pop(index)
            self._update_attachments_display()
    
    def _send_email(self):
        subject = self.subject_var.get().strip()
        body = self.text_var.get(1.0, tk.END).strip()
        
        if not subject or not body:
            messagebox.showwarning("Campos vazios", "Preencha assunto e mensagem.")
            return
        
        # Processar variáveis no corpo
        body = self._process_template(body)
        if body is None:  # Cancelado
            return
        
        try:
            sender = EmailSender(
                self.config.get("sender_email"),
                self.config.get("password")
            )
            sender.SMTP_SERVER = self.config.get("smtp_server", "smtp.gmail.com")
            sender.SMTP_PORT = int(self.config.get("smtp_port", "465"))
            sender.USE_SSL = bool(self.config.get("smtp_use_ssl", True))
            sender.REQUIRES_AUTH = bool(self.config.get("smtp_requires_auth", True))

            success, message = sender.send_email(
                self.recipient_email,
                subject,
                body,
                self.attachments if self.attachments else None
            )
            
            if success:
                messagebox.showinfo("Sucesso", message)
                self.destroy()
            else:
                messagebox.showerror("Erro", message)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar: {str(e)}")


class ValueInputDialog(tk.Toplevel):
    """Entrada de valor monetário, sem o prefixo R$.

    O valor é exibido no padrão brasileiro 1.234,56 e o último valor pode
    ser usado como sugestão pelo chamador.
    """
    def __init__(self, parent, title: str, message: str, initial_value: str = ""):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x145")
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text=message).pack(padx=10, pady=(10, 5))
        self.entry_var = tk.StringVar()
        self.entry_widget = ttk.Entry(self, textvariable=self.entry_var, width=28, justify=tk.RIGHT)
        self.entry_widget.pack(padx=10, pady=(0, 10))
        self.entry_widget.insert(0, self._format_money(initial_value))
        self.entry_widget.bind("<KeyRelease>", self._on_key_release)
        self.entry_widget.bind("<Return>", lambda event: self._ok())
        self.entry_widget.bind("<Escape>", lambda event: self._cancel())

        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=5)
        ttk.Button(button_frame, text="OK", command=self._ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self._cancel).pack(side=tk.LEFT, padx=5)

        self.transient(parent)
        self.grab_set()
        self.after(100, self.entry_widget.focus_set)
        self.entry_widget.selection_range(0, tk.END)
        center_window(self)

    @staticmethod
    def _digits_to_money(text: str) -> str:
        digits = ''.join(ch for ch in str(text or '') if ch.isdigit())
        if not digits:
            return ''
        digits = digits.lstrip('0') or '0'
        if len(digits) == 1:
            digits = '0' + digits
        cents = digits[-2:]
        integer = digits[:-2] or '0'
        groups = []
        while integer:
            groups.insert(0, integer[-3:])
            integer = integer[:-3]
        return '.'.join(groups) + ',' + cents

    @classmethod
    def _format_money(cls, value: str) -> str:
        if value is None:
            return ''
        text = str(value).strip()
        if not text:
            return ''
        return cls._digits_to_money(text)

    def _on_key_release(self, event=None):
        current = self.entry_var.get()
        formatted = self._digits_to_money(current)
        self.entry_var.set(formatted)
        self.entry_widget.icursor(tk.END)

    def _ok(self):
        value = self._digits_to_money(self.entry_var.get())
        if not value:
            messagebox.showwarning("Valor", "Informe um valor monetário.")
            return
        self.result = value
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
