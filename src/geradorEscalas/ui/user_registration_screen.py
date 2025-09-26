# src/geradorEscalas/ui/user_registration_screen.py

import customtkinter as ctk

class UserRegistrationScreen:
    def __init__(self, root, save_callback, back_callback):
        self.root = root
        self.save_callback = save_callback
        self.back_callback = back_callback

        # Variáveis
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()
        self.confirm_pass_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value='user')

        # Configuração da janela (agora é um Frame dentro do Toplevel)
        self.root.title("Cadastro de Novo Usuário")
        self.root.geometry("450x400")

        main_frame = ctk.CTkFrame(root, fg_color="transparent")
        main_frame.pack(expand=True, fill='both', padx=30, pady=20)

        ctk.CTkLabel(main_frame, text="Cadastro de Usuário", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        ctk.CTkLabel(main_frame, text="Nome de Usuário:", anchor="w").pack(fill="x")
        ctk.CTkEntry(main_frame, textvariable=self.user_var, height=35).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Senha:", anchor="w").pack(fill="x")
        ctk.CTkEntry(main_frame, textvariable=self.pass_var, show="*", height=35).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Confirmar Senha:", anchor="w").pack(fill="x")
        ctk.CTkEntry(main_frame, textvariable=self.confirm_pass_var, show="*", height=35).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(main_frame, text="Tipo de Acesso (Role):", anchor="w").pack(fill="x")
        ctk.CTkComboBox(main_frame, variable=self.role_var, values=['user', 'admin'], state='readonly', height=35).pack(fill="x", pady=(0, 20))
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill='x')
        
        ctk.CTkButton(button_frame, text="Salvar", command=self._save, height=40).pack(side='left', expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Voltar para Login", command=self.back_callback, fg_color="#7A7A7A", hover_color="#5E5E5E").pack(side='left', expand=True, padx=(5, 0))

    def _save(self):
        dados = {
            "username": self.user_var.get(),
            "password": self.pass_var.get(),
            "confirm_password": self.confirm_pass_var.get(),
            "role": self.role_var.get()
        }
        self.save_callback(dados)