# src/geradorEscalas/ui/user_registration_view.py

import customtkinter as ctk

class UserRegistrationWindow(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback):
        super().__init__(master, fg_color="transparent")
        
        self.title("Cadastro de Novo Usuário")
        self.geometry("450x450")
        self.resizable(False, False)
        self.save_callback = save_callback
        self.back_callback = back_callback

        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()
        self.confirm_pass_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value='user')

        ctk.CTkLabel(self, text="Cadastro de Usuário", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 30))

        ctk.CTkLabel(self, text="Nome de Usuário:", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(self, textvariable=self.user_var, width=300, height=40).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Senha:", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(self, textvariable=self.pass_var, show="*", width=300, height=40).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Confirmar Senha:", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkEntry(self, textvariable=self.confirm_pass_var, show="*", width=300, height=40).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Tipo de Acesso (Role):", anchor="w", width=300, font=ctk.CTkFont(size=14)).pack()
        ctk.CTkComboBox(self, variable=self.role_var, values=['user', 'admin'], state='readonly', width=300, height=40).pack(pady=(0, 25))
        
        ctk.CTkButton(self, text="Salvar Cadastro", command=self._save, height=45, font=ctk.CTkFont(size=14, weight="bold")).pack(fill='x', padx=50)
        ctk.CTkButton(self, text="Voltar para Login", command=self.back_callback, fg_color="transparent", hover_color="#4A4A4A").pack(pady=10, fill='x', padx=50)

    def _save(self):
        dados = {"username": self.user_var.get(), "password": self.pass_var.get(), "confirm_password": self.confirm_pass_var.get(), "role": self.role_var.get()}
        self.save_callback(dados)