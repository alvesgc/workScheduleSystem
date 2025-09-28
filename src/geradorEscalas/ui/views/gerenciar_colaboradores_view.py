import customtkinter as ctk
from CTkTable import CTkTable
from tkinter import messagebox
from ... import database as db
from ... import fonts

class GerenciarColaboradoresView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        
        # --- Variáveis para controle da seleção na tabela ---
        self.selected_row_index = None
        self.table_data = [] # Armazena os dados da tabela para fácil acesso
        self.default_colors = ["#343638", "#2A2D2E"]
        self.highlight_color = "#3A7EBF" # Cor de destaque azul

        # --- Layout Principal ---
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Frame do Cabeçalho e Ações ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header_frame, text="Gerenciar Colaboradores", font=fonts.TITULO_SECAO).grid(row=0, column=0)
        
        action_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2)
        ctk.CTkButton(action_buttons_frame, text="Adicionar Novo", command=self.app_controller.show_cadastro_manual_view).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Importar Planilha", command=self.app_controller.on_import_colaboradores).pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Excluir", command=self.delete_selected, fg_color="#D63031", hover_color="#B02020").pack(side="left", padx=5)

        # --- Frame de Filtros ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var, placeholder_text="Pesquisar por nome ou matrícula...")
        self.search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.search_entry.bind("<Return>", self.perform_search)
        ctk.CTkButton(filter_frame, text="Pesquisar", command=self.perform_search).pack(side="left", padx=10)

        # --- Tabela de Dados ---
        self.table_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.update_table()

    def on_row_selected(self, event):
        """Lida com o clique em uma linha, destacando-a ou removendo o destaque."""
        clicked_row = event["row"]

        # Se uma linha já estava selecionada, remove o destaque dela
        if self.selected_row_index is not None:
            # Pega a cor padrão (alternada) da linha antiga
            old_color = self.default_colors[self.selected_row_index % 2]
            self.table.edit_row(self.selected_row_index, fg_color=old_color)
        
        # Se o usuário clicou na mesma linha que já estava selecionada, desmarca
        if self.selected_row_index == clicked_row:
            self.selected_row_index = None
            return # Sai da função

        # Destaca a nova linha clicada
        self.table.edit_row(clicked_row, fg_color=self.highlight_color)
        self.selected_row_index = clicked_row
        print(f"Linha {clicked_row} selecionada.")

    def delete_selected(self):
        """Pede confirmação e chama o controller para excluir o colaborador."""
        if self.selected_row_index is None:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, clique em um colaborador na tabela para selecioná-lo.", parent=self)
            return

        # Pega a matrícula da linha selecionada (índice da linha - 1, pois a linha 0 é o cabeçalho)
        matricula = self.table_data[self.selected_row_index - 1][1]
        nome = self.table_data[self.selected_row_index - 1][0]
        
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o colaborador '{nome}' (matrícula: {matricula})?", parent=self):
            self.app_controller.on_delete_collaborator(matricula)

    def perform_search(self, event=None):
        """Chama a atualização da tabela com o termo de pesquisa."""
        search_term = self.search_var.get()
        self.update_table(search_term)

    def update_table(self, search_term=None):
        """Busca os dados do banco e recria a tabela."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.selected_row_index = None # Reseta a seleção
        df = db.get_all_collaborators_dataframe(search_term=search_term)
        
        if df.empty:
            ctk.CTkLabel(self.table_frame, text="Nenhum colaborador encontrado.", font=fonts.TEXTO_NORMAL).pack(pady=20)
            return

        header = [col.replace('_', ' ').title() for col in df.columns]
        self.table_data = df.values.tolist() # Armazena os dados
        all_values = [header] + self.table_data

        self.table = CTkTable(master=self.table_frame, column=len(header), values=all_values,
                              header_color="#2A2D2E", colors=self.default_colors,
                              font=fonts.TEXTO_NORMAL, command=self.on_row_selected)
        
        # Ajusta larguras das colunas
        self.table.edit_column(0, width=250); self.table.edit_column(1, width=100)
        self.table.edit_column(2, width=200); self.table.edit_column(3, width=150)
        self.table.edit_column(4, width=120); self.table.edit_column(5, width=120)
        self.table.edit_column(6, width=100)
        
        self.table.pack(expand=True, fill="both")