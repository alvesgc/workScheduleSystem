import customtkinter as ctk
import tkfontawesome as fa
from ... import database as db
from ... import fonts


class HomeView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master)
        self.app_controller = app_controller

        # --- Carrega os dados do Dashboard ---
        stats = db.get_dashboard_stats()
        upcoming_leaves = db.get_upcoming_leaves()

        # --- Lógica de Cores Dinâmicas ---
        text_color_tuple = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        appearance_mode = ctk.get_appearance_mode()
        icon_color = (
            text_color_tuple[0] if appearance_mode == "Light" else text_color_tuple[1]
        )

        # --- Ícones para o Dashboard ---
        icon_size_cards = 32
        icon_size_buttons = 20
        self.icon_users = fa.icon_to_image(
            "users", fill=icon_color, scale_to_height=icon_size_cards
        )
        self.icon_sitemap = fa.icon_to_image(
            "sitemap", fill=icon_color, scale_to_height=icon_size_cards
        )
        self.icon_calendar = fa.icon_to_image(
            "calendar-plus", fill=icon_color, scale_to_height=icon_size_buttons
        )
        self.icon_user_cog = fa.icon_to_image(
            "user-cog", fill=icon_color, scale_to_height=icon_size_buttons
        )

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew", padx=10)
        ctk.CTkLabel(
            header_frame,
            text="Bem-vindo ao Gerador de Escalas",
            font=fonts.TITULO_SECAO,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Painel de controle com informações importantes do sistema.",
            font=fonts.SUBTITULO,
            text_color="gray60",
        ).pack(anchor="w")

        # --- Frame para os Cards de Estatísticas ---
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, pady=10, sticky="ew", padx=10)
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Colaboradores Ativos
        card1 = ctk.CTkFrame(stats_frame, border_width=1, border_color="gray30")
        card1.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        card1.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card1, text="", image=self.icon_users).grid(
            row=0, column=0, rowspan=2, padx=20, pady=20
        )
        ctk.CTkLabel(
            card1, text=stats.get("total_colaboradores", 0), font=fonts.TITULO_CARD
        ).grid(row=0, column=1, sticky="sw", padx=(0, 20))
        ctk.CTkLabel(card1, text="Colaboradores Ativos", text_color="gray60").grid(
            row=1, column=1, sticky="nw", padx=(0, 20)
        )

        # Card 2: Setores Gerenciados
        card2 = ctk.CTkFrame(stats_frame, border_width=1, border_color="gray30")
        card2.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        card2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card2, text="", image=self.icon_sitemap).grid(
            row=0, column=0, rowspan=2, padx=20, pady=20
        )
        ctk.CTkLabel(
            card2, text=stats.get("total_setores", 0), font=fonts.TITULO_CARD
        ).grid(row=0, column=1, sticky="sw", padx=(0, 20))
        ctk.CTkLabel(card2, text="Setores Gerenciados", text_color="gray60").grid(
            row=1, column=1, sticky="nw", padx=(0, 20)
        )

        # --- Painel de Próximos Afastamentos ---
        leaves_panel = ctk.CTkFrame(self, border_width=1, border_color="gray30")
        leaves_panel.grid(
            row=2, column=0, columnspan=2, pady=20, sticky="nsew", padx=10
        )
        leaves_panel.grid_rowconfigure(1, weight=1)
        leaves_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            leaves_panel, text="Próximos Afastamentos (30 dias)", font=fonts.LABEL_FONT
        ).grid(row=0, column=0, pady=10, padx=20, sticky="w")

        scrollable_leaves = ctk.CTkScrollableFrame(leaves_panel, fg_color="transparent")
        # --- CORREÇÃO APLICADA AQUI ---
        # Substituído 'fill="both"' e 'expand=True' por 'sticky="nsew"'
        scrollable_leaves.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        if upcoming_leaves:
            for leave in upcoming_leaves:
                inicio_str = leave["afastamento_inicio"].strftime("%d/%m/%Y")
                fim_str = (
                    leave["afastamento_fim"].strftime("%d/%m/%Y")
                    if leave.get("afastamento_fim")
                    else "Indefinido"
                )
                texto = f"• {leave['nome']} (de {inicio_str} a {fim_str})"
                ctk.CTkLabel(
                    scrollable_leaves, text=texto, font=fonts.TEXTO_NORMAL
                ).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(
                scrollable_leaves,
                text="Nenhum afastamento programado.",
                text_color="gray60",
            ).pack(expand=True)

        # --- Botões de Ação ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(
            row=3, column=0, columnspan=2, pady=(0, 10), sticky="ew", padx=10
        )
        action_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            action_frame,
            text="Gerar Nova Escala",
            image=self.icon_calendar,
            command=app_controller.show_escala_wizard,
            height=50,
            font=fonts.BUTTON_FONT,
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            action_frame,
            text="Gerenciar Colaboradores",
            image=self.icon_user_cog,
            command=app_controller.show_colaboradores_view,
            height=50,
            font=fonts.BUTTON_FONT,
            fg_color="#4A4A4A",
            hover_color="#3A3A3A",
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")
