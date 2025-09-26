# src/geradorEscalas/ui/cadastro_screen.py

import customtkinter as ctk

class CadastroScreen:
    def __init__(self, root, choice_callback):
        self.root = root
        self.root.title("Gestão de Colaboradores")
        self.root.geometry("400x300")
        self.choice_callback = choice_callback
        
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(main_frame, text="Gestão de Colaboradores", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(main_frame, text="Como deseja prosseguir?", font=ctk.CTkFont(size=14)).pack(pady=(0, 20))
        
        ctk.CTkButton(
            main_frame, text="Importar de Planilha Excel",
            command=lambda: self.choice_callback("importar"),
            height=50, font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=10)
                   
        ctk.CTkButton(
            main_frame, text="Cadastrar Manualmente",
            command=lambda: self.choice_callback("manual"),
            height=50, font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=10)