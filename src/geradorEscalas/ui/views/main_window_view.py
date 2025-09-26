import customtkinter as ctk
from tkinter import messagebox
import tkfontawesome as fa

# --- NOVO WIDGET DE BOTÃO CUSTOMIZADO ---
class SidebarButton(ctk.CTkFrame):
    def __init__(self, master, icon, text, command):
        super().__init__(master, fg_color="transparent", corner_radius=6)
        
        self.command = command
        
        # Cores para o efeito hover
        self.default_color = "transparent"
        self.hover_color = "#4A4A4A"

        # Configura o grid interno para alinhar o ícone e o texto
        self.grid_columnconfigure(0, weight=0) # Coluna do ícone com largura fixa
        self.grid_columnconfigure(1, weight=1) # Coluna do texto expande
        self.grid_rowconfigure(0, weight=1)

        # Label para o ícone
        self.icon_label = ctk.CTkLabel(self, text="", image=icon)
        self.icon_label.grid(row=0, column=0, padx=(15, 10), pady=10)

        # Label para o texto
        self.text_label = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=14), anchor="w")
        self.text_label.grid(row=0, column=1, padx=(0, 15), sticky="w")
        
        # Vincula eventos de clique e hover a todos os componentes
        self.bind_all_children("<Button-1>", self._on_click)
        self.bind_all_children("<Enter>", self._on_enter)
        self.bind_all_children("<Leave>", self._on_leave)

    def _on_click(self, event=None):
        if self.command:
            self.command()

    def _on_enter(self, event=None):
        self.configure(fg_color=self.hover_color)

    def _on_leave(self, event=None):
        self.configure(fg_color=self.default_color)

    def bind_all_children(self, sequence, func):
        """Aplica um evento a si mesmo e a todos os widgets filhos."""
        self.bind(sequence, func)
        for child in self.winfo_children():
            child.bind(sequence, func)
            
    def update_text_anchor(self, text, anchor):
        """Atualiza o texto e a âncora para o modo recolhido/expandido."""
        self.text_label.configure(text=text)
        if anchor == "center":
            self.icon_label.grid_configure(padx=0)
            self.grid_columnconfigure(0, weight=1)
        else:
            self.icon_label.grid_configure(padx=(15, 10))
            self.grid_columnconfigure(0, weight=0)


class MainWindow(ctk.CTk):
    def __init__(self, nav_callbacks):
        super().__init__()

        self.title("Gerador de Escalas Profissional")
        self.state("zoomed")
        self.resizable(True, True)

        self.nav_callbacks = nav_callbacks
        self.sidebar_expanded = True

        self.grid_columnconfigure(0, minsize=250) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

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
        self.hamburger_button.grid(row=0, column=0, padx=20, pady=20)
        
        # --- UTILIZANDO O NOVO WIDGET DE BOTÃO ---
        self.home_button = SidebarButton(self.sidebar_frame, icon=self.icon_home, text="Início", command=nav_callbacks["home"])
        self.home_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.escala_button = SidebarButton(self.sidebar_frame, icon=self.icon_calendar, text="Gerar Escala", command=nav_callbacks["gerar_escala"])
        self.escala_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.colab_button = SidebarButton(self.sidebar_frame, icon=self.icon_users, text="Colaboradores", command=nav_callbacks["colaboradores"])
        self.colab_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Sair", image=self.icon_logout, compound="left", anchor="w", command=nav_callbacks["sair"], fg_color="#C43E3E", hover_color="#A03030")
        self.logout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
            
    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        
        if self.sidebar_expanded:
            self.grid_columnconfigure(0, minsize=250)
            self.home_button.update_text_anchor(text="Início", anchor="w")
            self.escala_button.update_text_anchor(text="Gerar Escala", anchor="w")
            self.colab_button.update_text_anchor(text="Colaboradores", anchor="w")
            self.logout_button.configure(text="Sair", anchor="w")
            self.hamburger_button.configure(image=self.icon_menu)
        else:
            self.grid_columnconfigure(0, minsize=70)
            self.home_button.update_text_anchor(text="", anchor="center")
            self.escala_button.update_text_anchor(text="", anchor="center")
            self.colab_button.update_text_anchor(text="", anchor="center")
            self.logout_button.configure(text="", anchor="center")
            self.hamburger_button.configure(image=self.icon_close)
            
    def show_view(self, ViewClass, *args, **kwargs):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        view = ViewClass(self.content_frame, *args, **kwargs)
        view.grid(row=0, column=0, sticky="nsew")