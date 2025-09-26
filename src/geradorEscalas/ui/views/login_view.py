# src/gerador_escalas/ui/views/login_view.py

import customtkinter as ctk
from PIL import Image

class LoginView(ctk.CTkFrame):
    def __init__(self, master, login_callback, register_callback):
        super().__init__(master, fg_color="#242424")

        self.login_callback = login_callback
        self.register_callback = register_callback
        
        # --- Layout Principal com Grid ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- Painel Esquerdo (Imagem/Logo) ---
        self.left_panel = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        try:
            logo_image_pil = Image.open("src/gerador_escalas/assets/logoUpa.png")
            logo_image = ctk.CTkImage(logo_image_pil, size=(450, 158))
            logo_label = ctk.CTkLabel(self.left_panel, image=logo_image, text="")
            logo_label.grid(row=0, column=0)
        except Exception as e:
            print(f"AVISO: logo.png não encontrada. {e}")

        # --- Painel Direito (Formulário) ---
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=50)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        form_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_frame.grid(row=0, column=0) # Centraliza o formulário

        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()

        ctk.CTkLabel(form_frame, text="Acesso ao Sistema", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(form_frame, text="Utilize suas credenciais para continuar").pack(pady=(0, 30))
        
        ctk.CTkLabel(form_frame, text="Usuário", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(form_frame, textvariable=self.user_var, width=300, height=40, placeholder_text="seu.usuario").pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Senha", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(form_frame, textvariable=self.pass_var, show="*", width=300, height=40).pack(pady=(0, 25))
        
        ctk.CTkButton(form_frame, text="Entrar", command=self._try_login, height=45, font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x")
        ctk.CTkButton(form_frame, text="Cadastrar Novo Usuário", command=self.register_callback, fg_color="transparent", hover_color="#4A4A4A").pack(pady=15, fill="x")

    def _try_login(self):
        self.login_callback(self.user_var.get(), self.pass_var.get())