import customtkinter as ctk
from ... import fonts
from PIL import Image


class LoginView(ctk.CTkFrame):
    def __init__(self, master, login_callback, register_callback):
        # === PALETA DE CORES (TEMA CLARO) ===
        BACKGROUND_COLOR = "#F9FAFB"
        CARD_COLOR = "#FFFFFF"
        BORDER_COLOR = "#E5E7EB"
        PRIMARY_TEXT = "#111827"
        SECONDARY_TEXT = "#6B7280"
        PRIMARY_BUTTON = "#3B82F6"
        PRIMARY_BUTTON_HOVER = "#2563EB"

        # --- Fundo principal da tela ---
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.login_callback = login_callback
        self.register_callback = register_callback

        # --- Estrutura de Grid para centralizar o Card e posicionar o rodapé ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # --- Card do Formulário ---
        form_card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        form_card.grid(
            row=0, column=0, padx=20, pady=(20, 0)
        )  # CORRIGIDO: Removido sticky="s"

        # Frame interno para aplicar padding uniforme
        main_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        # CORRIGIDO: Removido expand=True e fill="both"
        main_frame.pack(
            padx=28, pady=28
        )  # Ajuste o pady total para o conteúdo interno do card

        # --- LOGO DA EMPRESA ---
        try:
            logo_image_path = (
                "src/geradorEscalas/assets/logo.png"  # Verifique o caminho
            )
            pil_image = Image.open(logo_image_path)
            logo_image = ctk.CTkImage(pil_image, size=(120, 32))

            logo_label = ctk.CTkLabel(main_frame, text="", image=logo_image)
            logo_label.pack(pady=(0, 20), anchor="center")
        except FileNotFoundError:
            ctk.CTkLabel(
                main_frame, text="Nome da Empresa", font=fonts.TITULO_APP
            ).pack(pady=(0, 20))

        # --- Títulos ---
        ctk.CTkLabel(
            main_frame,
            text="Bem-vindo de volta!",
            font=fonts.TITULO_SECAO,
            text_color=PRIMARY_TEXT,
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            main_frame,
            text="Faça login para acessar o sistema.",
            font=fonts.SUBTITULO,
            text_color=SECONDARY_TEXT,
        ).pack(anchor="w", pady=(0, 20))

        # --- Campo de Usuário ---
        ctk.CTkLabel(
            main_frame, text="Usuário", font=fonts.LABEL_FONT, text_color=PRIMARY_TEXT
        ).pack(anchor="w", pady=(0, 4))
        self.user_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite seu usuário",
            font=fonts.TEXTO_NORMAL,
            height=38,
            corner_radius=8,
            border_color=BORDER_COLOR,
        )
        self.user_entry.pack(
            fill="x", pady=0
        )  # CORRIGIDO: Removido ipady e ajustado pady

        # --- Campo de Senha ---
        ctk.CTkLabel(
            main_frame, text="Senha", font=fonts.LABEL_FONT, text_color=PRIMARY_TEXT
        ).pack(anchor="w", pady=(12, 4))
        self.pass_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite sua senha",
            show="*",
            font=fonts.TEXTO_NORMAL,
            height=40,
            corner_radius=8,
            border_color=BORDER_COLOR,
        )
        self.pass_entry.pack(
            fill="x", pady=0
        )  # CORRIGIDO: Removido ipady e ajustado pady
        self.pass_entry.bind("<Return>", self._try_login)

        # --- Botão de Login ---
        login_button = ctk.CTkButton(
            main_frame,
            text="Entrar",
            command=self._try_login,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=PRIMARY_BUTTON,
            hover_color=PRIMARY_BUTTON_HOVER,
            corner_radius=8,
        )
        login_button.pack(fill="x", pady=(24, 10))

        # --- Link de Cadastro ---
        register_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        register_frame.pack(fill="x")

        ctk.CTkLabel(
            register_frame,
            text="Não tem uma conta?",
            font=fonts.TEXTO_NORMAL,
            text_color=SECONDARY_TEXT,
        ).pack(side="left")

        register_button = ctk.CTkButton(
            register_frame,
            text="Cadastre-se",
            font=fonts.TEXTO_NORMAL,
            fg_color="transparent",
            text_color=PRIMARY_BUTTON,
            hover_color=BACKGROUND_COLOR,
            command=self.register_callback,
        )
        register_button.pack(side="left", padx=4)

        # --- Rodapé ---
        footer_label = ctk.CTkLabel(
            self,
            text="Desenvolvido por NetCode - 2025",
            font=fonts.TEXTO_PEQUENO,
            text_color=SECONDARY_TEXT,
        )
        footer_label.grid(row=1, column=0, sticky="s", padx=20, pady=(20, 20))

    def _try_login(self, event=None):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        if username and password:
            self.master.focus_set()
            self.login_callback(username, password)
