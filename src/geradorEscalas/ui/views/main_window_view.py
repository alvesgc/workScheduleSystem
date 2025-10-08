import os
import customtkinter as ctk
import tkfontawesome as fa
from tkinter import messagebox
from PIL import Image as PIL_Image, ImageDraw
from ... import fonts
# Importa as outras views que serão exibidas DENTRO desta
from .home_view import HomeView
from .gerenciar_colaboradores_view import GerenciarColaboradoresView
from .cadastro_manual_view import CadastroManualView
from .edicao_lote_view import EdicaoEmLoteView
from .gerador_escala_view import GeradorEscalaView


class MainView(ctk.CTkFrame):
    def __init__(self, master, app_controller, user_data):
        super().__init__(master, fg_color="#242424")
        self.app_controller = app_controller
        self.sidebar_expanded = True
        self.user_data = user_data

        self.username = self.user_data.get("username", "Usuário").title()

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
            "home": fa.icon_to_image(
                "home", fill=icon_color, scale_to_height=icon_size
            ),
            "calendar": fa.icon_to_image(
                "calendar-alt", fill=icon_color, scale_to_height=icon_size
            ),
            "users": fa.icon_to_image(
                "users", fill=icon_color, scale_to_height=icon_size
            ),
            "logout": fa.icon_to_image(
                "sign-out-alt", fill=icon_color, scale_to_height=icon_size
            ),
            "menu": fa.icon_to_image(
                "bars", fill=icon_color, scale_to_height=icon_size
            ),
            "close": fa.icon_to_image(
                "times", fill=icon_color, scale_to_height=icon_size
            ),
        }

        photo_path = self.user_data.get("foto_path")
        generic_photo_path = "src/geradorEscalas/assets/icons/user_generic.png"
        image_size = (48, 48)
        try:
            final_path = None
            if photo_path and os.path.exists(photo_path):
                final_path = photo_path
            elif os.path.exists(generic_photo_path):
                final_path = final_path = generic_photo_path

            if final_path:
                pil_image = PIL_Image.open(final_path).resize(
                    image_size, PIL_Image.Resampling.LANCZOS
                )
                # --- AQUI ESTÁ A LÓGICA PARA TORNAR A IMAGEM CIRCULAR ---
                mask = PIL_Image.new("L", image_size, 0)  # Cria uma máscara preta
                draw = ImageDraw.Draw(mask)
                draw.ellipse(
                    (0, 0) + image_size, fill=255
                )  # Desenha um círculo branco na máscara

                # Aplica a máscara à imagem
                circular_pil_image = PIL_Image.new(
                    "RGBA", image_size, (0, 0, 0, 0)
                )  # Cria uma imagem transparente
                circular_pil_image.paste(
                    pil_image, (0, 0), mask
                )  # Cola a imagem original usando a máscara

                self.profile_image = ctk.CTkImage(
                    light_image=circular_pil_image,
                    dark_image=circular_pil_image,
                    size=image_size,
                )
            else:
                raise FileNotFoundError("Nenhuma imagem de perfil encontrada.")
        except Exception as e:
            print(
                f"AVISO: Não foi possível carregar a imagem de perfil ({e}). Usando ícone padrão."
            )
            self.profile_image = fa.icon_to_image(
                "user-circle", fill="#E0E0E0", scale_to_height=48
            )

        # --- Frame do Perfil do Usuário ---
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        self.profile_icon = ctk.CTkLabel(
            self.profile_frame, text="", image=self.profile_image
        )
        self.profile_icon.pack(pady=(5, 5))

        self.profile_name = ctk.CTkLabel(
            self.profile_frame, text=self.username, font=fonts.LABEL_FONT
        )
        self.profile_name.pack(pady=(0, 10))

        # --- Dicionário e Estilos para Botões de Navegação ---
        self.nav_buttons = {}
        self.style_inactive = {"fg_color": "transparent", "hover_color": "#3A3A3A"}
        self.style_active = {"fg_color": "#1F6AA5", "hover_color": "#1F6AA5"}

        button_info = [
            ("home", "Início", "home", self.show_home_view, 2),
            ("escala", "Gerar Escala", "calendar", self.show_escala_wizard, 3),
            (
                "colaboradores",
                "Colaboradores",
                "users",
                self.show_colaboradores_view,
                4,
            ),
        ]

        for name, text, icon_key, command, row in button_info:
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                image=self.icons[icon_key],
                compound="left",
                anchor="w",
                font=fonts.BUTTON_FONT,
                command=lambda cmd=command, btn_name=name: self._navigate(
                    cmd, btn_name
                ),
            )
            button.configure(**self.style_inactive)
            
            button.grid(row=row, column=0, padx=20, pady=12, sticky="ew")
            self.nav_buttons[name] = button

        # --- Botão de Sair ---
        self.logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Sair",
            image=self.icons["logout"],
            compound="left",
            anchor="w",
            command=self.logout,
            fg_color="#C43E3E",
            hover_color="#A03030",
            font=(fonts.BUTTON_FONT)
        )
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
            button.configure(
                **(
                    self.style_active
                    if name == active_button_name
                    else self.style_inactive
                )
            )

    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_content(self, ViewClass, *args, **kwargs):
        self._clear_content_frame()
        view = ViewClass(self.content_frame, *args, **kwargs)
        view.grid(row=0, column=0, sticky="nsew")

    def show_home_view(self):
        self._show_content(
            HomeView,
            gerar_escala_callback=self.show_escala_wizard,
            gerenciar_colaboradores_callback=self.show_colaboradores_view,
        )

    def show_escala_wizard(self):
        self._show_content(
            GeradorEscalaView,
            app_controller=self.app_controller,
        )

    def show_colaboradores_view(self, invalid_rows=None):
        self._show_content(
            GerenciarColaboradoresView,
            app_controller=self.app_controller,
            data_to_load=invalid_rows,
        )

    # --- FUNÇÃO CORRIGIDA ---
    def show_cadastro_manual_view(self, matricula_para_editar=None):
        """Mostra a tela de cadastro manual, passando a matrícula se estiver em modo de edição."""
        self._show_content(
            CadastroManualView,
            save_callback=self.app_controller.on_save_colaborador,
            back_callback=self.show_colaboradores_view,
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

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded

        if self.sidebar_expanded:
            self.sidebar_frame.configure(width=250)
            self.hamburger_button.configure(image=self.icons["menu"])
            self.profile_name.configure(text=self.username)

            # --- CORREÇÃO: Acessar botões pelo dicionário ---
            self.nav_buttons["home"].configure(text="Início", anchor="w")
            self.nav_buttons["escala"].configure(text="Gerar Escala", anchor="w")
            self.nav_buttons["colaboradores"].configure(
                text="Colaboradores", anchor="w"
            )

            self.logout_button.configure(text="Sair", anchor="w")
        else:
            self.sidebar_frame.configure(width=70)
            self.hamburger_button.configure(image=self.icons["close"])
            self.profile_name.configure(text="")

            # --- CORREÇÃO: Acessar botões pelo dicionário ---
            self.nav_buttons["home"].configure(text="", anchor="center")
            self.nav_buttons["escala"].configure(text="", anchor="center")
            self.nav_buttons["colaboradores"].configure(text="", anchor="center")

            self.logout_button.configure(text="", anchor="center")
