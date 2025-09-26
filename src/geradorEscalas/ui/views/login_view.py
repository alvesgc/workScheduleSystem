# src/gerador_escalas/ui/views/login_view.py

import customtkinter as ctk

class LoginWindow(ctk.CTk):
    def __init__(self, login_callback, register_callback):
        super().__init__()
        
        self.title("Acesso ao Sistema")
        self.geometry("400x480")
        self.resizable(False, False)
        
        self.login_callback = login_callback
        self.register_callback = register_callback

        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, padx=40, pady=40)
        
        ctk.CTkLabel(main_frame, text="Acesso ao Sistema", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(main_frame, text="Utilize suas credenciais para continuar").pack(pady=(0, 30))
        
        ctk.CTkLabel(main_frame, text="Usuário", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(main_frame, textvariable=self.user_var, width=300, height=40, placeholder_text="seu.usuario").pack(pady=(0, 20))
        
        ctk.CTkLabel(main_frame, text="Senha", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(main_frame, textvariable=self.pass_var, show="*", width=300, height=40).pack(pady=(0, 25))
        
        ctk.CTkButton(self, text="Entrar", command=self._try_login, height=45, font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=40)
        ctk.CTkButton(self, text="Cadastrar Novo Usuário", command=self.register_callback, fg_color="transparent", hover_color="#4A4A4A").pack(pady=15, fill="x", padx=40)

    def _try_login(self):
        self.login_callback(self.user_var.get(), self.pass_var.get())