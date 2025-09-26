import customtkinter as ctk

class HomeView(ctk.CTkFrame):
    def __init__(self, master, gerar_escala_callback, gerenciar_colaboradores_callback):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Bem-vindo ao Gerador de Escalas", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, pady=20, sticky="n")
        ctk.CTkLabel(self, text="Selecione uma das ações principais abaixo para começar.", font=ctk.CTkFont(size=16)).grid(row=1, column=0, pady=(0, 30), sticky="n")

        # Frame para os botões de ação
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, pady=20, sticky="n")
        action_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            action_frame, text="Gerar Nova Escala",
            command=gerar_escala_callback,
            height=80, font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(
            action_frame, text="Gerenciar Colaboradores",
            command=gerenciar_colaboradores_callback,
            height=80, font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10, sticky="ew")