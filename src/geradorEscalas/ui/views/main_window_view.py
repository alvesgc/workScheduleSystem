import os
import customtkinter as ctk
import tkfontawesome as fa
from tkinter import messagebox
from PIL import Image as PIL_Image, ImageDraw
from ... import fonts

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

        # --- Paleta de cores hierárquica ---
        primary_color = "#0078D7"
        hover_primary = "#005EA6"
        surface_color = "#FFFFFF"
        sidebar_bg = "#FFFFFF"
        sidebar_border = "#E0E0E0"
        icon_inactive = "#A0A0A0"
        text_primary = "#1E1E1E"
        text_secondary = "#6B6B6B"
        danger_color = "#C43E3E"
        danger_hover = "#A03030"

        # --- Layout base ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=sidebar_bg,
            border_color=sidebar_border,
            border_width=1,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # --- Ícones ---
        icon_size = 20
        self.icons = {
            name: fa.icon_to_image(
                fa_name, fill=icon_inactive, scale_to_height=icon_size
            )
            for name, fa_name in {
                "home": "home",
                "calendar": "calendar-alt",
                "users": "users",
                "logout": "sign-out-alt",
                "menu": "bars",
                "close": "times",
            }.items()
        }

        # --- Perfil do usuário ---
        photo_path = self.user_data.get("foto_path")
        generic_photo_path = "src/geradorEscalas/assets/icons/user_generic.png"
        image_size = (48, 48)
        try:
            final_path = (
                photo_path
                if photo_path and os.path.exists(photo_path)
                else generic_photo_path
            )
            pil_image = PIL_Image.open(final_path).resize(
                image_size, PIL_Image.Resampling.LANCZOS
            )
            mask = PIL_Image.new("L", image_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + image_size, fill=255)
            circular_pil_image = PIL_Image.new("RGBA", image_size, (0, 0, 0, 0))
            circular_pil_image.paste(pil_image, (0, 0), mask)
            self.profile_image = ctk.CTkImage(
                light_image=circular_pil_image,
                dark_image=circular_pil_image,
                size=image_size,
            )
        except Exception:
            self.profile_image = fa.icon_to_image(
                "user-circle", fill=icon_inactive, scale_to_height=48
            )

        # --- Perfil ---
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        ctk.CTkLabel(self.profile_frame, text="", image=self.profile_image).pack(
            pady=(5, 5)
        )
        ctk.CTkLabel(
            self.profile_frame,
            text=self.username,
            font=fonts.LABEL_FONT,
            text_color=text_primary,
        ).pack(pady=(0, 10))

        # --- Botões de navegação ---
        self.nav_buttons = {}
        self.style_inactive = {
            "fg_color": "#E9ECEF",  # cinza mais visível
            "text_color": "#4A4A4A",  # texto escuro
            "hover_color": "#DCE2E8",  # leve destaque no hover
        }

        self.style_active = {
            "fg_color": "#0078D7",  # azul principal
            "text_color": "#FFFFFF",  # texto branco
            "hover_color": "#005EA6",  # azul escuro no hover
        }

        inactive_icon_color = "#3C3C3C"
        active_icon_color = "#FFFFFF"
        icon_size = 20

        self.icons_colored = {
            "home_active": fa.icon_to_image(
                "home", fill=active_icon_color, scale_to_height=icon_size
            ),
            "home_inactive": fa.icon_to_image(
                "home", fill=inactive_icon_color, scale_to_height=icon_size
            ),
            "calendar_active": fa.icon_to_image(
                "calendar-alt", fill=active_icon_color, scale_to_height=icon_size
            ),
            "calendar_inactive": fa.icon_to_image(
                "calendar-alt", fill=inactive_icon_color, scale_to_height=icon_size
            ),
            "users_active": fa.icon_to_image(
                "users", fill=active_icon_color, scale_to_height=icon_size
            ),
            "users_inactive": fa.icon_to_image(
                "users", fill=inactive_icon_color, scale_to_height=icon_size
            ),
            "logout": fa.icon_to_image(
                "sign-out-alt", fill="#FFFFFF", scale_to_height=icon_size
            ),
        }

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
                height=42,
                corner_radius=8,
                border_spacing=6,
            )
            button.configure(**self.style_inactive)
            button.grid(row=row, column=0, padx=16, pady=5, sticky="ew")
            self.nav_buttons[name] = button

        divider = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color="#E1E4E8")
        divider.grid(row=5, column=0, sticky="ew", padx=16, pady=(10, 10))

        # --- Botão de sair ---
        footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer_frame.grid(row=6, column=0, sticky="sew", padx=10, pady=10)
        footer_frame.grid_columnconfigure(0, weight=1)

        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="  Sair",
            image=self.icons_colored["logout"],
            compound="left",
            anchor="w",
            command=self.logout,
            fg_color="#C43E3E",
            hover_color="#A03030",
            font=fonts.BUTTON_FONT,
            height=42,
            corner_radius=8,
        )
        self.logout_button.grid(row=6, column=0, padx=16, pady=(0, 10), sticky="ew")

        # --- Área de conteúdo ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Inicia na Home
        self._navigate(self.show_home_view, "home")

    # --- Navegação ---
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

    def logout(self):
        if messagebox.askyesno(
            "Sair", "Tem certeza que deseja sair do sistema?", parent=self
        ):
            self.app_controller.logout()
