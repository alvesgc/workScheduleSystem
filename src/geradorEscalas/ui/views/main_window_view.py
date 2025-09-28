# src/gerador_escalas/ui/views/main_window_view.py

import customtkinter as ctk
import tkfontawesome as fa
from tkinter import messagebox

# Importa as outras views que serão exibidas DENTRO desta
from .home_view import HomeView
from .cadastro_view import CadastroView
from .cadastro_manual_view import CadastroManualView

class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#242424")
        self.app_controller = app_controller

        self.sidebar_expanded = True

        # --- Layout Principal ---
        # A MainView agora controla seu próprio grid interno
        self.grid_columnconfigure(0, minsize=250) # Define o tamanho inicial da sidebar
        self.grid_columnconfigure(1, weight=1)   # A área de conteúdo ocupa o resto
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        icon_color = "white"
        icon_size = 22
        self.icon_home = fa.icon_to_image("home", fill=icon_color, scale_to_height=icon_size)
        self.icon_calendar = fa.icon_to_image("calendar-alt", fill=icon_color, scale_to_height=icon_size)
        self.icon_users = fa.icon_to_image("users", fill=icon_color, scale_to_height=icon_size)
        self.icon_logout = fa.icon_to_image("sign-out-alt", fill=icon_color, scale_to_height=icon_size)
        self.icon_menu = fa.icon_to_image("bars", fill=icon_color, scale_to_height=icon_size)
        self.icon_close = fa.icon_to_image("times", fill=icon_color, scale_to_height=icon_size)
        
        self.hamburger_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.icon_menu, width=40,
                                              command=self.toggle_sidebar, fg_color="transparent", hover_color="#4A4A4A")
        self.hamburger_button.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.home_button = ctk.CTkButton(self.sidebar_frame, text="Início", image=self.icon_home, compound="left", anchor="w", command=self.show_home_view)
        self.home_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.escala_button = ctk.CTkButton(self.sidebar_frame, text="Gerar Escala", image=self.icon_calendar, compound="left", anchor="w", command=self.show_escala_wizard)
        self.escala_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.colab_button = ctk.CTkButton(self.sidebar_frame, text="Colaboradores", image=self.icon_users, compound="left", anchor="w", command=self.show_colaboradores_view)
        self.colab_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Sair", image=self.icon_logout, compound="left", anchor="w", command=self.logout, fg_color="#C43E3E", hover_color="#A03030")
        self.logout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # --- Área de Conteúdo ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.show_home_view()

    def toggle_sidebar(self):
        """Expande ou recolhe a barra lateral, alterando a configuração do grid da MainView."""
        self.sidebar_expanded = not self.sidebar_expanded
        
        if self.sidebar_expanded:
            # CORREÇÃO: Comanda o grid da própria MainView (self)
            self.grid_columnconfigure(0, minsize=250)
            self.home_button.configure(text="Início", anchor="w")
            self.escala_button.configure(text="Gerar Escala", anchor="w")
            self.colab_button.configure(text="Colaboradores", anchor="w")
            self.logout_button.configure(text="Sair", anchor="w")
            self.hamburger_button.configure(image=self.icon_close)
        else:
            # CORREÇÃO: Comanda o grid da própria MainView (self)
            self.grid_columnconfigure(0, minsize=70)
            self.home_button.configure(text="", anchor="center")
            self.escala_button.configure(text="", anchor="center")
            self.colab_button.configure(text="", anchor="center")
            self.logout_button.configure(text="", anchor="center")
            self.hamburger_button.configure(image=self.icon_menu)
            
    # --- Métodos de Navegação Interna ---
    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_content(self, ViewClass, *args, **kwargs):
        self._clear_content_frame()
        # Garante que o content_frame tenha um grid configurado para centralizar
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        view = ViewClass(self.content_frame, *args, **kwargs)
        view.grid(row=0, column=0, sticky="nsew")

    def show_home_view(self):
        self._show_content(HomeView, 
                           gerar_escala_callback=self.show_escala_wizard,
                           gerenciar_colaboradores_callback=self.show_colaboradores_view)

    def show_escala_wizard(self):
        messagebox.showinfo("Navegação", "Aqui abriremos o assistente de Gerar Escala.")

    def show_colaboradores_view(self):
        self._show_content(CadastroView,
                           choice_callback=self.on_cadastro_choice,
                           back_callback=self.show_home_view)
                           
    def on_cadastro_choice(self, choice):
        if choice == "importar":
            self.app_controller.on_import_colaboradores()
        elif choice == "manual":
            self.show_cadastro_manual_view()

    def show_cadastro_manual_view(self):
        self._show_content(CadastroManualView,
                           save_callback=self.on_save_colaborador,
                           back_callback=self.show_colaboradores_view)
                           
    def on_save_colaborador(self, dados):
        self.app_controller.on_save_colaborador(dados)

    def logout(self):
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair?", parent=self):
            self.app_controller.show_login_view()