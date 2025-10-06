import customtkinter as ctk
import tkfontawesome as fa
from ... import fonts


class LoginView(ctk.CTkFrame):
    def __init__(self, master, login_callback, register_callback):
        super().__init__(master, fg_color="#242424")

        self.login_callback = login_callback
        self.register_callback = register_callback

        # --- REMOVIDO: As StringVars não são mais necessárias ---
        # self.user_var = ctk.StringVar()
        # self.pass_var = ctk.StringVar()

        # --- Estrutura de Grid para Centralização ---
        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_rowconfigure((0, 2), weight=1)

        form_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=15)
        form_frame.grid(row=1, column=1, padx=20, pady=20)

        # --- Ícones ---
        icon_color = "#DCE4EE"
        self.icons = {
            "user": fa.icon_to_image("user", fill=icon_color, scale_to_height=18),
            "lock": fa.icon_to_image("lock", fill=icon_color, scale_to_height=18),
        }

        # --- Títulos ---
        ctk.CTkLabel(form_frame, text="Bem vindo!", font=fonts.TITULO_SECAO).grid(
            row=0, column=0, columnspan=2, padx=40, pady=(40, 10)
        )
        ctk.CTkLabel(
            form_frame,
            text="Faça login para continuar",
            font=fonts.SUBTITULO,
            text_color="gray60",
        ).grid(row=1, column=0, columnspan=2, padx=40, pady=(0, 30))

        # --- Campo de Usuário ---
        ctk.CTkLabel(form_frame, text="", image=self.icons["user"]).grid(
            row=2, column=0, padx=(40, 10), pady=5, sticky="e"
        )
        # --- ALTERADO: Removido 'textvariable' e salvo o widget em 'self.user_entry' ---
        self.user_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Usuário",
            width=220,
            height=40,
            font=fonts.TEXTO_NORMAL,
        )
        self.user_entry.grid(row=2, column=1, padx=(0, 40), pady=5, sticky="w")

        # --- Campo de Senha ---
        ctk.CTkLabel(form_frame, text="", image=self.icons["lock"]).grid(
            row=3, column=0, padx=(40, 10), pady=5, sticky="e"
        )
        # --- ALTERADO: Removido 'textvariable' e salvo o widget em 'self.pass_entry' ---
        self.pass_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Senha",
            show="*",
            width=220,
            height=40,
            font=fonts.TEXTO_NORMAL,
        )
        self.pass_entry.grid(row=3, column=1, padx=(0, 40), pady=5, sticky="w")
        self.pass_entry.bind("<Return>", self._try_login)

        # --- Botões ---
        login_button = ctk.CTkButton(
            form_frame,
            text="Entrar",
            command=self._try_login,
            width=260,
            height=45,
            font=fonts.BUTTON_FONT,
        )
        login_button.grid(row=4, column=0, columnspan=2, padx=40, pady=(30, 10))

        register_button = ctk.CTkButton(
            form_frame,
            text="Cadastrar Novo Usuário",
            fg_color="transparent",
            hover_color="#3A3A3A",
            font=fonts.TEXTO_NORMAL,
            command=self.register_callback,
        )
        register_button.grid(row=5, column=0, columnspan=2, padx=40, pady=(0, 40))

    def _try_login(self, event=None):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        if username and password:
            self.master.focus_set()
            self.login_callback(username, password)
