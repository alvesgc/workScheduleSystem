import customtkinter as ctk
from ... import fonts

class UserRegistrationView(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback):
        super().__init__(master, fg_color="transparent")
        
        if hasattr(master, 'title'):
            master.title("Cadastro de Novo Usuário")
        if hasattr(master, 'geometry'):
            master.geometry("450x450")
        if hasattr(master, 'resizable'):
            master.resizable(False, False)

        self.save_callback = save_callback
        self.back_callback = back_callback
        
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()
        self.confirm_pass_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value='user')

        # Usamos 'self' como o container para os widgets, pois a classe é o próprio frame
        ctk.CTkLabel(self, text="Cadastro de Usuário", font=fonts.TITULO_SECAO).pack(pady=(20, 30))

        ctk.CTkLabel(self, text="Nome de Usuário:", anchor="w", width=300, font=fonts.LABEL_FONT).pack()
        ctk.CTkEntry(self, textvariable=self.user_var, width=300, height=40).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Senha:", anchor="w", width=300, font=fonts.LABEL_FONT).pack()
        ctk.CTkEntry(self, textvariable=self.pass_var, show="*", width=300, height=40).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Confirmar Senha:", anchor="w", width=300, font=fonts.LABEL_FONT).pack()
        ctk.CTkEntry(self, textvariable=self.confirm_pass_var, show="*", width=300, height=40).pack(pady=(0, 15))

        ctk.CTkLabel(self, text="Tipo de Acesso (Role):", anchor="w", width=300, font=fonts.LABEL_FONT).pack()
        ctk.CTkComboBox(self, variable=self.role_var, values=['user', 'admin'], state='readonly', width=300, height=40).pack(pady=(0, 25))
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill='x', padx=50)

        ctk.CTkButton(button_frame, text="Salvar Cadastro", command=self._save, height=45).pack(side='left', expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Voltar", command=self.back_callback, fg_color="#7A7A7A", hover_color="#5E5E5E").pack(side='left', expand=True, padx=(5, 0))

    def _save(self):
        dados = {"username": self.user_var.get(), "password": self.pass_var.get(), "confirm_password": self.confirm_pass_var.get(), "role": self.role_var.get()}
        self.save_callback(dados)