import os
import customtkinter as ctk
import tkfontawesome as fa
from tkinter import messagebox
from PIL import Image as PIL_Image, ImageOps
from ... import fonts
from ...utils import resource_path

from .home_view import HomeView
from .gerenciar_colaboradores_view import GerenciarColaboradoresView
from .cadastro_manual_view import CadastroManualView
from .edicao_lote_view import EdicaoEmLoteView
from .gerador_escala_view import GeradorEscalaView


class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller, user_data, app_version):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller
        self.sidebar_expanded = True
        self.user_data = user_data
        self.username = self.user_data.get("username", "Usuário").title()

        # === PALETA DE CORES HIERÁRQUICA ===
        # Cores primárias
        PRIMARY = "#0078D7"
        PRIMARY_HOVER = "#005EA6"

        # Cores de superfície
        SURFACE = "#FFFFFF"
        SURFACE_SECONDARY = "#FAFAFA"
        BACKGROUND = "#F5F6FA"

        # Bordas e divisores
        BORDER = "#E1E4E8"
        BORDER_LIGHT = "#F0F0F0"

        # Textos
        TEXT_PRIMARY = "#1E1E1E"
        TEXT_SECONDARY = "#6B6B6B"
        TEXT_TERTIARY = "#9CA3AF"

        # Botões de navegação
        NAV_INACTIVE_BG = "#F3F4F6"
        NAV_INACTIVE_HOVER = "#E5E7EB"
        NAV_INACTIVE_TEXT = "#4B5563"

        # Ícones
        ICON_INACTIVE = "#6B7280"
        ICON_ACTIVE = "#FFFFFF"

        # Botão de sair (danger)
        DANGER = "#DC2626"
        DANGER_HOVER = "#B91C1C"

        # === LAYOUT BASE ===
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # === SIDEBAR ===
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=SURFACE,
            border_color=BORDER,
            border_width=1,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # === ÍCONES COLORIDOS ===
        icon_size = 20

        self.icons_colored = {
            "home_active": fa.icon_to_image(
                "home", fill=ICON_ACTIVE, scale_to_height=icon_size
            ),
            "home_inactive": fa.icon_to_image(
                "home", fill=ICON_INACTIVE, scale_to_height=icon_size
            ),
            "calendar_active": fa.icon_to_image(
                "calendar-alt", fill=ICON_ACTIVE, scale_to_height=icon_size
            ),
            "calendar_inactive": fa.icon_to_image(
                "calendar-alt", fill=ICON_INACTIVE, scale_to_height=icon_size
            ),
            "users_active": fa.icon_to_image(
                "users", fill=ICON_ACTIVE, scale_to_height=icon_size
            ),
            "users_inactive": fa.icon_to_image(
                "users", fill=ICON_INACTIVE, scale_to_height=icon_size
            ),
            "logout": fa.icon_to_image(
                "sign-out-alt", fill=ICON_ACTIVE, scale_to_height=icon_size
            ),
        }

        # === LOGO  ===
        logo_path = resource_path("geradorEscalas/assets/logo.png")

        try:
            pil_logo = PIL_Image.open(logo_path)
            max_size = (160, 80)  # limite máximo de largura e altura
            pil_logo.thumbnail(
                max_size, PIL_Image.Resampling.LANCZOS
            )  # mantém proporção
            pil_logo = ImageOps.contain(
                pil_logo, max_size
            )  # garante encaixe sem distorção

            self.company_logo = ctk.CTkImage(
                light_image=pil_logo,
                dark_image=pil_logo,
                size=pil_logo.size,  # usa o tamanho real, sem forçar
            )
        except Exception:
            self.company_logo = fa.icon_to_image(
                "building", fill="#6B7280", scale_to_height=56
            )

        logo_container = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent",
        )
        logo_container.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 20))

        ctk.CTkLabel(
            logo_container,
            text="",  # sem texto, apenas a imagem
            image=self.company_logo,
        ).pack(pady=(0, 0))

        # Divisor abaixo da logo
        divider_top = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=BORDER_LIGHT)
        divider_top.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

        # === ESTILOS DOS BOTÕES ===
        self.style_inactive = {
            "fg_color": NAV_INACTIVE_BG,
            "text_color": NAV_INACTIVE_TEXT,
            "hover_color": NAV_INACTIVE_HOVER,
        }

        self.style_active = {
            "fg_color": PRIMARY,
            "text_color": ICON_ACTIVE,
            "hover_color": PRIMARY_HOVER,
        }

        # === BOTÕES DE NAVEGAÇÃO ===
        self.nav_buttons = {}

        button_info = [
            ("home", "  Início", "home", self.show_home_view, 2),
            ("escala", "  Gerar Escala", "calendar", self.show_escala_wizard, 3),
            (
                "colaboradores",
                "  Colaboradores",
                "users",
                self.show_colaboradores_view,
                4,
            ),
        ]

        for name, text, icon_key, command, row in button_info:
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                image=self.icons_colored[f"{icon_key}_inactive"],
                compound="left",
                anchor="w",
                font=fonts.BUTTON_FONT,
                command=lambda cmd=command, btn_name=name: self._navigate(
                    cmd, btn_name
                ),
                height=44,
                corner_radius=8,
                border_spacing=10,
            )
            button.configure(**self.style_inactive)
            button.grid(row=row, column=0, padx=16, pady=4, sticky="ew")
            self.nav_buttons[name] = button

        # === DIVISOR ANTES DO LOGOUT ===
        divider_bottom = ctk.CTkFrame(
            self.sidebar_frame, height=1, fg_color=BORDER_LIGHT
        )
        divider_bottom.grid(row=5, column=0, sticky="ew", padx=20, pady=8)

        # === BOTÃO DE SAIR ===
        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="  Sair",
            image=self.icons_colored["logout"],
            compound="left",
            anchor="w",
            command=self.logout,
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            text_color=ICON_ACTIVE,
            font=fonts.BUTTON_FONT,
            height=44,
            corner_radius=8,
            border_spacing=10,
        )
        self.logout_button.grid(row=6, column=0, padx=16, pady=(0, 16), sticky="ew")

        # === ÁREA DE CONTEÚDO ===
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Inicia na Home
        self._navigate(self.show_home_view, "home")

    # === MÉTODOS DE NAVEGAÇÃO ===
    def _navigate(self, command, button_name):
        command()
        self._highlight_button(button_name)

    def _highlight_button(self, active_button_name):
        for name, button in self.nav_buttons.items():
            icon_key = (
                "home"
                if name == "home"
                else ("calendar" if name == "escala" else "users")
            )
            if name == active_button_name:
                button.configure(
                    **self.style_active, image=self.icons_colored[f"{icon_key}_active"]
                )
            else:
                button.configure(
                    **self.style_inactive,
                    image=self.icons_colored[f"{icon_key}_inactive"],
                )

    def _show_content(self, ViewClass, **kwargs):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        view = ViewClass(self.content_frame, **kwargs)
        view.pack(expand=True, fill="both")

    def show_home_view(self):
        self._show_content(HomeView, app_controller=self.app_controller, main_view=self)
        

    def show_escala_wizard(self):
        self._show_content(GeradorEscalaView, app_controller=self.app_controller)

    def show_colaboradores_view(self, invalid_rows=None):
        self._show_content(
            GerenciarColaboradoresView,
            app_controller=self.app_controller,
            data_to_load=invalid_rows,
        )

    def show_cadastro_manual_view(self, matricula_para_editar=None):
        """Mostra a tela de cadastro manual, passando a matrícula se estiver em modo de edição."""
        self._show_content(
            CadastroManualView,
            app_controller=self.app_controller,
            matricula_para_editar=matricula_para_editar,
        )

    # --- MÉTODO NOVO ADICIONADO AQUI ---
    def show_edicao_lote_view(self, dados_selecionados):
        self._show_content(
            EdicaoEmLoteView,
            app_controller=self.app_controller,
            dados_para_editar=dados_selecionados,
        )

    def logout(self):
        if messagebox.askyesno(
            "Sair", "Tem certeza que deseja sair do sistema?", parent=self
        ):
            self.app_controller.logout()
