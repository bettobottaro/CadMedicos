import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import DataManager
from ui_utils import center_window


class EspecialidadesWindow(tk.Toplevel):
    def __init__(self, parent, data_manager: DataManager):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("Cadastro de Especialidades Suplementadas")
        self.geometry("450x400")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_data()
        
        # Centralizar janela
        center_window(self)
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Adicionar", command=self._on_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Editar", command=self._on_edit).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Excluir", command=self._on_delete).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(toolbar, text="Fechar", command=self.destroy).pack(side=tk.RIGHT, padx=2)
        
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("especialidade",)
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("especialidade", text="Especialidade Suplementada")
        self.tree.column("especialidade", width=400, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", lambda e: self._on_edit())
    
    def _load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        especialidades = self.data_manager.get_especialidades_suplementadas()
        for esp in especialidades:
            self.tree.insert("", tk.END, values=(esp,))
    
    def _on_add(self):
        dialog = AddEspecialidadeDialog(self, "Nova Especialidade Suplementada")
        self.wait_window(dialog)
        if dialog.result:
            self.data_manager.add_especialidade_suplementada(dialog.result)
            self._load_data()
    
    def _on_edit(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma especialidade para editar.")
            return
        
        item = self.tree.item(selection[0])
        old_value = item["values"][0]
        
        dialog = AddEspecialidadeDialog(self, "Editar Especialidade Suplementada", old_value)
        self.wait_window(dialog)
        if dialog.result and dialog.result != old_value:
            self.data_manager.remove_especialidade_suplementada(old_value)
            self.data_manager.add_especialidade_suplementada(dialog.result)
            self._load_data()
    
    def _on_delete(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma especialidade para excluir.")
            return
        
        item = self.tree.item(selection[0])
        value = item["values"][0]
        
        if messagebox.askyesno("Confirmar", f"Deseja excluir a especialidade '{value}'?"):
            self.data_manager.remove_especialidade_suplementada(value)
            self._load_data()


class AddEspecialidadeDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_value=""):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets(initial_value)
        
        # Centralizar janela
        center_window(self)
    
    def _create_widgets(self, initial_value):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Especialidade:").pack(anchor=tk.W)
        
        self.entry = ttk.Entry(main_frame, width=50)
        self.entry.pack(fill=tk.X, pady=(5, 15))
        self.entry.insert(0, initial_value)
        self.entry.focus()
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self.destroy())
    
    def _on_ok(self):
        value = self.entry.get().strip()
        if not value:
            messagebox.showerror("Erro", "Informe a especialidade.")
            return
        if len(value) > 100:
            messagebox.showerror("Erro", "Especialidade deve ter no máximo 100 caracteres.")
            return
        self.result = value
        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    dm = DataManager()
    win = EspecialidadesWindow(root, dm)
    root.mainloop()