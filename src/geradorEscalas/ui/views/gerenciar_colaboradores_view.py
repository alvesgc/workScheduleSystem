import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox
from .treeview_style import setup_treeview_style
from ... import database as db
from ... import fonts
import pandas as pd
from PIL import Image, ImageTk
import os
import tkfontawesome as fa

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
        self.grid_rowconfigure(1, weight=1) # A linha da tabela é a que expande
        self.grid_columnconfigure(0, weight=1)

        # --- NOVO PAINEL DE CONTROLE (para botões e filtros) ---
        control_panel = ctk.CTkFrame(self)
        control_panel.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_panel.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(control_panel, text="Gerenciar Colaboradores", font=fonts.TITULO_SECAO).grid(row=0, column=0, padx=20, pady=20)
        
        # Botões de Ação com Ícones
        action_buttons_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2, padx=20)
        ctk.CTkButton(action_buttons_frame, text="Adicionar", image=self.icon_add, compound="left", command=self.app_controller.show_cadastro_manual_view).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Importar", image=self.icon_import, compound="left", command=self.app_controller.on_import_colaboradores).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Editar", image=self.icon_edit, compound="left", command=self.edit_selected).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Excluir", image=self.icon_delete, compound="left", command=self.delete_selected, fg_color="#D63031", hover_color="#B02020").pack(side="left", padx=5)

        # Filtros
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(control_panel, textvariable=self.search_var, placeholder_text="Pesquisar por nome ou matrícula...", height=35)
        search_entry.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 20))
        search_entry.bind("<Return>", self.perform_search)
        
        # --- Tabela de Dados (agora dentro de seu próprio "Card") ---
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
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
        
        if len(matriculas) == 1:
            # Edição única: abre o formulário de cadastro em modo de edição
            self.app_controller.show_cadastro_manual_view(matricula_para_editar=matriculas[0])
        else: # > 1
            # Edição em lote: abre a nova tela de edição em lote
            self.app_controller.show_edicao_lote_view(matriculas)

    def delete_selected(self):
        matriculas = self.get_selected_matriculas()
        if not matriculas:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um ou mais colaboradores para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {len(matriculas)} colaborador(es)?", parent=self):
            self.app_controller.on_delete_collaborators(matriculas)

    def perform_search(self, event=None):
        self.update_table(self.search_var.get())
        
    def apply_batch_edit(self):
        """Coleta os dados do painel e chama o controlador para aplicar a edição em lote."""
        matriculas = self.get_selected_matriculas()
        # Converte o nome do campo para o formato do banco (ex: "Tipo de Turno" -> "tipo_turno")
        field = self.field_to_edit_var.get().lower().replace(' ', '_')
        new_value = self.new_value_var.get()

        if not matriculas:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um ou mais colaboradores para aplicar a alteração.", parent=self)
            return
            
        if not new_value.strip():
            messagebox.showwarning("Valor Vazio", "Por favor, digite o novo valor a ser aplicado.", parent=self)
            return
        
        # Chama a função no controlador principal para executar a ação
        self.app_controller.on_batch_update(matriculas, field, new_value)