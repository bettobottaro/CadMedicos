import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from tkinter import filedialog
from ui_utils import center_window


class EmailConfigForm(tk.Toplevel):
    """Formulário de configuração de e-mails."""

    @staticmethod
    def _get_base_dir() -> str:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(os.path.abspath(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def get_config_file_path(cls) -> str:
        base_dir = cls._get_base_dir()
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "email_config.json")


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

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuração de E-mails")
        self.geometry("720x520")
        self.minsize(620, 420)
        self.resizable(True, True)
        
        self.config_data = self._load_config()
        
        self._create_widgets()
        self._load_form_data()
        
        self.transient(parent)
        self.grab_set()
        
        # Centralizar janela
        center_window(self)
    
    def _create_widgets(self):
        """Cria o formulário com área central rolável e botões fixos no rodapé."""
        # A janela fica deliberadamente mais baixa para caber em telas pequenas.
        self.geometry("720x520")
        self.minsize(620, 420)

        outer = ttk.Frame(self, padding=5)
        outer.pack(fill=tk.BOTH, expand=True)

        # Área central: somente esta área rola.
        center = ttk.Frame(outer)
        center.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(center, highlightthickness=0, borderwidth=0)
        vbar = ttk.Scrollbar(center, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = ttk.Frame(canvas, padding=(4, 2, 10, 6))
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def _on_content_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)

        content.bind("<Configure>", _on_content_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel sobre a área central.
        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _wheel)

        main_frame = content

        # ===== REMETENTE =====
        ttk.Label(main_frame, text="Configuração de Remetente",
                  font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(0, 3))

        sender_frame = ttk.LabelFrame(main_frame, text="Dados do Remetente", padding=5)
        sender_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(sender_frame, text="E-mail:").grid(row=0, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        self.sender_email_var = tk.StringVar()
        ttk.Entry(sender_frame, textvariable=self.sender_email_var).grid(row=0, column=1, sticky=tk.EW, padx=(0, 8), pady=1)

        ttk.Label(sender_frame, text="Responder para:").grid(row=0, column=2, sticky=tk.W, padx=(0, 4), pady=1)
        self.reply_to_var = tk.StringVar()
        ttk.Entry(sender_frame, textvariable=self.reply_to_var).grid(row=0, column=3, sticky=tk.EW, pady=1)

        ttk.Label(sender_frame, text="Senha/Token (legado):").grid(row=1, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        self.password_var = tk.StringVar()
        ttk.Entry(sender_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, sticky=tk.EW, padx=(0, 8), pady=1)

        sender_frame.columnconfigure(1, weight=1)
        sender_frame.columnconfigure(3, weight=1)

        # ===== SERVIDOR =====
        ttk.Label(main_frame, text="Configuração do Servidor SMTP",
                  font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(2, 3))

        server_frame = ttk.LabelFrame(main_frame, text="Servidor SMTP", padding=5)
        server_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(server_frame, text="Servidor:").grid(row=0, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        self.server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(server_frame, textvariable=self.server_var).grid(row=0, column=1, sticky=tk.EW, padx=(0, 8), pady=1)

        ttk.Label(server_frame, text="Porta:").grid(row=0, column=2, sticky=tk.W, padx=(0, 4), pady=1)
        self.port_var = tk.StringVar(value="587")
        ttk.Entry(server_frame, textvariable=self.port_var, width=8).grid(row=0, column=3, sticky=tk.W, pady=1)

        self.use_ssl_var = tk.BooleanVar(value=False)
        self.requires_auth_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(server_frame, text="SSL direto", variable=self.use_ssl_var).grid(row=1, column=1, sticky=tk.W, padx=2, pady=1)
        ttk.Checkbutton(server_frame, text="Requer autenticação", variable=self.requires_auth_var).grid(row=1, column=3, sticky=tk.W, padx=2, pady=1)

        ttk.Label(server_frame, text="Autenticação:").grid(row=2, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        self.auth_method_var = tk.StringVar(value="oauth2")
        self.auth_method_combo = ttk.Combobox(
            server_frame, textvariable=self.auth_method_var,
            values=("oauth2", "senha/token"), state="readonly", width=18)
        self.auth_method_combo.grid(row=2, column=1, sticky=tk.W, padx=(0, 8), pady=1)

        ttk.Label(server_frame, text="Credentials OAuth2:").grid(row=3, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        self.oauth_credentials_var = tk.StringVar()
        ttk.Entry(server_frame, textvariable=self.oauth_credentials_var).grid(
            row=3, column=1, columnspan=2, sticky=tk.EW, padx=(0, 4), pady=1)
        ttk.Button(server_frame, text="Procurar...", command=self._browse_credentials).grid(
            row=3, column=3, sticky=tk.W, pady=1)

        ttk.Label(server_frame, text="Token OAuth2:").grid(row=4, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        self.oauth_token_var = tk.StringVar()
        ttk.Entry(server_frame, textvariable=self.oauth_token_var).grid(
            row=4, column=1, columnspan=2, sticky=tk.EW, padx=(0, 4), pady=1)
        ttk.Button(server_frame, text="Procurar...", command=self._browse_token).grid(
            row=4, column=3, sticky=tk.W, pady=1)

        ttk.Label(server_frame, text="Gmail: porta 587 + STARTTLS + OAuth2/XOAUTH2",
                  font=("Arial", 8, "italic")).grid(row=5, column=0, columnspan=4, sticky=tk.W, pady=(2, 0))

        server_frame.columnconfigure(1, weight=1)
        server_frame.columnconfigure(2, weight=1)

        # ===== TEMPLATE =====
        ttk.Label(main_frame, text="Template de E-mail",
                  font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(2, 3))

        template_frame = ttk.LabelFrame(main_frame, text="Configurar Template", padding=5)
        template_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(template_frame, text="Assunto:").pack(fill=tk.X, pady=(0, 1))
        self.subject_var = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.subject_var).pack(fill=tk.X, pady=(0, 3))

        ttk.Label(template_frame, text="Texto Padrão:").pack(fill=tk.X, pady=(0, 1))
        ttk.Label(
            template_frame,
            text="Use [Terceiro] para o nome do terceiro e [Valor_bruto] para um valor a ser preenchido no envio.",
            font=("Arial", 8, "italic"), wraplength=620
        ).pack(fill=tk.X, pady=(0, 3))

        text_frame = ttk.Frame(template_frame)
        text_frame.pack(fill=tk.X)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_var = tk.Text(
            text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
            height=5
        )
        self.text_var.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.text_var.yview)

        # ===== AJUDA =====
        help_frame = ttk.Frame(main_frame)
        help_frame.pack(fill=tk.X, pady=(2, 4))

        ttk.Label(help_frame, text="Variáveis disponíveis:",
                  font=("Arial", 9, "bold")).pack(anchor=tk.W)
        ttk.Label(help_frame, text="[Terceiro] - Será substituída pelo nome do terceiro selecionado",
                  font=("Arial", 8), wraplength=620).pack(anchor=tk.W)
        ttk.Label(help_frame, text="[Valor_bruto] - Será preenchida quando você enviar o e-mail",
                  font=("Arial", 8), wraplength=620).pack(anchor=tk.W)

        # Rodapé FIXO: não participa do scroll.
        button_frame = ttk.Frame(outer, padding=(4, 5, 4, 2))
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Separator(button_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(button_frame, text="Salvar", command=self._save_config).pack(
            side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(
            side=tk.RIGHT)

    def _browse_credentials(self):
        path = filedialog.askopenfilename(parent=self, title="Selecionar credentials.json", filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if path:
            self.oauth_credentials_var.set(path)

    def _browse_token(self):
        path = filedialog.askopenfilename(parent=self, title="Selecionar token OAuth2", filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if path:
            self.oauth_token_var.set(path)

    def _load_config(self) -> dict:
        """Carrega a configuração do arquivo JSON."""
        config_path = self.get_config_file_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")

        return {
            "sender_email": "",
            "reply_to": "",
            "password": "",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": "587",
            "smtp_use_ssl": False,
            "smtp_requires_auth": True,
            "auth_method": "oauth2",
            "oauth_credentials_file": "",
            "oauth_token_file": "",
            "subject_template": "",
            "text_template": ""
        }
    
    def _load_form_data(self):
        """Carrega os dados no formulário."""
        self.sender_email_var.set(self.config_data.get("sender_email", ""))
        self.reply_to_var.set(self.config_data.get("reply_to", ""))
        self.password_var.set(self.config_data.get("password", ""))
        self.server_var.set(self.config_data.get("smtp_server", "smtp.gmail.com"))
        self.port_var.set(self.config_data.get("smtp_port", "587"))
        self.use_ssl_var.set(bool(self.config_data.get("smtp_use_ssl", False)))
        self.requires_auth_var.set(bool(self.config_data.get("smtp_requires_auth", True)))
        self.auth_method_var.set(self.config_data.get("auth_method", "oauth2"))
        self.oauth_credentials_var.set(self.config_data.get("oauth_credentials_file", ""))
        self.oauth_token_var.set(self.config_data.get("oauth_token_file", ""))
        self.subject_var.set(self.config_data.get("subject_template", ""))
        self.text_var.insert(tk.END, self.config_data.get("text_template", ""))
    
    def _save_config(self):
        """Salva a configuração no arquivo JSON."""
        sender_email = self.sender_email_var.get().strip()
        
        auth_method = self.auth_method_var.get().strip().lower()
        if not sender_email:
            messagebox.showwarning("Campos vazios", "Preencha o e-mail do remetente.")
            return
        if auth_method == "oauth2" and not self.oauth_credentials_var.get().strip():
            messagebox.showwarning("OAuth2", "Informe o arquivo de credenciais OAuth2 (credentials.json).")
            return
        if auth_method != "oauth2" and not self.password_var.get().strip():
            messagebox.showwarning("Campos vazios", "Preencha a senha/token.")
            return
        
        config = {
            "sender_email": sender_email,
            "reply_to": self.reply_to_var.get().strip(),
            "password": self.password_var.get().strip(),
            "smtp_server": self.server_var.get().strip() or "smtp.gmail.com",
            "smtp_port": self.port_var.get().strip() or "587",
            "smtp_use_ssl": bool(self.use_ssl_var.get()),
            "smtp_requires_auth": bool(self.requires_auth_var.get()),
            "auth_method": auth_method,
            "oauth_credentials_file": self.oauth_credentials_var.get().strip(),
            "oauth_token_file": self.oauth_token_var.get().strip(),
            "subject_template": self.subject_var.get().strip(),
            "text_template": self.text_var.get(1.0, tk.END).strip()
        }
        
        config_path = self.get_config_file_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {str(e)}")

    @staticmethod
    def get_config() -> dict:
        """Obtém a configuração salva."""
        config_file = EmailConfigForm.get_config_file_path()
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")

        return {}
