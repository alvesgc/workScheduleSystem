import tkinter as tk
from tkinter import ttk

class UserRegistrationScreen:
    def __init__(self, root, save_callback, back_callback):
        self.root = root
        self.root.title("Cadastro de Novo Usuário")
        self.root.geometry("400x350")
        self.save_callback = save_callback
        self.back_callback = back_callback

        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        self.confirm_pass_var = tk.StringVar()
        self.role_var = tk.StringVar(value='user')

        style = ttk.Style(self.root)
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True, fill='both')

        ttk.Label(main_frame, text="Novo Usuário", font=("Helvetica", 16, "bold")).pack(pady=10)

        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(pady=10)
        
        ttk.Label(fields_frame, text="Nome de Usuário:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(fields_frame, textvariable=self.user_var, width=30).grid(row=0, column=1, sticky="ew")

        ttk.Label(fields_frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(fields_frame, textvariable=self.pass_var, show="*", width=30).grid(row=1, column=1, sticky="ew")

        ttk.Label(fields_frame, text="Confirmar Senha:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(fields_frame, textvariable=self.confirm_pass_var, show="*", width=30).grid(row=2, column=1, sticky="ew")

        ttk.Label(fields_frame, text="Tipo de Acesso (Role):").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Combobox(fields_frame, textvariable=self.role_var, values=['user', 'admin'], state='readonly').grid(row=3, column=1, sticky="ew")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Salvar", command=self._save, style='Accent.TButton').pack(side='left', padx=10)
        ttk.Button(button_frame, text="Voltar para Login", command=self.back_callback).pack(side='left')

    def _save(self):
        dados = {
            "username": self.user_var.get(),
            "password": self.pass_var.get(),
            "confirm_password": self.confirm_pass_var.get(),
            "role": self.role_var.get()
        }
        self.save_callback(dados)