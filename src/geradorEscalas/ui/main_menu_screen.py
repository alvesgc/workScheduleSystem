# --- TELA DE MENU PRINCIPAL ---
class MainMenuScreen:
    def __init__(self, root, choice_callback):
        self.root = root
        self.root.title("Menu Principal")
        self.root.geometry("400x250")
        self.choice_callback = choice_callback
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Bem-vindo!", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(main_frame, text="Selecione uma opção para continuar:").pack(pady=5)
        
        btn_gerar = ttk.Button(main_frame, text="Gerar Escala", 
                               command=lambda: self.choice_callback("gerar_escala"),
                               style='Accent.TButton')
        btn_gerar.pack(fill="x", pady=10, ipady=10)
                   
        btn_cadastrar = ttk.Button(main_frame, text="Cadastrar/Importar Colaboradores",
                                   command=lambda: self.choice_callback("cadastrar_colaborador"))
        btn_cadastrar.pack(fill="x", pady=10, ipady=10)