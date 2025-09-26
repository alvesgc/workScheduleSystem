import customtkinter as ctk

class CadastroView(ctk.CTkFrame):
    def __init__(self, master, choice_callback, back_callback):
        super().__init__(master, fg_color="transparent")
        self.choice_callback = choice_callback
        self.back_callback = back_callback # Callback para voltar para a tela Home
        
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Gerenciar Colaboradores", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, pady=20, sticky="n")
        ctk.CTkLabel(self, text="Importe uma lista de colaboradores ou cadastre um novo manualmente.", font=ctk.CTkFont(size=16)).grid(row=1, column=0, pady=(0, 30), sticky="n")

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, pady=20, sticky="n")
        action_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            action_frame, text="Importar de Planilha Excel",
            command=lambda: self.choice_callback("importar"),
            height=60, font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
                   
        ctk.CTkButton(
            action_frame, text="Cadastrar Manualmente",
            command=lambda: self.choice_callback("manual"),
            height=60, font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(self, text="< Voltar ao Início", command=self.back_callback, width=150).grid(row=3, column=0, pady=40, sticky="n")