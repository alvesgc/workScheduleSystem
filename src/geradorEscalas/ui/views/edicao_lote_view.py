import customtkinter as ctk
from tkinter import messagebox
from ... import fonts
from ... import database as db

class EdicaoEmLoteView(ctk.CTkFrame):
    def __init__(self, master, app_controller, dados_para_editar):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.dados_para_editar = dados_para_editar

        # Extrai as matrículas REAIS para usar ao salvar (ignora os temporários)
        self.matriculas = [
            str(d.get('matricula') or d.get('Matrícula')) 
            for d in self.dados_para_editar 
            if d.get('matricula') or d.get('Matrícula')
        ]
        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # A lista de nomes expande

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(header_frame, text=f"Editando {len(dados_para_editar)} Colaboradores em Lote", font=fonts.TITULO_SECAO).pack(anchor="w")

        # --- Painéis Principais ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Painel Esquerdo: Lista de Selecionados ---
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(list_frame, text="Colaboradores Selecionados:", font=fonts.LABEL_FONT).pack(anchor="w", padx=10, pady=5)
        
        scrollable_list = ctk.CTkScrollableFrame(list_frame, fg_color="#2A2D2E")
        scrollable_list.pack(expand=True, fill="both", padx=5, pady=5)

        for colaborador in self.dados_para_editar:
            nome = colaborador.get('Nome') or colaborador.get('nome', 'Nome Indisponível')
            matricula = colaborador.get('Matrícula') or colaborador.get('matricula', 'N/A')
            
            display_text = f"{nome} (Mat.: {matricula})"
            
            ctk.CTkLabel(scrollable_list, text=display_text).pack(anchor="w", padx=10)

        # --- Painel Direito: Campos de Edição ---
        edit_frame = ctk.CTkFrame(main_frame)
        edit_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        ctk.CTkLabel(edit_frame, text="Deixe um campo em branco para não alterá-lo.", font=fonts.TEXTO_NORMAL).pack(pady=10, padx=20, anchor="w")

        self.field_vars = {
            "Cargo": ctk.StringVar(),
            "Setor": ctk.StringVar(),
            "Escala": ctk.StringVar(),
            "Tipo de Turno": ctk.StringVar(),
            "Horario Padrao": ctk.StringVar()
        }

        for label, var in self.field_vars.items():
            ctk.CTkLabel(edit_frame, text=f"{label}:", font=fonts.LABEL_FONT).pack(anchor="w", padx=20, pady=(10, 0))
            ctk.CTkEntry(edit_frame, textvariable=var, placeholder_text=f"Novo valor para {label}").pack(fill="x", padx=20, pady=5)

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=20)
        button_frame.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkButton(button_frame, text="Salvar Alterações", command=self._save, height=45).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(button_frame, text="Cancelar", command=self.app_controller.show_colaboradores_view, fg_color="#7A7A7A", hover_color="#5E5E5E").grid(row=0, column=1, padx=(5, 0), sticky="ew")

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