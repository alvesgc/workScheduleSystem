# src/geradorEscalas/ui/login_screen.py

import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, login_callback, register_callback):
        # O 'master' agora é o painel direito da janela principal
        super().__init__(master, fg_color="transparent")
        
        self.login_callback = login_callback
        self.register_callback = register_callback
        
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()

        # Configura o grid interno deste frame
        self.grid_columnconfigure(0, weight=1)
        
        # --- Widgets ---
        ctk.CTkLabel(self, text="Acesso ao Sistema", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, pady=(0, 10))
        ctk.CTkLabel(self, text="Utilize suas credenciais para continuar").grid(row=1, column=0, pady=(0, 30))
        
        ctk.CTkLabel(self, text="Usuário", font=ctk.CTkFont(size=14)).grid(row=2, column=0, sticky="w", padx=20)
        ctk.CTkEntry(self, textvariable=self.user_var, width=300, height=40, placeholder_text="seu.usuario").grid(row=3, column=0, pady=(0, 20), padx=20)
        
        ctk.CTkLabel(self, text="Senha", font=ctk.CTkFont(size=14)).grid(row=4, column=0, sticky="w", padx=20)
        ctk.CTkEntry(self, textvariable=self.pass_var, show="*", width=300, height=40).grid(row=5, column=0, pady=(0, 25), padx=20)
        
        ctk.CTkButton(
            self, text="Entrar", 
            command=self._try_login, 
            height=45, font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=6, column=0, sticky="ew", padx=20)
        
        ctk.CTkButton(
            self, text="Cadastrar Novo Usuário", 
            command=self.register_callback, 
            fg_color="transparent", hover_color="#4A4A4A"
        ).grid(row=7, column=0, pady=15, sticky="ew", padx=20)

    def _try_login(self):
        # Adiciona uma verificação para não enviar dados vazios
        if not self.user_var.get() or not self.pass_var.get():
            messagebox.showwarning("Atenção", "Por favor, preencha usuário e senha.", parent=self)
            return
        self.login_callback(self.user_var.get(), self.pass_var.get())