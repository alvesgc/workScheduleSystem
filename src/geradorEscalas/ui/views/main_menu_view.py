import customtkinter as ctk

class MainMenuView(ctk.CTkFrame):
    def __init__(self, master, choice_callback):
        super().__init__(master, fg_color="transparent")
        self.choice_callback = choice_callback
        
        ctk.CTkLabel(self, text="Menu Principal", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Selecione uma opção para continuar:", font=ctk.CTkFont(size=16)).pack(pady=(0, 30))
        
        ctk.CTkButton(
            self, text="Gerar Escala",
            command=lambda: self.choice_callback("gerar_escala"),
            height=60, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(fill="x", pady=10, padx=50)
                   
        ctk.CTkButton(
            self, text="Gerenciar Colaboradores",
            command=lambda: self.choice_callback("cadastrar_colaborador"),
            height=60, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(fill="x", pady=10, padx=50)