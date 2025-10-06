import os
import customtkinter as ctk
import tkfontawesome as fa
from tkinter import Image, messagebox

# Importa as outras views que serão exibidas DENTRO desta
from .home_view import HomeView
from .gerenciar_colaboradores_view import GerenciarColaboradoresView
from .cadastro_manual_view import CadastroManualView
from .edicao_lote_view import EdicaoEmLoteView

class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller, user_data, photo_path=None):
        super().__init__(master, fg_color="#242424")
        self.app_controller = app_controller
        self.sidebar_expanded = True
        self.user_data = user_data
        
        self.username = self.user_data.get('username', 'Usuário').title()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#2B2B2B")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        # --- Ícones ---
        icon_color = "#E0E0E0"
        icon_size = 20
        self.icons = {
            "home": fa.icon_to_image("home", fill=icon_color, scale_to_height=icon_size),
            "calendar": fa.icon_to_image("calendar-alt", fill=icon_color, scale_to_height=icon_size),
            "users": fa.icon_to_image("users", fill=icon_color, scale_to_height=icon_size),
            "logout": fa.icon_to_image("sign-out-alt", fill=icon_color, scale_to_height=icon_size),
            "menu": fa.icon_to_image("bars", fill=icon_color, scale_to_height=icon_size),
            "close": fa.icon_to_image("times", fill=icon_color, scale_to_height=icon_size), # NOVO: Ícone de fechar
            "user_profile": fa.icon_to_image("user-circle", fill=icon_color, scale_to_height=36)
        }   
        try:
            user_image_path = photo_path if photo_path and os.path.exists(photo_path) else "caminho/para/user_generic.png"
            user_pil_image = Image.open(user_image_path).resize((36, 36))
            self.icons["user_profile"] = ctk.CTkImage(user_pil_image)
        except Exception:
            # Fallback para o ícone de FontAwesome se a imagem falhar
            self.icons["user_profile"] = fa.icon_to_image("user-circle", fill="#E0E0E0", scale_to_height=36)
            self.hamburger_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.icons["menu"], width=40, command=self.toggle_sidebar, fg_color="transparent", hover_color="#4A4A4A")
            self.hamburger_button.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # --- Frame do Perfil do Usuário ---
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        
        large_user_icon = fa.icon_to_image("user-circle", fill=icon_color, scale_to_height=48)
        self.profile_icon = ctk.CTkLabel(self.profile_frame, text="", image=large_user_icon)
        self.profile_icon.pack(pady=(5, 5)) 
        
        username = self.user_data.get('username', 'Usuário').title()
        
        self.profile_name = ctk.CTkLabel(self.profile_frame, text=self.username, font=("", 14, "bold"))
        self.profile_name.pack(pady=(0, 10))

        # --- Dicionário e Estilos para Botões de Navegação ---
        self.nav_buttons = {}
        self.style_inactive = {"fg_color": "transparent", "hover_color": "#3A3A3A"}
        self.style_active = {"fg_color": "#1F6AA5", "hover_color": "#1F6AA5"}

        button_info = [
            ("home", "Início", "home", self.show_home_view, 2),
            ("escala", "Gerar Escala", "calendar", self.show_escala_wizard, 3),
            ("colaboradores", "Colaboradores", "users", self.show_colaboradores_view, 4)
        ]

        for name, text, icon_key, command, row in button_info:
            button = ctk.CTkButton(self.sidebar_frame, text=text, image=self.icons[icon_key],
                                   compound="left", anchor="w", **self.style_inactive,
                                   command=lambda cmd=command, btn_name=name: self._navigate(cmd, btn_name))
            button.grid(row=row, column=0, padx=20, pady=12, sticky="ew")
            self.nav_buttons[name] = button

        # --- Botão de Sair ---
        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Sair", image=self.icons["logout"],
                                           compound="left", anchor="w", command=self.logout,
                                           fg_color="#C43E3E", hover_color="#A03030")
        self.logout_button.grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # --- Área de Conteúdo ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self._navigate(self.show_home_view, "home")
        
        # Inicia a aplicação
        self._navigate(self.show_home_view, "home")

    def _navigate(self, command, button_name):
        command()
        self._highlight_button(button_name)

    def _highlight_button(self, active_button_name):
        for name, button in self.nav_buttons.items():
            button.configure(**(self.style_active if name == active_button_name else self.style_inactive))

    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_content(self, ViewClass, *args, **kwargs):
        self._clear_content_frame()
        view = ViewClass(self.content_frame, *args, **kwargs)
        view.grid(row=0, column=0, sticky="nsew")

    def show_home_view(self):
        self._show_content(HomeView, 
                           gerar_escala_callback=self.show_escala_wizard,
                           gerenciar_colaboradores_callback=self.show_colaboradores_view)

    def show_escala_wizard(self):
        messagebox.showinfo("Navegação", "Aqui abriremos o assistente de Gerar Escala.")

    def show_colaboradores_view(self, invalid_rows=None):
        self._show_content(GerenciarColaboradoresView, 
                        app_controller=self.app_controller,
                        data_to_load=invalid_rows)

    # --- FUNÇÃO CORRIGIDA ---
    def show_cadastro_manual_view(self, matricula_para_editar=None):
        """Mostra a tela de cadastro manual, passando a matrícula se estiver em modo de edição."""
        self._show_content(CadastroManualView,
                           save_callback=self.app_controller.on_save_colaborador,
                           back_callback=self.show_colaboradores_view,
                           matricula_para_editar=matricula_para_editar)
     # --- MÉTODO NOVO ADICIONADO AQUI ---
    def show_edicao_lote_view(self, dados_selecionados):
        self._show_content(EdicaoEmLoteView,
                        app_controller=self.app_controller,
                        dados_para_editar=dados_selecionados)

    def logout(self):
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair do sistema?", parent=self):
            self.app_controller.logout()

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        
        if self.sidebar_expanded:
            self.sidebar_frame.configure(width=250)
            self.hamburger_button.configure(image=self.icons["menu"])
            self.profile_name.configure(text=self.username)
            
            # --- CORREÇÃO: Acessar botões pelo dicionário ---
            self.nav_buttons['home'].configure(text="Início", anchor="w")
            self.nav_buttons['escala'].configure(text="Gerar Escala", anchor="w")
            self.nav_buttons['colaboradores'].configure(text="Colaboradores", anchor="w")
            
            self.logout_button.configure(text="Sair", anchor="w")
        else:
            self.sidebar_frame.configure(width=70)
            self.hamburger_button.configure(image=self.icons["close"])
            self.profile_name.configure(text="")

            # --- CORREÇÃO: Acessar botões pelo dicionário ---
            self.nav_buttons['home'].configure(text="", anchor="center")
            self.nav_buttons['escala'].configure(text="", anchor="center")
            self.nav_buttons['colaboradores'].configure(text="", anchor="center")
            
            self.logout_button.configure(text="", anchor="center")
        