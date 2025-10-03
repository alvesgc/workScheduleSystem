import customtkinter as ctk
from tkinter import messagebox
from ... import fonts
from ... import database as db

class EdicaoEmLoteView(ctk.CTkFrame):
    def __init__(self, master, app_controller, matriculas):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.matriculas = matriculas

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(header_frame, text=f"Editando {len(self.matriculas)} Colaboradores em Lote", font=fonts.TITULO_SECAO).pack(anchor="w")

        # --- Painéis de Conteúdo ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- PAINEL ESQUERDO: LISTA DE SELECIONADOS ---
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(list_frame, text="Colaboradores Selecionados:", font=fonts.LABEL_FONT).pack(anchor="w", padx=15, pady=10)
        
        scrollable_list = ctk.CTkScrollableFrame(list_frame, fg_color="#2A2D2E")
        scrollable_list.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        # Busca os nomes no banco para exibir na lista
        for mat in self.matriculas:
            colab = db.get_collaborator_by_matricula(mat)
            if colab:
                ctk.CTkLabel(scrollable_list, text=colab.get('nome', ''), font=fonts.TEXTO_NORMAL).pack(anchor="w", padx=10, pady=2)

        # --- PAINEL DIREITO: CAMPOS DE EDIÇÃO ---
        edit_frame = ctk.CTkFrame(main_frame)
        edit_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        edit_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(edit_frame, text="Novos Valores", font=fonts.LABEL_FONT).grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(edit_frame, text="Preencha apenas os campos que deseja alterar.", font=fonts.TEXTO_NORMAL, text_color="gray").grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="w")

        self.field_vars = {
            "Cargo": ctk.StringVar(), "Setor": ctk.StringVar(), "Escala": ctk.StringVar(),
            "Tipo de Turno": ctk.StringVar(), "Horario Padrao": ctk.StringVar()
        }
        
        # Cria os campos de forma organizada em um grid
        row = 2
        for label, var in self.field_vars.items():
            ctk.CTkLabel(edit_frame, text=f"{label}:", font=fonts.LABEL_FONT).grid(row=row, column=0, sticky="w", padx=20, pady=(10,0))
            
            if label == "Escala":
                entry = ctk.CTkComboBox(edit_frame, variable=var, values=["", "12x36", "Diarista"], state="readonly", height=35, font=fonts.TEXTO_NORMAL)
            elif label == "Tipo de Turno":
                entry = ctk.CTkComboBox(edit_frame, variable=var, values=["", "Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2", "-"], height=35, font=fonts.TEXTO_NORMAL)
            else:
                entry = ctk.CTkEntry(edit_frame, textvariable=var, placeholder_text=f"Novo valor para {label}", height=35, font=fonts.TEXTO_NORMAL)
            
            entry.grid(row=row+1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
            row += 2

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=20)
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(button_frame, text="Salvar Alterações", command=self._save, height=45).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(button_frame, text="Cancelar", command=self.app_controller.show_colaboradores_view, height=45,fg_color="#7A7A7A", hover_color="#5E5E5E").grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _save(self):
        changes = {}
        # Coleta apenas os campos que o usuário preencheu
        for label, var in self.field_vars.items():
            if var.get().strip():
                db_field_name = label.lower().replace(' ', '_')
                changes[db_field_name] = var.get()
        
        if not changes:
            messagebox.showwarning("Nenhuma Alteração", "Preencha pelo menos um campo para aplicar a alteração em lote.", parent=self)
            return

        self.app_controller.on_batch_update(self.matriculas, changes)