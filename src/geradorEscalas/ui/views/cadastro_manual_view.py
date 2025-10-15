from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from ... import fonts
from ... import database as db
from ..widgets.ctk_calendar import CTkCalendar
import tkfontawesome as fa

class CadastroManualView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.back_callback = app_controller.show_colaboradores_view
        self.matricula_para_editar = kwargs.get("matricula_para_editar")

        # --- PALETA DE CORES (consistente com as outras telas) ---
        SURFACE = "#FFFFFF"
        BORDER = "#E1E4E8"
        TEXT_PRIMARY = "#1E1E1E"
        TEXT_SECONDARY = "#6B6B6B"
        PRIMARY = "#0078D7"; PRIMARY_HOVER = "#005EA6"
        PRIMARY_HOVER = "#005EA6"

        # Bordas e divisores
        BORDER = "#E1E4E8"

        # Botões secundários
        BUTTON_SECONDARY = "#FFFFFF"
        BUTTON_SECONDARY_HOVER = "#F5F5F5"
        BUTTON_SECONDARY_BORDER = "#D1D5DB"

        # --- Dicionário de Campos ---
        self.campos = {
            "Nome": ctk.StringVar(),
            "Matrícula": ctk.StringVar(),
            "Cargo": ctk.StringVar(),
            "Setor": ctk.StringVar(),
            "Tipo de Escala": ctk.StringVar(),
            "Turno Específico": ctk.StringVar(),
            "Conselho (Opcional)": ctk.StringVar(),
            "Início do Afastamento": ctk.StringVar(),
            "Fim do Afastamento": ctk.StringVar(),
            "Motivo do Afastamento": ctk.StringVar(),
        }
        self._trace_active = True

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(24, 16), sticky="w")
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Novo Colaborador",
            font=fonts.TITULO_SECAO,
            text_color=TEXT_PRIMARY,
        )
        self.title_label.pack(anchor="w")

        # --- Card Principal para o Formulário ---
        form_container = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            border_color=BORDER,
            border_width=1,
            corner_radius=12,
        )
        form_container.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="nsew")
        form_container.grid_columnconfigure(0, weight=1)
        form_container.grid_rowconfigure(0, weight=1)

        scrollable_frame = ctk.CTkScrollableFrame(
            form_container, fg_color="transparent"
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        icon_color = ctk.ThemeManager.theme["CTkButton"]["text_color"]
        icon_color = icon_color[0] if ctk.get_appearance_mode() == "Light" else icon_color[1]
        icon_calendar = fa.icon_to_image("calendar-alt", fill=icon_color, scale_to_height=16)
        
        # --- L ÓGICA DO LOOP CORRIGIDA ---
        for i, (label, var) in enumerate(self.campos.items()):
            ctk.CTkLabel(
                scrollable_frame, text=f"{label}:", font=fonts.LABEL_FONT
            ).grid(row=i, column=0, sticky="w", padx=20, pady=10)

            entry = None  # Inicializa a variável 'entry'

            if "Afastamento" in label and ("Início" in label or "Fim" in label):
                date_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
                date_frame.grid(row=i, column=1, padx=20, pady=10, sticky="ew")
                date_frame.grid_columnconfigure(0, weight=1)
                entry = ctk.CTkEntry(
                    date_frame,
                    textvariable=var,
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                    placeholder_text="DD/MM/AAAA",
                )
                entry.grid(row=0, column=0, sticky="ew")
                var.trace_add(
                    "write", lambda name, index, mode, v=var: self._format_date(v)
                )
                btn = ctk.CTkButton(
                    date_frame,
                    text="", # Sem texto
                    image=icon_calendar,
                    width=35, height=35,
                    fg_color=PRIMARY, # Usa a cor azul do tema
                    hover_color=PRIMARY_HOVER,
                    command=lambda v=var: self._open_calendar(v)
                )
                btn.grid(row=0, column=1, padx=(5, 0))

            elif label == "Tipo de Escala":
                entry = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=var,
                    values=db.get_distinct_escala_types(),
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                    button_color=PRIMARY,
                    dropdown_hover_color=PRIMARY_HOVER
                )
            elif label == "Turno Específico":
                entry = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=var,
                    values=["", "Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2"],
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                    state="readonly",
                    button_color=PRIMARY,
                    dropdown_hover_color=PRIMARY_HOVER
                )
            else:
                entry = ctk.CTkEntry(
                    scrollable_frame,
                    textvariable=var,
                    height=35,
                    font=fonts.TEXTO_NORMAL,
                )

            if not ("Afastamento" in label and ("Início" in label or "Fim" in label)):
                entry.grid(row=i, column=1, padx=20, pady=12, sticky="ew")

            if label == "Matrícula":
                self.matricula_entry = entry

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(0, 24), padx=24, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="Salvar",
            command=self._save,
            height=45,
            font=fonts.BUTTON_FONT,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(
            button_frame,
            text="Voltar",
            command=self.back_callback,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=BUTTON_SECONDARY,
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            corner_radius=8,
            compound="left",
            border_spacing=10,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        if self.matricula_para_editar:
            self.load_data_for_editing()

    def load_data_for_editing(self):
        """Busca os dados do colaborador no BD e preenche o formulário, tratando valores nulos."""
        self.title_label.configure(text="Editar Colaborador")
        data = db.get_collaborator_by_matricula(self.matricula_para_editar)
        if not data:
            messagebox.showerror("Erro", "Colaborador não encontrado.", parent=self)
            self.back_callback()
            return

        # Preenche os campos de texto
        self.campos["Nome"].set(data.get("nome") or "")
        self.campos["Matrícula"].set(data.get("matricula") or "")
        self.campos["Cargo"].set(data.get("cargo") or "")
        self.campos["Setor"].set(data.get("setor") or "")
        self.campos["Tipo de Escala"].set(data.get("escala") or "")
        self.campos["Turno Específico"].set(data.get("tipo_turno") or "")
        self.campos["Conselho (Opcional)"].set(
            data.get("conselho") or ""
        )  # Corrigido aqui também
        self.campos["Motivo do Afastamento"].set(
            data.get("afastamento_motivo") or ""
        )  # Corrigido aqui

        # Preenche os campos de data
        inicio = data.get("afastamento_inicio")
        fim = data.get("afastamento_fim")
        self.campos["Início do Afastamento"].set(
            inicio.strftime("%d/%m/%Y") if inicio else ""
        )
        self.campos["Fim do Afastamento"].set(fim.strftime("%d/%m/%Y") if fim else "")

        self.matricula_entry.configure(state="disabled")

    def _format_date(self, var):
        if not self._trace_active:
            return
        current_text = var.get()
        cleaned_text = "".join(filter(str.isdigit, current_text))[:8]
        formatted_text = ""
        if len(cleaned_text) > 4:
            formatted_text = (
                f"{cleaned_text[:2]}/{cleaned_text[2:4]}/{cleaned_text[4:]}"
            )
        elif len(cleaned_text) > 2:
            formatted_text = f"{cleaned_text[:2]}/{cleaned_text[2:]}"
        else:
            formatted_text = cleaned_text
        self._trace_active = False
        var.set(formatted_text)
        self._trace_active = True

    def _open_calendar(self, string_var_to_update):
        def update_var_callback(selected_date_obj):
            string_var_to_update.set(selected_date_obj.strftime("%d/%m/%Y"))

        initial_date = None
        if string_var_to_update.get():
            try:
                initial_date = datetime.strptime(
                    string_var_to_update.get(), "%d/%m/%Y"
                ).date()
            except ValueError:
                pass
        CTkCalendar(self, current_date=initial_date, callback=update_var_callback)

    def _save(self):
        """Coleta os dados, valida, mapeia para o formato do BD e chama o callback."""
        # 1. Coleta os dados brutos da interface do usuário
        dados_ui = {key: var.get() for key, var in self.campos.items()}

        # 2. Validações principais
        if not dados_ui["Nome"] or not dados_ui["Matrícula"]:
            messagebox.showwarning(
                "Campo Obrigatório",
                "Os campos 'Nome' e 'Matrícula' são obrigatórios.",
                parent=self,
            )
            return

        inicio_str = dados_ui["Início do Afastamento"]
        fim_str = dados_ui["Fim do Afastamento"]
        inicio_date = None
        fim_date = None

        try:
            if inicio_str:
                inicio_date = datetime.strptime(inicio_str, "%d/%m/%Y").date()
            if fim_str:
                fim_date = datetime.strptime(fim_str, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror(
                "Formato Inválido",
                "Uma das datas de afastamento está em formato inválido. Use DD/MM/AAAA.",
                parent=self,
            )
            return

        if fim_date and not inicio_date:
            messagebox.showerror(
                "Erro de Lógica",
                "A data de Fim do Afastamento não pode ser preenchida sem uma data de Início.",
                parent=self,
            )
            return

        if inicio_date and fim_date and fim_date < inicio_date:
            messagebox.showerror(
                "Erro de Lógica",
                "A data de Fim do Afastamento não pode ser anterior à data de Início.",
                parent=self,
            )
            return

        dados_mapeados = {
            "nome": dados_ui.get("Nome"),
            "matricula": dados_ui.get("Matrícula"),
            "cargo": dados_ui.get("Cargo"),
            "setor": dados_ui.get("Setor"),
            "escala": dados_ui.get(
                "Tipo de Escala"
            ),  # UI 'Tipo de Escala' -> DB 'escala'
            "tipo_turno": dados_ui.get(
                "Turno Específico"
            ),  # UI 'Turno Específico' -> DB 'tipo_turno'
            "conselho": dados_ui.get("Conselho (Opcional)"),
            "afastamento_inicio": (
                inicio_date.strftime("%Y-%m-%d") if inicio_date else None
            ),
            "afastamento_fim": fim_date.strftime("%Y-%m-%d") if fim_date else None,
            "afastamento_motivo": dados_ui.get("Motivo do Afastamento"),
        }

        # 4. Chama a função de callback com os dados já mapeados e prontos para o BD
        self.app_controller.on_save_colaborador(
            dados_mapeados, self.matricula_para_editar
        )
