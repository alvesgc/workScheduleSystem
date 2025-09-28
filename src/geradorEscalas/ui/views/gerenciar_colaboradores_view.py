# src/geradorEscalas/ui/views/gerenciar_colaboradores_view.py

import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox
from .treeview_style import setup_treeview_style
from ... import database as db
from ... import fonts
import pandas as pd
from PIL import Image, ImageTk
import os

class GerenciarColaboradoresView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        
        self.selected_matriculas = set()
        self.table_data = []

        setup_treeview_style()

        # --- Carregar Imagens dos Checkboxes ---
        try:
            icon_path = "src/geradorEscalas/assets/icons"
            pil_checked = Image.open(os.path.join(icon_path, "checkbox_checked.png")).resize((16, 16), Image.Resampling.LANCZOS)
            pil_unchecked = Image.open(os.path.join(icon_path, "checkbox_unchecked.png")).resize((16, 16), Image.Resampling.LANCZOS)
            
            # Converte para o formato que o ttk.Treeview entende
            self.img_checked = ImageTk.PhotoImage(pil_checked)
            self.img_unchecked = ImageTk.PhotoImage(pil_unchecked)
            
        except Exception as e:
            print(f"ERRO: Não foi possível carregar as imagens de checkbox: {e}")
            self.img_checked = self.img_unchecked = None

        # --- Layout Principal ---
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Cabeçalho e Ações ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header_frame, text="Gerenciar Colaboradores", font=fonts.TITULO_SECAO).grid(row=0, column=0, sticky="w")
        
        action_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2)
        ctk.CTkButton(action_buttons_frame, text="Adicionar Novo", command=self.app_controller.show_cadastro_manual_view).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Importar", command=self.app_controller.on_import_colaboradores).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Editar Selecionado(s)", command=self.edit_selected).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Excluir Selecionado(s)", command=self.delete_selected, fg_color="#D63031", hover_color="#B02020").pack(side="left", padx=5)

        # --- Filtros ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var, placeholder_text="Pesquisar...")
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search)
        ctk.CTkButton(filter_frame, text="Pesquisar", command=self.perform_search).pack(side="left", padx=10)

        # --- Tabela ---
        self.table_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        self.update_table()

    def update_table(self, search_term=None, invalid_rows=None):
        for widget in self.table_frame.winfo_children(): widget.destroy()
        self.selected_matriculas.clear()
        
        df = db.get_all_collaborators_dataframe(search_term) if invalid_rows is None else pd.DataFrame(invalid_rows)
        df.fillna('', inplace=True)
        
        columns = list(df.columns)
        
        # O Treeview agora mostra a coluna #0, que conterá a imagem do checkbox
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="tree headings", style="Treeview")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configura a coluna #0 para a imagem
        self.tree.column("#0", width=50, stretch=False, anchor="center")
        self.tree.heading("#0", text="") # Sem texto no cabeçalho

        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(), anchor="w")
            if col == 'nome': width = 300
            elif col == 'cargo': width = 250
            elif col == 'setor': width = 200
            else: width = 120
            self.tree.column(col, width=width, anchor="w")

        self.table_data = df.to_dict('records')
        for i, record in enumerate(self.table_data):
            matricula = str(record.get('matricula', f'temp_id_{i}'))
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", iid=matricula, image=self.img_unchecked, values=list(record.values()), tags=(tag,))

        self.tree.bind("<Button-1>", self.on_row_click)

    def on_row_click(self, event):
        """Alterna a seleção e a imagem do checkbox ao clicar em uma linha."""
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        
        matricula = item_id
        
        if matricula in self.selected_matriculas:
            self.selected_matriculas.remove(matricula)
            self.tree.item(item_id, image=self.img_unchecked)
        else:
            self.selected_matriculas.add(matricula)
            self.tree.item(item_id, image=self.img_checked)
            
        # Força o Treeview a mostrar a seleção visualmente de forma consistente
        if self.selected_matriculas:
            self.tree.selection_set(list(self.selected_matriculas))
        else:
            self.tree.selection_set([])

    def get_selected_matriculas(self):
        return list(self.selected_matriculas)
        
    def edit_selected(self):
        matriculas = self.get_selected_matriculas()
        if not matriculas:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um ou mais colaboradores para editar.", parent=self)
            return
        
        # Lógica para decidir qual tela de edição abrir
        if len(matriculas) == 1:
            self.app_controller.show_cadastro_manual_view(matricula_para_editar=matriculas[0])
        else: # > 1
             messagebox.showinfo("Edição em Lote", "A funcionalidade de edição em lote será implementada aqui.", parent=self)
             # self.app_controller.show_edicao_lote_view(matriculas)

    def delete_selected(self):
        matriculas = self.get_selected_matriculas()
        if not matriculas:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um ou mais colaboradores para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {len(matriculas)} colaborador(es)?", parent=self):
            self.app_controller.on_delete_collaborators(matriculas)

    def perform_search(self, event=None):
        self.update_table(self.search_var.get())