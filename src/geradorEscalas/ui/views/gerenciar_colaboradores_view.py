import customtkinter as ctk
from CTkTable import CTkTable # Importa a nova tabela
from ... import database as db
from ... import fonts

class GerenciarColaboradoresView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller

        # --- Layout Principal com Grid ---
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Frame do Cabeçalho e Ações ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text="Gerenciar Colaboradores", font=fonts.TITULO_SECAO).grid(row=0, column=0)
        
        action_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_buttons_frame.grid(row=0, column=2)

        ctk.CTkButton(action_buttons_frame, text="Adicionar Novo").pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Importar Planilha").pack(side="left", padx=5)
        ctk.CTkButton(action_buttons_frame, text="Excluir", fg_color="#D63031", hover_color="#B02020").pack(side="left", padx=5)

        # --- Frame de Filtros ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkEntry(filter_frame, placeholder_text="Pesquisar por nome ou matrícula...").pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ctk.CTkButton(filter_frame, text="Pesquisar").pack(side="left", padx=10)

        # --- Tabela de Dados ---
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.table = self.create_table(table_frame)
        self.table.pack(expand=True, fill="both")

    def create_table(self, master):
        """Busca os dados do banco e cria a tabela."""
        df = db.get_all_collaborators_dataframe()
        
        # Converte o DataFrame para uma lista de listas + cabeçalho
        header = [col.replace('_', ' ').title() for col in df.columns]
        data_values = [header] + df.values.tolist()

        table = CTkTable(master=master, 
                         values=data_values,
                         header_color="#2A2D2E",
                         colors=["#343638", "#2A2D2E"])
        
        return table