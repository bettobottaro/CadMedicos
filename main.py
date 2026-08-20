import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from models import DataManager, MedicoRecord, TerceiroRecord
from edit_form import AddForm, EditForm, TerceiroForm
from especialidades_window import EspecialidadesWindow
from email_config import EmailConfigForm
from email_dialog import EmailDialog, ValueInputDialog


class CadMedicosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CadMedicos - Cadastro de Médicos")
        self.root.geometry("1100x600")
        self.root.minsize(900, 500)

        # Fonte das células dos dois painéis, ligeiramente maior para facilitar a leitura.
        style = ttk.Style(self.root)
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Right.Treeview", font=("Segoe UI", 11), rowheight=24)
        style.configure("Right.Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.data_manager = DataManager()
        self.highlight_color = "#8B0000"  # vermelho escuro para especialidade suplementada
        self.check_image = self._load_check_image()
        self.records = []
        self.filtered_records = []
        self.left_records = []
        self.selected_index = -1
        self.selected_terceiro = ""

        self._create_menu()
        self._create_main_layout()
        self._load_data()
        self._apply_filters()

        # Centraliza depois que a janela estiver pronta.
        self.root.after(100, self._center_window)

        self._center_window()
        
    def _center_window(self):
        """Centraliza a janela principal na tela."""
        self.root.update_idletasks()

        largura = self.root.winfo_width()
        altura = self.root.winfo_height()

        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()

        pos_x = (largura_tela - largura) // 2
        pos_y = (altura_tela - altura) // 2

        self.root.geometry(
            f"{largura}x{altura}+{pos_x}+{pos_y}"
        )       


    def _create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Importar (XLS/XLSX/CSV)", command=self._on_import)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar CSV", command=self._on_export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        cadastro_menu = tk.Menu(menubar, tearoff=0)
        cadastro_menu.add_command(label="Especialidades Suplementadas", command=self._on_especialidades)
        cadastro_menu.add_separator()
        cadastro_menu.add_command(label="Config. E-mails", command=self._on_email_config)
        menubar.add_cascade(label="Cadastros", menu=cadastro_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self._on_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

        self.root.config(menu=menubar)

    def _create_main_layout(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._create_left_panel(main_paned)
        self._create_right_panel(main_paned)

        self._create_filter_bar()
        self._create_status_bar()

    def _create_filter_bar(self):
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(filter_frame, text="Filtros:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(filter_frame, text="Terceiro:").pack(side=tk.LEFT)
        self.terceiro_filter = ttk.Entry(filter_frame, width=25)
        self.terceiro_filter.pack(side=tk.LEFT, padx=(5, 15))
        self.terceiro_filter.bind("<KeyRelease>", lambda event: self._apply_filters())

        ttk.Label(filter_frame, text="Médico:").pack(side=tk.LEFT)
        self.medico_filter = ttk.Entry(filter_frame, width=25)
        self.medico_filter.pack(side=tk.LEFT, padx=(5, 15))
        self.medico_filter.bind("<KeyRelease>", lambda event: self._apply_filters())

        ttk.Label(filter_frame, text="Especialidade:").pack(side=tk.LEFT)
        self.especialidade_filter = ttk.Entry(filter_frame, width=22)
        self.especialidade_filter.pack(side=tk.LEFT, padx=(5, 15))
        self.especialidade_filter.bind("<KeyRelease>", lambda event: self._apply_filters())

        self.solic_nf_filter = tk.BooleanVar(value=False)
        self.nf_rec_filter = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Somente Solic NF", variable=self.solic_nf_filter,
                        command=self._apply_filters).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Checkbutton(filter_frame, text="Somente NF Rec", variable=self.nf_rec_filter,
                        command=self._apply_filters).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(filter_frame, text="Limpar Filtros", command=self._clear_filters).pack(side=tk.LEFT, padx=10)

    def _create_left_panel(self, parent):
        left_frame = ttk.LabelFrame(parent, text="Dados do Terceiro", padding="5")
        parent.add(left_frame, weight=1)

        columns = ("solic_nf", "nf_rec", "terceiro", "contato", "email")
        panel_content = ttk.Frame(left_frame)
        panel_content.pack(fill=tk.BOTH, expand=True)

        self.left_tree = ttk.Treeview(panel_content, columns=columns, show="headings", selectmode="browse")
        self.left_tree.heading("solic_nf", text="Solic NF")
        self.left_tree.heading("nf_rec", text="NF Rec")
        self.left_tree.heading("terceiro", text="Terceiro")
        self.left_tree.heading("contato", text="Contato")
        self.left_tree.heading("email", text="Email")
        self.left_tree.column("solic_nf", width=65, minwidth=65, anchor=tk.CENTER, stretch=False)
        self.left_tree.column("nf_rec", width=65, minwidth=65, anchor=tk.CENTER, stretch=False)
        self.left_tree.column("terceiro", width=200, anchor=tk.W)
        self.left_tree.column("contato", width=120, anchor=tk.W)
        self.left_tree.column("email", width=150, anchor=tk.W)
        try:
            self.left_tree.tag_configure("checkbox", font=("Segoe UI Symbol", 11))
        except Exception:
            pass

        scrollbar = ttk.Scrollbar(panel_content, orient=tk.VERTICAL, command=self.left_tree.yview)
        self.left_tree.configure(yscrollcommand=scrollbar.set)
        self.left_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.left_tree.bind("<<TreeviewSelect>>", self._on_left_select)
        self.left_tree.bind("<Double-1>", self._on_left_double_click)
        self.left_tree.bind("<ButtonRelease-1>", self._on_left_click)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=0, pady=(5, 0))
        ttk.Button(button_frame, text="Novo Terceiro", command=self._on_new_terceiro).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Excluir Terceiro", command=self._on_delete_selected_terceiro).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Marcar todos", command=lambda: self._set_all_nf_flags(True)).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(button_frame, text="Desmarcar todos", command=lambda: self._set_all_nf_flags(False)).pack(side=tk.LEFT)

    def _create_right_panel(self, parent):
        right_frame = ttk.LabelFrame(parent, text="Dados do Médico", padding="5")
        parent.add(right_frame, weight=1)

        columns = ("suplementacao", "medico", "especialidade")
        panel_content = ttk.Frame(right_frame)
        panel_content.pack(fill=tk.BOTH, expand=True)

        self.right_tree = ttk.Treeview(panel_content, columns=columns, show="headings", selectmode="browse", style="Right.Treeview")
        self.right_tree.heading("suplementacao", text="Supl")
        self.right_tree.heading("medico", text="Médico")
        self.right_tree.heading("especialidade", text="Especialidade")
        self.right_tree.column("suplementacao", width=55, minwidth=55, anchor=tk.CENTER, stretch=False)
        self.right_tree.column("medico", width=220, anchor=tk.W)
        self.right_tree.column("especialidade", width=220, anchor=tk.W)
        self._configure_highlight_tags()
        self.right_tree.bind("<<TreeviewSelect>>", self._on_right_select)

        scrollbar = ttk.Scrollbar(panel_content, orient=tk.VERTICAL, command=self.right_tree.yview)
        self.right_tree.configure(yscrollcommand=scrollbar.set)
        self.right_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.right_tree.bind("<Double-1>", self._on_right_double_click)

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, padx=0, pady=(5, 0))
        ttk.Button(button_frame, text="Novo Médico", command=self._on_new_record).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Excluir Médico", command=self._on_delete_selected_medico).pack(side=tk.LEFT)

    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

    def _load_data(self):
        self.records = self.data_manager.load_medicos()
        self.data_manager.load_especialidades_suplementadas()

    def _apply_filters(self):
        terceiro_filter = self.terceiro_filter.get().strip()
        medico_filter = self.medico_filter.get().strip()
        especialidade_filter = self.especialidade_filter.get().strip()

        terceiros_all = self.data_manager.load_terceiros()
        terceiro_flags = {
            (t.nome or "").strip().casefold(): t for t in terceiros_all
        }

        self.filtered_records = sorted(
            [
                record for record in self.records
                if record.matches_filter(terceiro_filter, medico_filter, especialidade_filter)
                and (not self.solic_nf_filter.get() or bool(getattr(terceiro_flags.get((record.terceiro or "").strip().casefold()), "solic_nf", False)))
                and (not self.nf_rec_filter.get() or bool(getattr(terceiro_flags.get((record.terceiro or "").strip().casefold()), "nf_rec", False)))
            ],
            key=lambda r: ((r.terceiro or "").strip().casefold(), (r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold()),
        )

        terceiros = sorted(
            self.data_manager.load_terceiros(),
            key=lambda r: (r.nome or "").strip().casefold()
        )

        if medico_filter or especialidade_filter:
            # Quando houver filtro por Médico OU Especialidade, o painel de
            # Terceiros deve refletir TODOS os terceiros que possuem ao menos
            # um registro que satisfaz os filtros. Isso é especialmente
            # importante para o filtro de Especialidade: não podemos manter
            # somente o terceiro que estava previamente selecionado.
            seen = set()
            filtered_terceiros = []
            terceiro_map = {item.nome.strip().casefold(): item for item in terceiros}

            for record in self.filtered_records:
                key = (record.terceiro or '').strip().casefold()
                if key and key not in seen:
                    seen.add(key)
                    terceiro = terceiro_map.get(key)
                    if terceiro is not None:
                        filtered_terceiros.append(terceiro)
                    else:
                        filtered_terceiros.append(TerceiroRecord(nome=record.terceiro))
        elif terceiro_filter:
            filtered_terceiros = [
                item for item in terceiros
                if terceiro_filter.casefold() in (item.nome or '').casefold()
            ]
        else:
            filtered_terceiros = terceiros

        if self.solic_nf_filter.get():
            filtered_terceiros = [r for r in filtered_terceiros if r.solic_nf]
        if self.nf_rec_filter.get():
            filtered_terceiros = [r for r in filtered_terceiros if r.nf_rec]

        self.left_records = sorted(
            filtered_terceiros,
            key=lambda r: (r.nome or "").strip().casefold()
        )
        if self.left_records and self.selected_terceiro:
            if not any(item.nome == self.selected_terceiro for item in self.left_records):
                self.selected_terceiro = self.left_records[0].nome
        elif self.left_records:
            self.selected_terceiro = self.left_records[0].nome
        else:
            self.selected_terceiro = ""

        self._refresh_left_tree()
        self._refresh_right_tree()
        self._update_status()

    def _clear_filters(self):
        self.terceiro_filter.delete(0, tk.END)
        self.medico_filter.delete(0, tk.END)
        self.especialidade_filter.delete(0, tk.END)
        self.solic_nf_filter.set(False)
        self.nf_rec_filter.set(False)
        self._apply_filters()

    def _refresh_left_tree(self):
        self.left_tree.delete(*self.left_tree.get_children())
        for i, record in enumerate(self.left_records):
            self.left_tree.insert(
                "", tk.END, iid=str(i),
                values=(
                    "☑" if record.solic_nf else "☐",
                    "☑" if record.nf_rec else "☐",
                    record.nome, record.contato, record.email
                ),
                tags=("checkbox",)
            )

        if self.left_records:
            target_index = 0
            if self.selected_terceiro:
                for idx, item in enumerate(self.left_records):
                    if item.nome == self.selected_terceiro:
                        target_index = idx
                        break
            self.left_tree.selection_set(str(target_index))
            self.left_tree.focus(str(target_index))
            self.selected_index = target_index
            self.selected_terceiro = self.left_records[target_index].nome
        else:
            self.selected_index = -1
            self.selected_terceiro = ""

    def _load_check_image(self):
        """Carrega o ícone de item checado usado na coluna Supl."""
        try:
            image_path = os.path.join(self.data_manager.data_dir, "check_item.gif")
            if os.path.exists(image_path):
                return tk.PhotoImage(file=image_path)
        except Exception:
            pass
        return None

    def _configure_highlight_tags(self):
        """Configura o vermelho escuro para especialidades suplementadas."""
        try:
            self.right_tree.tag_configure(
                "suplementada",
                background=self.highlight_color,
                foreground="#FFFFFF"
            )
        except Exception:
            pass

    def _refresh_right_tree(self):
        self._configure_highlight_tags()
        self.right_tree.delete(*self.right_tree.get_children())
        if not self.selected_terceiro and self.left_records:
            self.selected_terceiro = self.left_records[0].nome

        right_records = sorted(
            [
                record for record in self.filtered_records
                if record.terceiro == self.selected_terceiro
            ],
            key=lambda r: ((r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold())
        )

        for i, record in enumerate(right_records):
            # A indicação visual de Supl depende exclusivamente da presença
            # da especialidade na tabela Especialidades Suplementadas.
            is_suplementada = self.data_manager.is_especialidade_suplementada(record.especialidade)
            tags = ("suplementada",) if is_suplementada else ()

            self.right_tree.insert(
                "", tk.END, iid=str(i),
                values=(
                    "SIM" if is_suplementada else "",
                    record.medico,
                    record.especialidade
                ),
                tags=tags
            )

        if right_records:
            self.right_tree.selection_set("0")
            self.right_tree.focus("0")
            self.right_tree.see("0")
            self._update_right_selection_style()

    def _on_right_select(self, event=None):
        self._update_right_selection_style()

    def _update_right_selection_style(self):
        """Mantém o vermelho escuro da especialidade suplementada quando selecionada."""
        try:
            style = ttk.Style(self.root)
            selected = self.right_tree.selection()
            if selected:
                tags = self.right_tree.item(selected[0], "tags")
                if "suplementada" in tags:
                    style.map(
                        "Right.Treeview",
                        background=[("selected", self.highlight_color)],
                        foreground=[("selected", "#FFFFFF")]
                    )
                else:
                    style.map(
                        "Right.Treeview",
                        background=[("selected", "#347083")],
                        foreground=[("selected", "#FFFFFF")]
                    )
            else:
                style.map(
                    "Right.Treeview",
                    background=[("selected", "#347083")],
                    foreground=[("selected", "#FFFFFF")]
                )
        except Exception:
            pass

    def _on_left_select(self, event):
        selection = self.left_tree.selection()
        if selection:
            idx = int(selection[0])
            if 0 <= idx < len(self.left_records):
                self.selected_index = idx
                self.selected_terceiro = self.left_records[idx].nome
                self._refresh_right_tree()

    def _on_left_click(self, event):
        item = self.left_tree.identify_row(event.y)
        column = self.left_tree.identify_column(event.x)
        if not item or column not in ("#1", "#2"):
            return
        idx = int(item)
        if idx < 0 or idx >= len(self.left_records):
            return
        record = self.left_records[idx]
        if column == "#1":
            record.solic_nf = not record.solic_nf
            self.data_manager.set_terceiro_nf_flags(record.nome, solic_nf=record.solic_nf)
        else:
            record.nf_rec = not record.nf_rec
            self.data_manager.set_terceiro_nf_flags(record.nome, nf_rec=record.nf_rec)
        self._refresh_left_tree()
        self.status_var.set("Status das NF atualizado")

    def _set_all_nf_flags(self, value):
        self.data_manager.set_all_terceiros_nf_flags(value)
        self.left_records = self._get_filtered_terceiros()
        self._refresh_left_tree()
        self.status_var.set("Solic NF e NF Rec: " + ("marcados" if value else "desmarcados"))

    def _get_filtered_terceiros(self):
        terceiro_filter = self.terceiro_filter.get().strip()
        medico_filter = self.medico_filter.get().strip()
        terceiros = self.data_manager.load_terceiros()
        if medico_filter:
            seen = set()
            result = []
            terceiro_map = {item.nome.strip().lower(): item for item in terceiros}
            for record in self.filtered_records:
                key = record.terceiro.strip().lower()
                if key and key not in seen:
                    seen.add(key)
                    result.append(terceiro_map.get(key, TerceiroRecord(nome=record.terceiro)))
            return sorted(result, key=lambda r: (r.nome or "").strip().casefold())
        if terceiro_filter:
            return sorted(
                [item for item in terceiros if terceiro_filter.lower() in item.nome.lower()],
                key=lambda r: (r.nome or "").strip().casefold()
            )
        return sorted(terceiros, key=lambda r: (r.nome or "").strip().casefold())

    def _on_left_double_click(self, event):
        column = self.left_tree.identify_column(event.x)
        if column in ("#1", "#2"):
            return
        item = self.left_tree.identify_row(event.y)
        if not item:
            return
        self.left_tree.selection_set(item)
        idx = int(item)
        if idx < 0 or idx >= len(self.left_records):
            return
        record = self.left_records[idx]

        # Duplo clique especificamente no Email: perguntar Valor_bruto e abrir envio.
        if column == "#5":
            email = (record.email or "").strip()
            if not email:
                messagebox.showwarning("E-mail", "Este Terceiro não possui e-mail cadastrado.")
                return
            initial_value = self.data_manager.get_last_valor_bruto()
            dialog = ValueInputDialog(self.root, "Valor bruto", "Informe o valor de [Valor_bruto]:", initial_value)
            self.root.wait_window(dialog)
            if dialog.result is not None:
                self.data_manager.set_last_valor_bruto(dialog.result)
                EmailDialog(self.root, email, record.nome, dialog.result)
            return

        # Duplo clique em qualquer outra coluna abre a edição do Terceiro.
        self._edit_selected_terceiro()

    def _on_right_double_click(self, event):
        item = self.right_tree.identify_row(event.y)
        if item:
            self.right_tree.selection_set(item)
            self._edit_selected_medico()

    def _edit_selected_terceiro(self):
        if not self.left_records:
            return
        idx = int(self.left_tree.selection()[0]) if self.left_tree.selection() else self.selected_index
        if idx < 0 or idx >= len(self.left_records):
            return
        record = self.left_records[idx]

        def on_save(updated):
            self.data_manager.update_terceiro(updated)
            self._load_data()
            self._apply_filters()

        TerceiroForm(self.root, record, on_save)

    def _edit_selected_medico(self):
        selection = self.right_tree.selection()
        if not selection:
            return
        idx = int(selection[0])
        right_records = sorted(
            [record for record in self.filtered_records if record.terceiro == self.selected_terceiro],
            key=lambda r: ((r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold())
        )
        if idx >= 0 and idx < len(right_records):
            record = right_records[idx]

            def on_save(updated):
                self.data_manager.update_medico(updated)
                self._load_data()
                self._apply_filters()
                self.selected_terceiro = updated.terceiro
                self._select_record_by_id(updated.id)

            EditForm(self.root, record, on_save, terceiro_options=self.data_manager.get_terceiros(),
                     especialidade_options=self.data_manager.get_especialidades_cadastradas())

    def _on_new_terceiro(self):
        def on_save(new_record):
            self.data_manager.add_terceiro(new_record)
            self._load_data()
            self._apply_filters()
            self.selected_terceiro = new_record.nome
            self._refresh_right_tree()

        TerceiroForm(self.root, TerceiroRecord(), on_save, title="Novo Terceiro")

    def _on_new_record(self):
        def on_save(new_record):
            self.data_manager.add_medico(new_record)
            self._load_data()
            self._apply_filters()
            self.selected_terceiro = new_record.terceiro
            self._select_record_by_id(new_record.id)

        AddForm(self.root, on_save, terceiro_options=self.data_manager.get_terceiros(),
                especialidade_options=self.data_manager.get_especialidades_cadastradas())

    def _on_delete_selected_terceiro(self):
        if not self.left_records or not self.left_tree.selection():
            messagebox.showwarning("Aviso", "Selecione um terceiro para excluir.")
            return
        idx = int(self.left_tree.selection()[0])
        record = self.left_records[idx]
        if not messagebox.askyesno("Confirmar exclusão", f"Deseja excluir o terceiro '{record.nome}' e todos os médicos vinculados?"):
            return
        self.data_manager.delete_terceiro(record.nome)
        self._load_data()
        self._apply_filters()
        self.status_var.set("Terceiro excluído")

    def _on_delete_selected_medico(self):
        selection = self.right_tree.selection()
        idx = int(selection[0]) if selection else -1
        right_records = sorted(
            [record for record in self.filtered_records if record.terceiro == self.selected_terceiro],
            key=lambda r: ((r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold())
        )

        if idx < 0:
            if 0 <= self.selected_index < len(self.filtered_records):
                record = self.filtered_records[self.selected_index]
            elif right_records:
                record = right_records[0]
            else:
                messagebox.showwarning("Aviso", "Selecione um médico para excluir.")
                return
        elif idx < len(right_records):
            record = right_records[idx]
        else:
            return

        if not messagebox.askyesno("Confirmar exclusão", f"Deseja excluir o médico '{record.medico}'?"):
            return
        self.data_manager.delete_medico(record.id)
        self._load_data()
        self._apply_filters()
        self.status_var.set("Médico excluído")

    def _on_delete_selected_record(self):
        self._on_delete_selected_medico()

    def _select_record_by_id(self, record_id: int):
        right_records = sorted(
            [record for record in self.filtered_records if record.terceiro == self.selected_terceiro],
            key=lambda r: ((r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold())
        )
        for i, record in enumerate(right_records):
            if record.id == record_id:
                self.right_tree.selection_set(str(i))
                self.right_tree.focus(str(i))
                self.right_tree.see(str(i))
                break

    def _on_especialidades(self):
        EspecialidadesWindow(self.root, self.data_manager)
        self.data_manager.load_especialidades_suplementadas()
        self._refresh_right_tree()

    def _on_email_config(self):
        EmailConfigForm(self.root)

    def _on_import(self):
        filepath = filedialog.askopenfilename(
            title="Importar arquivo",
            filetypes=[
                ("Arquivos Excel/CSV", "*.xls;*.xlsx;*.csv"),
                ("Arquivos Excel 97-2003", "*.xls"),
                ("Arquivos Excel", "*.xlsx"),
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if filepath:
            if filepath.endswith('.xls'):
                self._do_import(filepath, "xls")
            elif filepath.endswith('.xlsx'):
                self._do_import(filepath, "xlsx")
            elif filepath.endswith('.csv'):
                self._do_import(filepath, "csv")
            else:
                messagebox.showerror("Erro", "Formato de arquivo não suportado. Use XLS, XLSX ou CSV.")

    def _do_import(self, filepath: str, filetype: str):
        self.status_var.set(f"Importando {filetype.upper()}...")
        self.root.update()

        if filetype == "xls":
            added, skipped, errors = self.data_manager.import_from_xls(filepath)
        elif filetype == "csv":
            added, skipped, errors = self.data_manager.import_from_csv(filepath)
        else:
            added, skipped, errors = self.data_manager.import_from_xlsx(filepath)

        duplicates = getattr(self.data_manager, 'last_import_duplicates', [])

        self._load_data()
        self._apply_filters()

        # Relatório detalhado: não deixa duplicidades/erros passarem despercebidos.
        msg = (
            f"Importação concluída!\n\n"
            f"Novos registros importados: {added}\n"
            f"Registros ignorados (duplicados): {skipped}\n"
            f"Registros com erro: {len(errors)}"
        )

        if duplicates:
            msg += "\n\n--- DUPLICADOS IGNORADOS ---"
            for item in duplicates[:30]:
                msg += f"\n• {item}"
            if len(duplicates) > 30:
                msg += f"\n... e mais {len(duplicates) - 30} duplicados."

        if errors:
            msg += "\n\n--- ERROS ---"
            for err in errors[:30]:
                msg += f"\n• {err}"
            if len(errors) > 30:
                msg += f"\n... e mais {len(errors) - 30} erros."

        self._show_import_report(msg)
        self.status_var.set("Pronto")

    def _show_import_report(self, text: str):
        """Exibe o relatório em uma janela dimensionável com rolagem vertical."""
        win = tk.Toplevel(self.root)
        win.title("Relatório da importação")
        win.transient(self.root)
        win.geometry("760x520")
        win.minsize(520, 320)

        container = ttk.Frame(win, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        text_frame = ttk.Frame(container)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            padx=8,
            pady=8
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.insert("1.0", text)
        text_widget.configure(state=tk.DISABLED)

        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(button_frame, text="Fechar", command=win.destroy).pack(side=tk.RIGHT)

        win.grab_set()
        win.focus_set()
        win.protocol("WM_DELETE_WINDOW", win.destroy)

    def _on_export_csv(self):
        filepath = filedialog.asksaveasfilename(
            title="Exportar para CSV",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        if filepath:
            try:
                self.data_manager.export_to_csv(filepath, self.filtered_records)
                messagebox.showinfo("Exportação", f"Exportados {len(self.filtered_records)} registros para:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def _on_about(self):
        messagebox.showinfo("Sobre", "CadMedicos v1.0\nCadastro de Médicos\nCompatível com Windows 7 x86 / Python 3.8")

    def _update_status(self):
        total = len(self.records)
        filtered = len(self.filtered_records)
        if total == filtered:
            self.status_var.set(f"Total de registros: {total}")
        else:
            self.status_var.set(f"Exibindo: {filtered} de {total} registros")


def main():
    root = tk.Tk()
    app = CadMedicosApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()