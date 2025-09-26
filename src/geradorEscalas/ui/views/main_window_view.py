import customtkinter as ctk
from PIL import Image
import os

class MainWindow(ctk.CTk):
    def __init__(self, nav_callbacks):
        super().__init__()

        self.title("Gerador de Escalas Profissional")
        self.state("zoomed")
        self.resizable(True, True)

        self.nav_callbacks = nav_callbacks
        self.sidebar_expanded = True # Variável de estado para controlar a sidebar

        # --- Layout Principal com Grid ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar de Navegação ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Espaço para empurrar o botão de sair

        # --- Carregar Ícones ---
        # Certifique-se de que os ícones estão na pasta correta
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../assets/icons")
        self.icon_home = ctk.CTkImage(Image.open(os.path.join(icon_path, "home.png")), size=(24, 24))
        self.icon_calendar = ctk.CTkImage(Image.open(os.path.join(icon_path, "calendar.png")), size=(24, 24))
        self.icon_users = ctk.CTkImage(Image.open(os.path.join(icon_path, "users.png")), size=(24, 24))
        self.icon_logout = ctk.CTkImage(Image.open(os.path.join(icon_path, "log-out.png")), size=(24, 24))
        self.icon_menu = ctk.CTkImage(Image.open(os.path.join(icon_path, "menu.png")), size=(24, 24))

        # --- Widgets da Sidebar ---
        self.hamburger_button = ctk.CTkButton(self.sidebar_frame, text="", image=self.icon_menu, width=40,
                                              command=self.toggle_sidebar, fg_color="transparent", hover_color="#4A4A4A")
        self.hamburger_button.grid(row=0, column=0, padx=20, pady=20)
        
        # Armazena os botões para poder modificar o texto depois
        self.home_button = ctk.CTkButton(self.sidebar_frame, text="Início", image=self.icon_home, compound="left", anchor="w", command=nav_callbacks["home"])
        self.home_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.escala_button = ctk.CTkButton(self.sidebar_frame, text="Gerar Escala", image=self.icon_calendar, compound="left", anchor="w", command=nav_callbacks["gerar_escala"])
        self.escala_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.colab_button = ctk.CTkButton(self.sidebar_frame, text="Colaboradores", image=self.icon_users, compound="left", anchor="w", command=nav_callbacks["colaboradores"])
        self.colab_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Sair", image=self.icon_logout, compound="left", anchor="w", command=nav_callbacks["sair"], fg_color="#C43E3E", hover_color="#A03030")
        self.logout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # --- Área de Conteúdo Principal ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        
        if self.sidebar_expanded:
            self.sidebar_frame.configure(width=250)
            self.home_button.configure(text="Início", anchor="w")
            self.escala_button.configure(text="Gerar Escala", anchor="w")
            self.colab_button.configure(text="Colaboradores", anchor="w")
            self.logout_button.configure(text="Sair", anchor="w")
        else:
            self.sidebar_frame.configure(width=70)
            self.home_button.configure(text="", anchor="center")
            self.escala_button.configure(text="", anchor="center")
            self.colab_button.configure(text="", anchor="center")
            self.logout_button.configure(text="", anchor="center")
            
    def show_view(self, ViewClass, *args, **kwargs):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        view = ViewClass(self.content_frame, *args, **kwargs)
        view.grid(row=0, column=0, sticky="nsew")