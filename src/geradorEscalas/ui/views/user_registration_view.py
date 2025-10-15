import customtkinter as ctk
from ... import fonts


class UserRegistrationView(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback):
        # --- Fundo principal ---
        # Cor de fundo levemente acinzentada para consistência
        super().__init__(master, fg_color="#F9FAFB")
        self.save_callback = save_callback
        self.back_callback = back_callback

        # === PALETA DE CORES (Consistente com LoginView) ===
        CARD_COLOR = "#FFFFFF"
        BORDER_COLOR = "#E5E7EB"
        PRIMARY_TEXT = "#111827"
        SECONDARY_TEXT = "#6B7280"
        BUTTON_SECONDARY = "#F3F4F6"
        BUTTON_SECONDARY_HOVER = "#E5E7EB"
        BUTTON_SECONDARY_BORDER = "#D1D5DB"
        SUCCESS = "#10B981"
        SUCCESS_HOVER = "#059669"

        # --- Container principal para centralizar o card ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Card do Formulário (com borda, para consistência) ---
        form_card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        form_card.grid(row=0, column=0, sticky="", padx=20, pady=20)

        # Frame interno com padding maior
        main_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        main_frame.pack(expand=True, padx=32, pady=32)

        # --- Título e Subtítulo (Melhora a hierarquia) ---
        ctk.CTkLabel(
            main_frame,
            text="Crie sua Conta",
            font=fonts.TITULO_SECAO,
            text_color=PRIMARY_TEXT,
        ).pack(pady=(0, 8), anchor="w")

        ctk.CTkLabel(
            main_frame,
            text="Preencha os campos abaixo.",
            font=fonts.SUBTITULO,
            text_color=SECONDARY_TEXT,
        ).pack(pady=(0, 32), anchor="w")

        # --- Campos de Dados (com mais espaçamento vertical) ---
        ctk.CTkLabel(
            main_frame,
            text="Nome de Usuário",
            font=fonts.LABEL_FONT,
            text_color=PRIMARY_TEXT,
        ).pack(anchor="w", pady=(0, 4))
        self.user_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Apenas letras, números, _ ou -",
            font=fonts.TEXTO_NORMAL,
            height=40,
            corner_radius=8,
            border_color=BORDER_COLOR,
        )
        self.user_entry.pack(fill="x", pady=(0, 20))  # Aumentado o pady inferior

        ctk.CTkLabel(
            main_frame, text="Senha", font=fonts.LABEL_FONT, text_color=PRIMARY_TEXT
        ).pack(anchor="w", pady=(0, 4))
        self.pass_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite a senha",
            show="*",
            font=fonts.TEXTO_NORMAL,
            height=40,
            corner_radius=8,
            border_color=BORDER_COLOR,
        )
        self.pass_entry.pack(fill="x", pady=(0, 20))  # Aumentado o pady inferior

        ctk.CTkLabel(
            main_frame,
            text="Confirmar Senha",
            font=fonts.LABEL_FONT,
            text_color=PRIMARY_TEXT,
        ).pack(anchor="w", pady=(0, 4))
        self.confirm_pass_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Confirme a senha",
            show="*",
            font=fonts.TEXTO_NORMAL,
            height=40,
            corner_radius=8,
            border_color=BORDER_COLOR,
        )
        self.confirm_pass_entry.pack(fill="x")

        # --- Botões de Ação (com mais espaço acima) ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(40, 0))  # Aumentado o pady superior
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="Salvar Cadastro",
            command=self._on_save,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=SUCCESS,
            hover_color=SUCCESS_HOVER,
            corner_radius=8,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Voltar",
            command=self.back_callback,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=BUTTON_SECONDARY,
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=PRIMARY_TEXT,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            corner_radius=8,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _on_save(self):
        """Coleta os dados do formulário e os envia para o controlador principal."""
        data = {
            "username": self.user_entry.get(),
            "password": self.pass_entry.get(),
            "confirm_password": self.confirm_pass_entry.get(),
        }
        self.save_callback(data, self.winfo_toplevel())
