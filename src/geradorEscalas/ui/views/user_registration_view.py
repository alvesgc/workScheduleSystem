import customtkinter as ctk
from ... import fonts


class UserRegistrationView(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback):
        # Fundo principal da tela, herda a cor da janela pop-up
        super().__init__(master, fg_color="transparent")
        self.save_callback = save_callback
        self.back_callback = back_callback

        # === PALETA DE CORES ===
        SURFACE = "#FFFFFF"
        BORDER = "#E1E4E8"
        TEXT_PRIMARY = "#1E1E1E"
        TEXT_SECONDARY = "#6B6B6B"
        BUTTON_SECONDARY = "#F3F4F6"
        BUTTON_SECONDARY_HOVER = "#E5E7EB"
        BUTTON_SECONDARY_BORDER = "#D1D5DB"
        SUCCESS = "#10B981"
        SUCCESS_HOVER = "#059669"

        # --- Container principal para centralizar o card ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Card do Formulário ---
        form_card = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        form_card.grid(row=0, column=0, sticky="", padx=20, pady=20)

        # Frame interno para padding
        main_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        main_frame.pack(expand=True, padx=24, pady=20)

        # --- Título ---
        ctk.CTkLabel(
            main_frame,
            text="Novo Usuário",
            font=fonts.TITULO_SECAO,
            text_color=TEXT_PRIMARY,
            justify="left",  
        ).pack(pady=(0, 20), anchor="w", fill="x") 

        # --- Campos de Dados ---
        ctk.CTkLabel(
            main_frame,
            text="Nome de Usuário",
            font=fonts.LABEL_FONT,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w")
        self.user_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Apenas letras, números, _ ou -",
            font=fonts.TEXTO_NORMAL,
            height=36,
            corner_radius=8,
            border_color=BORDER,
        )
        self.user_entry.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(
            main_frame, text="Senha:", font=fonts.LABEL_FONT, text_color=TEXT_SECONDARY
        ).pack(anchor="w")
        self.pass_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite a senha",
            show="*",
            font=fonts.TEXTO_NORMAL,
            height=36,
            corner_radius=8,
            border_color=BORDER,
        )
        self.pass_entry.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(
            main_frame,
            text="Confirmar Senha:",
            font=fonts.LABEL_FONT,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w")
        self.confirm_pass_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Confirme a senha",
            show="*",
            font=fonts.TEXTO_NORMAL,
            height=36,
            corner_radius=8,
            border_color=BORDER,
        )
        self.confirm_pass_entry.pack(fill="x", pady=4)

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(24, 0))
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
            text_color=TEXT_PRIMARY,
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
        # Passa a janela para o callback poder fechá-la
        self.save_callback(data, self.winfo_toplevel())
