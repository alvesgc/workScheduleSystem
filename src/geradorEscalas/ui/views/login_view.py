import customtkinter as ctk
from PIL import Image
import os

class LoginView(ctk.CTkFrame):
    def __init__(self, master, login_callback, register_callback):
        super().__init__(master, fg_color="#242424")

        self.login_callback = login_callback
        self.register_callback = register_callback
        
        # Frame que centraliza todo o conteúdo de login
        login_container = ctk.CTkFrame(self, fg_color="transparent")
        login_container.pack(expand=True)

        try:
          logo_image_pil = Image.open("src/geradorEscalas/assets/logoUpa.png")
          logo_image = ctk.CTkImage(logo_image_pil, size=(450, 158))
          logo_label = ctk.CTkLabel(login_container, image=logo_image, text="")
          logo_label.pack(pady=(0, 30))
        except Exception as e:
            print(f"AVISO: logo.png não encontrada. {e}")
            ctk.CTkLabel(login_container, text="Gerador de Escalas", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(20, 30))

        form_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        form_frame.pack(padx=40, pady=20)

        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()

        ctk.CTkLabel(form_frame, text="Usuário", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(form_frame, textvariable=self.user_var, width=300, height=40, placeholder_text="seu.usuario").pack(pady=(0, 20))
        
        ctk.CTkLabel(form_frame, text="Senha", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(form_frame, textvariable=self.pass_var, show="*", width=300, height=40).pack(pady=(0, 25))
        
        ctk.CTkButton(form_frame, text="Entrar", command=self._try_login, height=45, font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x")
        ctk.CTkButton(form_frame, text="Cadastrar Novo Usuário", command=self.register_callback, fg_color="transparent", hover_color="#4A4A4A").pack(pady=15, fill="x")

    def _try_login(self):
        self.login_callback(self.user_var.get(), self.pass_var.get())