# src/gerador_escalas/ui/views/main_window_view.py

import customtkinter as ctk
import tkfontawesome as fa
from tkinter import messagebox

# Importa as outras views que serão exibidas DENTRO desta
from .home_view import HomeView
from .cadastro_view import CadastroView
from .cadastro_manual_view import CadastroManualView

class MainView(ctk.CTkFrame):
    def __init__(self, master, logout_callback):
        super().__init__(master, fg_color="#242424")
        self.logout_callback = logout_callback

        # --- Layout Principal ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Ícones...
        icon_color = "white"
        icon_size = 22
        self.icon_home = fa.icon_to_image("home", fill=icon_color, scale_to_height=icon_size)
        self.icon_calendar = fa.icon_to_image("calendar-alt", fill=icon_color, scale_to_height=icon_size)
        self.icon_users = fa.icon_to_image("users", fill=icon_color, scale_to_height=icon_size)
        self.icon_logout = fa.icon_to_image("sign-out-alt", fill=icon_color, scale_to_height=icon_size)

        ctk.CTkLabel(self.sidebar_frame, text="Navegação", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkButton(self.sidebar_frame, text="Início", image=self.icon_home, compound="left", anchor="w", command=self.show_home_view).grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="Gerar Escala", image=self.icon_calendar, compound="left", anchor="w", command=self.show_escala_wizard).grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="Colaboradores", image=self.icon_users, compound="left", anchor="w", command=self.show_colaboradores_view).grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="Sair", image=self.icon_logout, compound="left", anchor="w", command=self.logout, fg_color="#C43E3E", hover_color="#A03030").grid(row=5, column=0, padx=20, pady=20, sticky="s")

        # --- Área de Conteúdo ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    
    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_content(self, ViewClass, *args, **kwargs):
        self._clear_content_frame()
        view = ViewClass(self.content_frame, *args, **kwargs)
        view.pack(expand=True, fill="both")

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
            # Esta função agora precisa ser passada pelo controller principal
            messagebox.showinfo("Navegação", "Aqui chamaremos a função de importação.")
        elif choice == "manual":
            self.show_cadastro_manual_view()

    def show_cadastro_manual_view(self):
        self._show_content(CadastroManualView,
                           save_callback=self.on_save_colaborador,
                           back_callback=self.show_colaboradores_view)
                           
    def on_save_colaborador(self, dados):
        messagebox.showinfo("Navegação", f"Aqui chamaremos a função para salvar o colaborador: {dados['Nome']}")

    def logout(self):
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair?", parent=self):
            self.logout_callback()