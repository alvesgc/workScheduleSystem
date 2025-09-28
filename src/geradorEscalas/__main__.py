import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt
import pandas as pd

# Importa as classes da UI e os módulos de apoio
from .ui.views import LoginView, MainView, UserRegistrationView
from . import database as db
from . import fonts

# --- CONFIGURAÇÕES GLOBAIS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Escalas")
        self.state("zoomed")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.current_view = None
        self.show_login_view()

    def _show_view(self, ViewClass, *args, **kwargs):
        """Limpa a janela e exibe uma nova view principal nela."""
        if self.current_view:
            self.current_view.destroy()
        self.current_view = ViewClass(self, *args, **kwargs)
        self.current_view.pack(expand=True, fill="both")

    def show_login_view(self):
        self._show_view(LoginView, 
                        login_callback=self.on_login, 
                        register_callback=self.show_registration_view)

    def on_login(self, username, password):
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            self.show_main_view()
        else:
            messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.", parent=self)

    def show_main_view(self):
        self._show_view(MainView, app_controller=self)

    def show_registration_view(self):
        reg_window = ctk.CTkToplevel(self)
        view = UserRegistrationView(reg_window, 
                                    save_callback=lambda data: self.on_save_user(data, reg_window), 
                                    back_callback=reg_window.destroy)
        view.pack(expand=True, fill="both")
        reg_window.transient(self)
        reg_window.grab_set()
    
    def on_save_user(self, data, window_to_close):
        username, password, confirm_password, role = data.values()
        if not username or not password:
            messagebox.showwarning("Campos Vazios", "Usuário e Senha são obrigatórios.", parent=window_to_close)
            return
        if password != confirm_password:
            messagebox.showerror("Erro de Senha", "As senhas não coincidem.", parent=window_to_close)
            return
        success, message = db.add_user(username, password, role)
        if success:
            messagebox.showinfo("Sucesso", message, parent=window_to_close)
            window_to_close.destroy()
        else:
            messagebox.showerror("Erro no Cadastro", message, parent=window_to_close)

    def on_save_colaborador(self, dados):
        success, message = db.add_colaborador(dados)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            # Recarrega a view de cadastro para adicionar outro
            self.current_view.show_cadastro_manual_view()
        else:
            messagebox.showerror("Erro ao Salvar", message, parent=self)
            
    def on_import_colaboradores(self):
        # ... (A lógica de importação pode ser colocada aqui)
        messagebox.showinfo("Importar", "Lógica de importação a ser implementada aqui.")

if __name__ == "__main__":
    root = ctk.CTk()
    fonts.init_fonts()
    root.withdraw()
    app = App()