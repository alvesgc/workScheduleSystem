class LoginScreen:
    def __init__(self, root, login_callback):
        self.root = root
        self.root.title("Login - Gerador de Escalas")
        self.root.geometry("350x220")
        self.root.resizable(False, False)
        
        self.login_callback = login_callback
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        style = ttk.Style(self.root)
        style.theme_use('vista')

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True)
        
        ttk.Label(main_frame, text="Usuário:", font=("Helvetica", 10)).pack(anchor="w")
        ttk.Entry(main_frame, textvariable=self.user_var, width=35).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Senha:", font=("Helvetica", 10)).pack(anchor="w")
        ttk.Entry(main_frame, textvariable=self.pass_var, show="*", width=35).pack(pady=(0, 15))
        
        ttk.Button(main_frame, text="Entrar", command=self._try_login, style='Accent.TButton').pack(pady=5)
        
        self.root.bind('<Return>', self._try_login)
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

    def _try_login(self, event=None):
        username = self.user_var.get()
        password = self.pass_var.get()
        self.login_callback(username, password)
