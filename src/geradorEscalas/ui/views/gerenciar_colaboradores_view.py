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
from ..widgets.CTkAdvancedTable import CTkAdvancedTable

class GerenciarColaboradoresView(ctk.CTkFrame):
    def __init__(self, master, app_controller, data_to_load=None):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        
        self.selected_matriculas = set()
        self.table_data = []
        self.hovered_item = None # Atributo para controlar o hover

        # --- Carregar Imagens dos Checkboxes ---
        try:
            icon_path = "src/geradorEscalas/assets/icons"
            pil_checked = Image.open(os.path.join(icon_path, "checkbox_checked.png")).resize((16, 16), Image.Resampling.LANCZOS)
            pil_unchecked = Image.open(os.path.join(icon_path, "checkbox_unchecked.png")).resize((16, 16), Image.Resampling.LANCZOS)
            self.img_checked = ImageTk.PhotoImage(pil_checked)
            self.img_unchecked = ImageTk.PhotoImage(pil_unchecked)
        except Exception as e:
            print(f"ERRO: Não foi possível carregar as imagens de checkbox: {e}")
            self.img_checked = self.img_unchecked = None

        # --- Layout Principal ---
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Ícones ---
        icon_color = "#DCE4EE"
        icon_add = fa.icon_to_image("plus", fill=icon_color, scale_to_height=16)
        icon_import = fa.icon_to_image("file-import", fill=icon_color, scale_to_height=16)
        icon_edit = fa.icon_to_image("pencil-alt", fill=icon_color, scale_to_height=16)
        icon_delete = fa.icon_to_image("trash-alt", fill=icon_color, scale_to_height=16)

        # --- Cabeçalho e Ações ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1) # Cria espaço entre o título e os botões

        ctk.CTkLabel(header_frame, text="Gerenciar Colaboradores", font=fonts.TITULO_SECAO).grid(row=0, column=0, sticky="w")

        # Frame para os botões, posicionado na coluna 2
        action_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2, sticky="e")
        
        # --- Botões agora usam .grid() em vez de .pack() ---
        add_button = ctk.CTkButton(action_buttons_frame, text="Adicionar Novo", image=icon_add, compound="left", command=self.app_controller.show_cadastro_manual_view)
        add_button.grid(row=0, column=0, padx=5)

        import_button = ctk.CTkButton(action_buttons_frame, text="Importar", image=icon_import, compound="left", fg_color="transparent", border_color="#565B5E", border_width=2, command=self.app_controller.on_import_colaboradores)
        import_button.grid(row=0, column=1, padx=5)

        self.edit_button = ctk.CTkButton(action_buttons_frame, text="Editar", image=icon_edit, compound="left", command=self.edit_selected)
        self.edit_button.grid(row=0, column=2, padx=5)

        self.delete_button = ctk.CTkButton(action_buttons_frame, text="Excluir", image=icon_delete, compound="left", command=self.delete_selected, fg_color="#D63031", hover_color="#B02020")
        self.delete_button.grid(row=0, column=3, padx=5)

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        filter_frame.grid_columnconfigure(0, weight=1) # Entry de busca expande
        
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Pesquisar por nome ou matrícula...", font=fonts.TEXTO_NORMAL, height=35)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", self.perform_search)
        
        icon_search = fa.icon_to_image("search", fill="#DCE4EE", scale_to_height=16)
        # O botão agora tem a mesma altura do campo de busca
        ctk.CTkButton(filter_frame, text="", image=icon_search, width=35, height=35, command=self.perform_search).grid(row=0, column=1)

        # --- Tabela ---
        self.table_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", border_width=1, border_color="gray30")
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        self.update_table(invalid_rows=data_to_load)
        self.update_context_buttons()

    def update_table(self, search_term=None, invalid_rows=None):
        """
        Atualiza a tabela de colaboradores, usando o componente CTkAdvancedTable
        e aplicando os estilos de cores alternadas.
        """
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.selected_matriculas.clear()
        
        df = db.get_all_collaborators_dataframe(search_term) if invalid_rows is None else pd.DataFrame(invalid_rows)
        
        # --- Lógica de Estado Vazio ---
        if df.empty:
            msg_text = "Nenhum colaborador encontrado."
            if search_term:
                msg_text = f"Nenhum resultado para a busca '{search_term}'."
            elif invalid_rows is not None:
                msg_text = "Todos os colaboradores da planilha foram importados com sucesso!"
            
            empty_label = ctk.CTkLabel(self.table_frame, text=msg_text, font=fonts.SUBTITULO, text_color="gray60")
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
           
            self.update_context_buttons()
            return 
            
        df.fillna('', inplace=True)
        
        colunas_visiveis = ['nome', 'matricula', 'cargo', 'setor', 'escala', 'tipo_turno']
        colunas_df = [col for col in colunas_visiveis if col in df.columns]

        style = ttk.Style()

        style.configure("Treeview", borderwidth=0) 
        
        style.configure("Treeview.Heading", font=fonts.LABEL_FONT, padding=10)
        
        style.configure("Treeview.Cell", padding=5)

        self.tree = CTkAdvancedTable(self.table_frame, columns=colunas_df, show_checkbox_column=True)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1) # Pequeno padding interno
        
        scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)


        for col in colunas_df:
            self.tree.heading(col, text=col.replace('_', ' ').title(), anchor="w")
            if col == 'nome': width = 300
            elif col == 'cargo': width = 250
            elif col == 'setor': width = 200
            else: width = 120
            self.tree.column(col, width=width, anchor="w")

        self.table_data = df.to_dict('records')
        
        for i, record in enumerate(self.table_data):
            iid = str(record.get('matricula', f'temp_id_{i}'))
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            valores = [record.get(col, '') for col in colunas_df]
            self.tree.insert("", "end", iid=iid, image=self.img_unchecked, values=valores, tags=(row_tag,))

        self.tree.bind("<Button-1>", self.on_row_click)
        self.update_context_buttons()

    def on_mouse_motion(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id != self.hovered_item:
            if self.hovered_item:
                tags = list(self.tree.item(self.hovered_item, 'tags'))
                if 'hover' in tags:
                    tags.remove('hover')
                    self.tree.item(self.hovered_item, tags=tags)
            
            if item_id:
                tags = list(self.tree.item(item_id, 'tags'))
                tags.append('hover')
                self.tree.item(item_id, tags=tags)

            self.hovered_item = item_id

    def on_mouse_leave(self, event):
        if self.hovered_item:
            tags = list(self.tree.item(self.hovered_item, 'tags'))
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(self.hovered_item, tags=tags)
        self.hovered_item = None

    def on_row_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        
        if item_id in self.selected_matriculas:
            self.selected_matriculas.remove(item_id)
            self.tree.item(item_id, image=self.img_unchecked)
        else:
            self.selected_matriculas.add(item_id)
            self.tree.item(item_id, image=self.img_checked)
            
        if self.selected_matriculas:
            self.tree.selection_set(list(self.selected_matriculas))
        else:
            self.tree.selection_set([])
            
        self.update_context_buttons()
        
    def update_context_buttons(self):
        state = "normal" if self.selected_matriculas else "disabled"
        self.edit_button.configure(state=state)
        self.delete_button.configure(state=state)
        
    def get_selected_matriculas(self):
        return list(self.selected_matriculas)

    def edit_selected(self):
        matriculas_selecionadas = self.get_selected_matriculas()
        if not matriculas_selecionadas:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um ou mais colaboradores para editar.", parent=self)
            return
        
        dados_selecionados = []
        for i, record in enumerate(self.table_data):
            matricula_val = record.get('matricula') or record.get('Matrícula')
            iid = str(matricula_val) if matricula_val else f"registro_invalido_{i}"
            if iid in matriculas_selecionadas:
                dados_selecionados.append(record)
        
        if len(dados_selecionados) == 1:
            self.app_controller.show_cadastro_manual_view(matricula_para_editar=matriculas_selecionadas[0])
        else:
            self.app_controller.show_edicao_lote_view(dados_selecionados)
            
    def delete_selected(self):
        matriculas = self.get_selected_matriculas()
        if not matriculas:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um ou mais colaboradores para excluir.", parent=self)
            return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir {len(matriculas)} colaborador(es)?", parent=self):
            self.app_controller.on_delete_collaborators(matriculas)

    def perform_search(self, event=None):
        search_term = self.search_entry.get()
        self.update_table(search_term=search_term)