from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from ... import fonts
from ... import database as db
from ..widgets.ctk_calendar import CTkCalendar
import tkfontawesome as fa


class CadastroManualView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller
        self.back_callback = app_controller.show_colaboradores_view
        self.matricula_para_editar = kwargs.get("matricula_para_editar")

        # === PALETA DE CORES HIERÁRQUICA ===
        self.PRIMARY = "#0078D7"
        self.PRIMARY_HOVER = "#005EA6"
        self.SURFACE = "#FFFFFF"
        self.SURFACE_SECONDARY = "#FAFAFA"
        self.BORDER = "#E1E4E8"
        self.BORDER_LIGHT = "#F0F0F0"
        self.TEXT_PRIMARY = "#1E1E1E"
        self.TEXT_SECONDARY = "#6B6B6B"
        self.TEXT_TERTIARY = "#9CA3AF"
        self.BUTTON_SECONDARY = "#FFFFFF"
        self.BUTTON_SECONDARY_HOVER = "#F5F5F5"
        self.BUTTON_SECONDARY_BORDER = "#D1D5DB"
        self.SUCCESS = "#10B981"
        self.SUCCESS_HOVER = "#059669"

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

        # === LAYOUT PRINCIPAL ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === CABEÇALHO ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Novo Colaborador",
            font=fonts.TITULO_SECAO,
            text_color=self.TEXT_PRIMARY,
        )
        self.title_label.pack(anchor="w", pady=(0, 4))
        
        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Preencha os dados abaixo para cadastrar um novo colaborador.",
            font=fonts.SUBTITULO,
            text_color=self.TEXT_SECONDARY,
        )
        self.subtitle_label.pack(anchor="w")

        # === CARD PRINCIPAL DO FORMULÁRIO ===
        form_container = ctk.CTkFrame(
            self,
            fg_color=self.SURFACE,
            border_color=self.BORDER,
            border_width=1,
            corner_radius=12,
        )
        form_container.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="nsew")
        form_container.grid_columnconfigure(0, weight=1)
        form_container.grid_rowconfigure(0, weight=1)

        scrollable_frame = ctk.CTkScrollableFrame(
            form_container, fg_color="transparent"
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # === ÍCONE DO CALENDÁRIO ===
        icon_calendar = fa.icon_to_image(
            "calendar-alt", fill="#FFFFFF", scale_to_height=16
        )
        
        # === SEÇÃO: DADOS PRINCIPAIS ===
        section_row = 0
        
        ctk.CTkLabel(
            scrollable_frame,
            text="Dados Principais",
            font=fonts.LABEL_FONT,
            text_color=self.TEXT_PRIMARY,
        ).grid(row=section_row, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 10))
        
        divider1 = ctk.CTkFrame(scrollable_frame, height=1, fg_color=self.BORDER_LIGHT)
        divider1.grid(row=section_row+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 16))

        # === CAMPOS DO FORMULÁRIO ===
        main_fields = ["Nome", "Matrícula", "Cargo", "Setor", "Tipo de Escala", "Turno Específico", "Conselho (Opcional)"]
        current_row = section_row + 2
        
        for label in main_fields:
            var = self.campos[label]
            
            ctk.CTkLabel(
                scrollable_frame,
                text=f"{label}:",
                font=fonts.SUBTITULO,
                text_color=self.TEXT_SECONDARY,
            ).grid(row=current_row, column=0, sticky="w", padx=20, pady=(0, 12))

            entry = None

            if label == "Tipo de Escala":
                entry = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=var,
                    values=db.get_distinct_escala_types(),
                    height=36,
                    font=fonts.SUBTITULO,
                    button_color=self.PRIMARY,
                    dropdown_hover_color=self.PRIMARY_HOVER,
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                )
            elif label == "Turno Específico":
                entry = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=var,
                    values=["", "Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2"],
                    height=36,
                    font=fonts.SUBTITULO,
                    state="readonly",
                    button_color=self.PRIMARY,
                    dropdown_hover_color=self.PRIMARY_HOVER,
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                )
            else:
                entry = ctk.CTkEntry(
                    scrollable_frame,
                    textvariable=var,
                    height=36,
                    font=fonts.SUBTITULO,
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                )

            entry.grid(row=current_row, column=1, padx=20, pady=(0, 12), sticky="ew")

            if label == "Matrícula":
                self.matricula_entry = entry
            
            current_row += 1

        # === SEÇÃO: AFASTAMENTOS ===
        ctk.CTkLabel(
            scrollable_frame,
            text="Afastamentos (Opcional)",
            font=fonts.LABEL_FONT,
            text_color=self.TEXT_PRIMARY,
        ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 10))
        
        divider2 = ctk.CTkFrame(scrollable_frame, height=1, fg_color=self.BORDER_LIGHT)
        divider2.grid(row=current_row+1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 16))
        
        current_row += 2

        # Campos de afastamento
        afastamento_fields = ["Início do Afastamento", "Fim do Afastamento", "Motivo do Afastamento"]
        
        for label in afastamento_fields:
            var = self.campos[label]
            
            ctk.CTkLabel(
                scrollable_frame,
                text=f"{label}:",
                font=fonts.SUBTITULO,
                text_color=self.TEXT_SECONDARY,
            ).grid(row=current_row, column=0, sticky="w", padx=20, pady=(0, 12))

            if "Início" in label or "Fim" in label:
                # Campo de data com botão de calendário
                date_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
                date_frame.grid(row=current_row, column=1, padx=20, pady=(0, 12), sticky="ew")
                date_frame.grid_columnconfigure(0, weight=1)
                
                entry = ctk.CTkEntry(
                    date_frame,
                    textvariable=var,
                    height=36,
                    font=fonts.SUBTITULO,
                    placeholder_text="DD/MM/AAAA",
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                )
                entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
                
                var.trace_add(
                    "write", lambda name, index, mode, v=var: self._format_date(v)
                )
                
                btn_calendar = ctk.CTkButton(
                    date_frame,
                    text="",
                    image=icon_calendar,
                    width=36,
                    height=36,
                    fg_color=self.PRIMARY,
                    hover_color=self.PRIMARY_HOVER,
                    corner_radius=8,
                    command=lambda v=var: self._open_calendar(v)
                )
                btn_calendar.grid(row=0, column=1)
            else:
                # Campo de texto normal (Motivo)
                entry = ctk.CTkEntry(
                    scrollable_frame,
                    textvariable=var,
                    height=36,
                    font=fonts.SUBTITULO,
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                )
                entry.grid(row=current_row, column=1, padx=20, pady=(0, 12), sticky="ew")
            
            current_row += 1

        # Espaço final
        ctk.CTkLabel(scrollable_frame, text="").grid(row=current_row, column=0, pady=10)

        # === BOTÕES DE AÇÃO ===
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(0, 24), padx=24, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="Salvar",
            command=self._save,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=self.SUCCESS,
            hover_color=self.SUCCESS_HOVER,
            corner_radius=8,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        
        ctk.CTkButton(
            button_frame,
            text="Voltar",
            command=self.back_callback,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=self.BUTTON_SECONDARY,
            hover_color=self.BUTTON_SECONDARY_HOVER,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BUTTON_SECONDARY_BORDER,
            corner_radius=8,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        if self.matricula_para_editar:
            self.load_data_for_editing()

    def load_data_for_editing(self):
        """Busca os dados do colaborador no BD e preenche o formulário."""
        self.title_label.configure(text="Editar Colaborador")
        self.subtitle_label.configure(text="Atualize os dados do colaborador abaixo.")
        
        data = db.get_collaborator_by_matricula(self.matricula_para_editar)
        if not data:
            messagebox.showerror("Erro", "Colaborador não encontrado.", parent=self)
            self.back_callback()
            return

        # Preenche os campos
        self.campos["Nome"].set(data.get("nome") or "")
        self.campos["Matrícula"].set(data.get("matricula") or "")
        self.campos["Cargo"].set(data.get("cargo") or "")
        self.campos["Setor"].set(data.get("setor") or "")
        self.campos["Tipo de Escala"].set(data.get("escala") or "")
        self.campos["Turno Específico"].set(data.get("tipo_turno") or "")
        self.campos["Conselho (Opcional)"].set(data.get("conselho") or "")
        self.campos["Motivo do Afastamento"].set(data.get("afastamento_motivo") or "")

        # Preenche datas
        inicio = data.get("afastamento_inicio")
        fim = data.get("afastamento_fim")
        self.campos["Início do Afastamento"].set(
            inicio.strftime("%d/%m/%Y") if inicio else ""
        )
        self.campos["Fim do Afastamento"].set(fim.strftime("%d/%m/%Y") if fim else "")

        self.matricula_entry.configure(state="disabled")

    def _format_date(self, var):
        """Formata automaticamente a data enquanto o usuário digita."""
        if not self._trace_active:
            return
        current_text = var.get()
        cleaned_text = "".join(filter(str.isdigit, current_text))[:8]
        formatted_text = ""
        if len(cleaned_text) > 4:
            formatted_text = f"{cleaned_text[:2]}/{cleaned_text[2:4]}/{cleaned_text[4:]}"
        elif len(cleaned_text) > 2:
            formatted_text = f"{cleaned_text[:2]}/{cleaned_text[2:]}"
        else:
            formatted_text = cleaned_text
        self._trace_active = False
        var.set(formatted_text)
        self._trace_active = True

    def _open_calendar(self, string_var_to_update):
        """Abre o calendário para seleção de data."""
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
        """Coleta os dados, valida e salva."""
        dados_ui = {key: var.get() for key, var in self.campos.items()}

        # Validações
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
                "Uma das datas está em formato inválido. Use DD/MM/AAAA.",
                parent=self,
            )
            return

        if fim_date and not inicio_date:
            messagebox.showerror(
                "Erro de Lógica",
                "A data de Fim não pode ser preenchida sem uma data de Início.",
                parent=self,
            )
            return

        if inicio_date and fim_date and fim_date < inicio_date:
            messagebox.showerror(
                "Erro de Lógica",
                "A data de Fim não pode ser anterior à data de Início.",
                parent=self,
            )
            return

        # Mapeia dados para o formato do BD
        dados_mapeados = {
            "nome": dados_ui.get("Nome"),
            "matricula": dados_ui.get("Matrícula"),
            "cargo": dados_ui.get("Cargo"),
            "setor": dados_ui.get("Setor"),
            "escala": dados_ui.get("Tipo de Escala"),
            "tipo_turno": dados_ui.get("Turno Específico"),
            "conselho": dados_ui.get("Conselho (Opcional)"),
            "afastamento_inicio": (
                inicio_date.strftime("%Y-%m-%d") if inicio_date else None
            ),
            "afastamento_fim": fim_date.strftime("%Y-%m-%d") if fim_date else None,
            "afastamento_motivo": dados_ui.get("Motivo do Afastamento"),
        }

        self.app_controller.on_save_colaborador(
            dados_mapeados, self.matricula_para_editar
        )