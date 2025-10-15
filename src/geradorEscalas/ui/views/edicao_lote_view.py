import customtkinter as ctk
from tkinter import messagebox
import tkfontawesome as fa
from ... import fonts
from ... import database as db


class EdicaoEmLoteView(ctk.CTkFrame):
    def __init__(self, master, app_controller, dados_para_editar):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller
        self.dados_para_editar = dados_para_editar

        self.matriculas = [
            str(d.get("matricula") or d.get("Matrícula"))
            for d in self.dados_para_editar
            if d.get("matricula") or d.get("Matrícula")
        ]

        # === PALETA DE CORES ===
        self.PRIMARY = "#0078D7"
        self.PRIMARY_HOVER = "#005EA6"
        self.SURFACE = "#FFFFFF"
        self.SURFACE_SECONDARY = "#FAFAFA"
        self.BORDER = "#E1E4E8"
        self.TEXT_PRIMARY = "#1E1E1E"
        self.TEXT_SECONDARY = "#6B6B6B"
        self.TEXT_TERTIARY = "#9CA3AF"
        self.BUTTON_SECONDARY = "#FFFFFF"
        self.BUTTON_SECONDARY_HOVER = "#F5F5F5"
        self.BUTTON_SECONDARY_BORDER = "#D1D5DB"
        self.SUCCESS = "#10B981"
        self.SUCCESS_HOVER = "#059669"

        self.edit_fields = {}

        # === LAYOUT PRINCIPAL ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === CABEÇALHO ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Edição em Lote",
            font=fonts.TITULO_SECAO,
            text_color=self.TEXT_PRIMARY,
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=f"Editando {len(dados_para_editar)} colaboradores simultaneamente. "
            "Marque os campos que deseja alterar.",
            font=fonts.SUBTITULO,
            text_color=self.TEXT_SECONDARY,
            wraplength=800,
            anchor="w",
            justify="left",
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # === CONTEÚDO PRINCIPAL ===
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        main_container.grid_columnconfigure((0, 1), weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # === PAINEL ESQUERDO ===
        list_container = ctk.CTkFrame(
            main_container,
            fg_color=self.SURFACE,
            border_color=self.BORDER,
            border_width=1,
            corner_radius=12,
        )
        list_container.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        list_container.grid_rowconfigure(1, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        list_header = ctk.CTkFrame(list_container, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        list_header.grid_columnconfigure(0, weight=1)

        label_title = ctk.CTkLabel(
            list_header,
            text="Colaboradores Selecionados",
            font=fonts.LABEL_FONT,
            text_color=self.TEXT_PRIMARY,
        )
        label_title.pack(side="left")

        label_count = ctk.CTkLabel(
            list_header,
            text=f"({len(dados_para_editar)})",
            font=fonts.SUBTITULO,
            text_color=self.TEXT_TERTIARY,
        )
        label_count.pack(side="left", padx=(8, 0))

        scrollable_list = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        scrollable_list.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        for i, colaborador in enumerate(self.dados_para_editar):
            nome = colaborador.get("nome", "Nome Indisponível")
            matricula = colaborador.get("matricula", "N/A")

            item_frame = ctk.CTkFrame(
                scrollable_list,
                fg_color=self.SURFACE_SECONDARY if i % 2 == 0 else "transparent",
                corner_radius=6,
            )
            item_frame.pack(fill="x", pady=2, padx=4)

            ctk.CTkLabel(
                item_frame,
                text=nome,
                font=fonts.SUBTITULO,
                text_color=self.TEXT_PRIMARY,
                anchor="w",
            ).pack(side="left", padx=12, pady=10)

            ctk.CTkLabel(
                item_frame,
                text=f"Mat: {matricula}",
                font=fonts.SUBTITULO,
                text_color=self.TEXT_SECONDARY,
                anchor="e",
            ).pack(side="right", padx=12, pady=10)

        # === PAINEL DIREITO ===
        edit_container = ctk.CTkFrame(
            main_container,
            fg_color=self.SURFACE,
            border_color=self.BORDER,
            border_width=1,
            corner_radius=12,
        )
        edit_container.grid(row=0, column=1, sticky="nsew")
        edit_container.grid_rowconfigure(1, weight=1)
        edit_container.grid_columnconfigure(0, weight=1)

        edit_header = ctk.CTkFrame(edit_container, fg_color="transparent")
        edit_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 12))

        ctk.CTkLabel(
            edit_header,
            text="Campos para Edição",
            font=fonts.LABEL_FONT,
            text_color=self.TEXT_PRIMARY,
        ).pack(anchor="w")

        fields_scroll = ctk.CTkScrollableFrame(edit_container, fg_color="transparent")
        fields_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        campos_config = {
            "cargo": {"label": "Cargo", "type": "entry"},
            "setor": {"label": "Setor", "type": "entry"},
            "escala": {
                "label": "Tipo de Escala",
                "type": "combo",
                "values": db.get_distinct_escala_types(),
            },
            "tipo_turno": {
                "label": "Tipo de Turno",
                "type": "combo",
                "values": ["", "Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2"],
            },
        }

        for campo_db, config in campos_config.items():
            field_card = ctk.CTkFrame(
                fields_scroll, fg_color=self.SURFACE_SECONDARY, corner_radius=8
            )
            field_card.pack(fill="x", pady=6, padx=8)

            check_var = ctk.StringVar(value="off")
            text_var = ctk.StringVar()

            field_inner = ctk.CTkFrame(field_card, fg_color="transparent")
            field_inner.pack(fill="x", padx=16, pady=12)

            checkbox = ctk.CTkCheckBox(
                field_inner,
                text=config["label"],
                variable=check_var,
                onvalue="on",
                offvalue="off",
                font=fonts.SUBTITULO,
                text_color=self.TEXT_PRIMARY,
                command=lambda c=campo_db: self._toggle_entry_state(c),
                width=160,
            )
            checkbox.pack(side="left", padx=(0, 12))

            if config["type"] == "combo":
                entry = ctk.CTkComboBox(
                    field_inner,
                    variable=text_var,
                    values=config["values"],
                    state="disabled",
                    font=fonts.SUBTITULO,
                    height=36,
                    button_color=self.PRIMARY,
                    dropdown_hover_color=self.PRIMARY_HOVER,
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                )
            else:
                entry = ctk.CTkEntry(
                    field_inner,
                    textvariable=text_var,
                    state="disabled",
                    font=fonts.SUBTITULO,
                    height=36,
                    fg_color=self.BUTTON_SECONDARY,
                    border_color=self.BUTTON_SECONDARY_BORDER,
                    corner_radius=8,
                    placeholder_text="Manter valores atuais",
                )
            entry.pack(side="left", fill="x", expand=True)

            self.edit_fields[campo_db] = {
                "check": check_var,
                "text": text_var,
                "entry": entry,
                "label": config["label"],
                "type": config["type"],
            }

        self._preencher_valores_iniciais()

        # === BOTÕES DE AÇÃO ===
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        button_frame.grid_columnconfigure((0, 1), weight=1)

        icon_save = fa.icon_to_image("save", fill="#FFFFFF", scale_to_height=16)

        ctk.CTkButton(
            button_frame,
            text="Salvar Alterações",
            command=self._save,
            height=44,
            font=fonts.BUTTON_FONT,
            image=icon_save,
            compound="left",
            fg_color=self.SUCCESS,
            hover_color=self.SUCCESS_HOVER,
            corner_radius=8,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.app_controller.show_colaboradores_view,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=self.BUTTON_SECONDARY,
            hover_color=self.BUTTON_SECONDARY_HOVER,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BUTTON_SECONDARY_BORDER,
            corner_radius=8,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    # === MÉTODOS AUXILIARES (inalterados) ===
    def _toggle_entry_state(self, campo):
        widgets = self.edit_fields.get(campo)
        if widgets:
            new_state = "normal" if widgets["check"].get() == "on" else "disabled"
            widgets["entry"].configure(state=new_state)
            if new_state == "normal":
                widgets["entry"].focus()

    def _preencher_valores_iniciais(self):
        for campo_db, widgets in self.edit_fields.items():
            primeiro_valor = self.dados_para_editar[0].get(campo_db, "")
            todos_iguais = all(
                colab.get(campo_db, "") == primeiro_valor
                for colab in self.dados_para_editar
            )

            if todos_iguais and primeiro_valor:
                widgets["text"].set(primeiro_valor)
                if widgets["type"] == "entry":
                    widgets["entry"].configure(placeholder_text="")
            else:
                widgets["text"].set("")
                if not todos_iguais and widgets["type"] == "entry":
                    widgets["entry"].configure(
                        placeholder_text="--- Múltiplos Valores ---"
                    )

    def _save(self):
        changes = {}
        for campo_db, widgets in self.edit_fields.items():
            if widgets["check"].get() == "on":
                changes[campo_db] = widgets["text"].get()

        if not changes:
            messagebox.showwarning(
                "Nenhuma Alteração",
                "Marque e preencha pelo menos um campo para aplicar a alteração.",
                parent=self,
            )
            return

        self.app_controller.on_batch_update(self.matriculas, changes)
