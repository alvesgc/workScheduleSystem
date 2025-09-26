# src/geradorEscalas/ui/main_menu_screen.py

import customtkinter as ctk

class MainMenuScreen:
    def __init__(self, root, choice_callback):
        self.root = root
        self.choice_callback = choice_callback
        
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(main_frame, text="Menu Principal", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        ctk.CTkLabel(main_frame, text="Selecione uma opção para continuar:", font=ctk.CTkFont(size=14)).pack(pady=(0, 20))
        
        ctk.CTkButton(
            main_frame, text="Gerar Escala",
            command=lambda: self.choice_callback("gerar_escala"),
            height=50, font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=10)
                   
        ctk.CTkButton(
            main_frame, text="Cadastrar/Importar Colaboradores",
            command=lambda: self.choice_callback("cadastrar_colaborador"),
            height=50, font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=10)