import customtkinter as ctk
from tkinter import messagebox
import tkfontawesome as fa
from ... import fonts
from ... import database as db


class EdicaoEmLoteView(ctk.CTkFrame):
    def __init__(self, master, app_controller, dados_para_editar):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.dados_para_editar = dados_para_editar

        self.matriculas = [
            str(d.get("matricula") or d.get("Matrícula"))
            for d in self.dados_para_editar
            if d.get("matricula") or d.get("Matrícula")
        ]

        # Dicionário para guardar os widgets de cada campo de edição
        self.edit_fields = {}

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(
            header_frame,
            text=f"Editando {len(dados_para_editar)} Colaboradores em Lote",
            font=fonts.TITULO_SECAO,
        ).pack(anchor="w")

        # --- Painéis Principais ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1, minsize=300)  # Coluna da lista
        main_frame.grid_columnconfigure(1, weight=2)  # Coluna dos campos
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Painel Esquerdo: Lista de Selecionados ---
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            list_frame, text="Colaboradores Selecionados", font=fonts.LABEL_FONT
        ).pack(anchor="w", padx=10, pady=10)

        scrollable_list = ctk.CTkScrollableFrame(
            list_frame, fg_color="#2A2D2E", border_width=1, border_color="gray30"
        )
        scrollable_list.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        for colaborador in self.dados_para_editar:
            nome = colaborador.get("nome", "Nome Indisponível")
            matricula = colaborador.get("matricula", "N/A")
            display_text = f"• {nome} (Mat.: {matricula})"
            ctk.CTkLabel(
                scrollable_list, text=display_text, font=fonts.TEXTO_NORMAL
            ).pack(anchor="w", padx=10, pady=2)

        # --- Painel Direito: Campos de Edição ---
        edit_frame = ctk.CTkFrame(main_frame)
        edit_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(
            edit_frame,
            text="Marque os campos que deseja alterar:",
            font=fonts.LABEL_FONT,
        ).pack(pady=10, padx=20, anchor="w")

        # Define os campos que podem ser editados em lote
        campos_para_edicao = ["cargo", "setor", "escala", "tipo_turno"]

        for campo_db in campos_para_edicao:
            label_text = campo_db.replace("_", " ").title()

            row_frame = ctk.CTkFrame(edit_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=10, anchor="n")

            check_var = ctk.StringVar(value="off")
            text_var = ctk.StringVar()

            # O command do checkbox agora chama uma função para habilitar/desabilitar o campo
            checkbox = ctk.CTkCheckBox(
                row_frame,
                text=f"{label_text}:",
                variable=check_var,
                onvalue="on",
                offvalue="off",
                font=fonts.LABEL_FONT,
                command=lambda c=campo_db: self._toggle_entry_state(c),
            )
            checkbox.pack(side="left")

            # O Entry agora tem um placeholder dinâmico
            entry = ctk.CTkEntry(
                row_frame,
                textvariable=text_var,
                state="disabled",
                font=fonts.TEXTO_NORMAL,
                height=35,
                placeholder_text="Manter valores atuais",
            )
            entry.pack(side="left", expand=True, fill="x", padx=10)

            self.edit_fields[campo_db] = {
                "check": check_var,
                "text": text_var,
                "entry": entry,
                "label": label_text,
            }

        self._preencher_valores_iniciais()

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=20)
        button_frame.grid_columnconfigure(0, weight=1)

        icon_save = fa.icon_to_image("save", fill="#DCE4EE", scale_to_height=16)
        ctk.CTkButton(
            button_frame,
            text="Salvar Alterações",
            command=self._save,
            height=45,
            font=fonts.BUTTON_FONT,
            image=icon_save,
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.app_controller.show_colaboradores_view,
            height=45,
            font=fonts.BUTTON_FONT,
            fg_color="#7A7A7A",
            hover_color="#5E5E5E",
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _toggle_entry_state(self, campo):
        widgets = self.edit_fields.get(campo)
        if widgets:
            new_state = "normal" if widgets["check"].get() == "on" else "disabled"
            widgets["entry"].configure(state=new_state)
            if new_state == "normal":
                widgets["entry"].focus()

    def _preencher_valores_iniciais(self):
        """Verifica os dados dos colaboradores e pré-preenche os campos ou placeholders."""
        for campo_db, widgets in self.edit_fields.items():
            primeiro_valor = self.dados_para_editar[0].get(campo_db, "")
            todos_iguais = all(
                colab.get(campo_db, "") == primeiro_valor
                for colab in self.dados_para_editar
            )

            if todos_iguais:
                # Se todos os valores são iguais, preenche o campo
                widgets["text"].set(primeiro_valor or "")
                # Remove o placeholder para não confundir
                widgets["entry"].configure(placeholder_text="")
            else:
                # Se os valores são diferentes, o campo fica vazio e o placeholder aparece
                widgets["text"].set("")
                widgets["entry"].configure(placeholder_text="--- Múltiplos Valores ---")

    def _save(self):
        """Coleta os dados apenas dos campos marcados e chama o callback."""
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
