# src/geradorEscalas/__main__.py

import customtkinter as ctk
from tkinter import messagebox
import bcrypt
from PIL import Image

# Importações relativas ao pacote
from .ui.login_screen import LoginView
# from .ui.main_menu_screen import MainMenuView # Futuras importações
from . import database as db

# --- DEFINIÇÕES GLOBAIS DO CUSTOMTKINTER ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerador de Escalas Profissional")
        
        # --- RESPONSIVIDADE E TELA CHEIA ---
        # Deixa a janela maximizada ao iniciar
        self.state('zoomed')
        # Permite que o usuário redimensione a janela se desejar
        self.resizable(True, True) 

        # --- Layout Principal com Grid ---
        # Configura o grid para ter duas colunas e uma linha que se expandem
        self.grid_columnconfigure(0, weight=1) # Painel esquerdo (peso 1)
        self.grid_columnconfigure(1, weight=2) # Painel direito (peso 2, crescerá mais)
        self.grid_rowconfigure(0, weight=1)    # A linha única ocupa toda a altura

        # --- Painel Esquerdo (Imagem/Logo) ---
        self.left_panel = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        # Configura o grid interno do painel para centralizar a logo
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        try:
            logo_image = ctk.CTkImage(Image.open("src/geradorEscalas/logo.png"), size=(300, 300))
            logo_label = ctk.CTkLabel(self.left_panel, image=logo_image, text="")
            logo_label.grid(row=0, column=0) # Usa grid para centralizar
        except Exception as e:
            print(f"AVISO: logo.png não encontrada. {e}")

        # --- Painel Direito (Conteúdo Dinâmico) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="#242424", corner_radius=0)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        # Configura o grid do painel direito para centralizar seu conteúdo
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.current_view = None
        self.show_login_view()

    def _clear_right_panel(self):
        """Limpa todos os widgets do painel de conteúdo direito."""
        for widget in self.right_panel.winfo_children():
            widget.destroy()

    def show_login_view(self):
        self._clear_right_panel()
        self.current_view = LoginView(self.right_panel, 
                                      login_callback=self.on_login, 
                                      register_callback=self.show_user_registration_view)
        # --- CORREÇÃO: Usa grid para posicionar a view ---
        # Isso garante que ela fique centralizada no painel direito
        self.current_view.grid(row=0, column=0, sticky="")

    def on_login(self, username, password):
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            messagebox.showinfo("Sucesso", f"Login bem-sucedido, {username}!")
            # self.show_main_menu_view() # Próximo passo
        else:
            messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.")

    def show_user_registration_view(self):
        messagebox.showinfo("Navegação", "Aqui abriremos a tela de Cadastro de Usuário no painel direito.")
        # Lógica para mostrar a tela de cadastro...

if __name__ == "__main__":
    app = App()
    app.mainloop()