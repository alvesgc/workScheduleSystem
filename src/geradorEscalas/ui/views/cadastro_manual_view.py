import customtkinter as ctk
from tkinter import messagebox
from ... import fonts
from ... import database as db


class CadastroManualView(ctk.CTkFrame):
    def __init__(
        self, master, save_callback, back_callback, matricula_para_editar=None
    ):
        super().__init__(master, fg_color="transparent")
        self.save_callback = save_callback
        self.back_callback = back_callback
        self.matricula_para_editar = matricula_para_editar

        self.campos = {
            "Nome": ctk.StringVar(),
            "Matrícula": ctk.StringVar(),
            "Cargo": ctk.StringVar(),
            "Setor": ctk.StringVar(),
            "Escala": ctk.StringVar(),
            "Tipo de Turno": ctk.StringVar(),
            "Horário Padrão": ctk.StringVar(),
            "COREN (opcional)": ctk.StringVar(),
            "Período de Afastamento": ctk.StringVar(),
        }

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- WIDGET DO TÍTULO CRIADO E ARMAZENADO CORRETAMENTE ---
        self.title_label = ctk.CTkLabel(
            self, text="Novo Colaborador", font=fonts.TITULO_SECAO
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # --- Frame com Rolagem para o Formulário ---
        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure(1, weight=1)

        for i, (label, var) in enumerate(self.campos.items()):
            ctk.CTkLabel(
                scrollable_frame, text=f"{label}:", font=fonts.LABEL_FONT
            ).grid(row=i, column=0, sticky="w", padx=20, pady=10)

            if label == "Escala":
                entry = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=var,
                    values=["12x36", "Diarista"],
                    state="readonly",
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                )
            elif label == "Tipo de Turno":
                entry = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=var,
                    values=["Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2", "-"],
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                )
            else:
                entry = ctk.CTkEntry(
                    scrollable_frame,
                    textvariable=var,
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                )

            # Armazena a referência ao entry da matrícula para poder desabilitá-lo
            if label == "Matrícula":
                self.matricula_entry = entry

            entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            button_frame,
            text="Salvar",
            command=self._save,
            height=45,
            font=fonts.BUTTON_FONT,
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(
            button_frame,
            text="Voltar",
            command=self.back_callback,
            fg_color="#7A7A7A",
            hover_color="#5E5E5E",
            height=45,
            font=fonts.BUTTON_FONT,
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Se estiver no modo de edição, carrega os dados
        if self.matricula_para_editar:
            self.load_data_for_editing()

    def load_data_for_editing(self):
        """Busca os dados do colaborador no BD e preenche o formulário."""
        # Agora self.title_label existe e pode ser configurado
        self.title_label.configure(text="Editar Colaborador")

        data = db.get_collaborator_by_matricula(self.matricula_para_editar)
        if not data:
            messagebox.showerror("Erro", "Colaborador não encontrado.", parent=self)
            self.back_callback()
            return

        # Preenche os campos
        self.campos["Nome"].set(data.get("nome", ""))
        self.campos["Matrícula"].set(data.get("matricula", ""))
        self.campos["Cargo"].set(data.get("cargo", ""))
        self.campos["Setor"].set(data.get("setor", ""))
        self.campos["Escala"].set(data.get("escala", ""))
        self.campos["Tipo de Turno"].set(data.get("tipo_turno", ""))
        self.campos["Horário Padrão"].set(data.get("horario_padrao", ""))
        self.campos["COREN (opcional)"].set(data.get("coren", ""))
        self.campos["Período de Afastamento"].set(data.get("periodo_afastamento", ""))

        # Desabilita o campo de matrícula para não ser alterado
        self.matricula_entry.configure(state="disabled")

    def _save(self):
        """Coleta os dados, formata para o BD e chama o callback de salvamento."""
        dados_para_db = {key: var.get() for key, var in self.campos.items()}

        # A validação agora usa as chaves corretas
        if not dados_para_db["Nome"] or not dados_para_db["Matrícula"]:
            messagebox.showwarning(
                "Campo Obrigatório",
                "Os campos 'Nome' e 'Matrícula' são obrigatórios.",
                parent=self,
            )
            return

        if "dd/mm/aaaa" in str(dados_para_db["Período de Afastamento"]):
            dados_para_db["Período de Afastamento"] = ""
            
        self.save_callback(dados_para_db, self.matricula_para_editar)
