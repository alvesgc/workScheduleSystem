import customtkinter as ctk
import tkfontawesome as fa
from ... import database as db
from ... import fonts


class HomeView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller

        stats = db.get_dashboard_stats()
        upcoming_leaves = db.get_upcoming_leaves()

        # === PALETA DE CORES HIERÁRQUICA ===
        # Cores primárias (ações principais)
        PRIMARY = "#0078D7"
        PRIMARY_HOVER = "#005EA6"
        PRIMARY_LIGHT = "#E8F4FD"

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

        # Botões secundários
        BUTTON_SECONDARY = "#FFFFFF"
        BUTTON_SECONDARY_HOVER = "#F5F5F5"
        BUTTON_SECONDARY_BORDER = "#D1D5DB"

        # === ÍCONES ===
        icon_size_cards = 28
        icon_size_buttons = 18

        self.icon_users = fa.icon_to_image(
            "users", fill=PRIMARY, scale_to_height=icon_size_cards
        )
        self.icon_sitemap = fa.icon_to_image(
            "sitemap", fill=PRIMARY, scale_to_height=icon_size_cards
        )
        self.icon_calendar = fa.icon_to_image(
            "calendar-plus", fill="#FFFFFF", scale_to_height=icon_size_buttons
        )
        self.icon_user_cog = fa.icon_to_image(
            "user-cog", fill=TEXT_PRIMARY, scale_to_height=icon_size_buttons
        )

        # === CONFIGURAÇÃO DO GRID PRINCIPAL ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=0)  # stats
        self.grid_rowconfigure(2, weight=1)  # leaves panel
        self.grid_rowconfigure(3, weight=0)  # actions

        # === CONTAINER PRINCIPAL (para padding consistente) ===
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_rowconfigure(3, weight=0)

        # === CABEÇALHO ===
        header_frame = ctk.CTkFrame(
            main_container,
            fg_color="transparent",
            corner_radius=0,
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 24))

        ctk.CTkLabel(
            header_frame,
            text="Bem-vindo ao Gerador de Escalas",
            font=fonts.TITULO_SECAO,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            header_frame,
            text="Painel de controle com informações importantes do sistema.",
            font=fonts.SUBTITULO,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w")

        # === CARDS DE ESTATÍSTICAS ===
        stats_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 24))
        stats_frame.grid_columnconfigure((0, 1), weight=1, uniform="stats")

        stats_data = [
            (
                self.icon_users,
                stats.get("total_colaboradores", 0),
                "Colaboradores Ativos",
            ),
            (self.icon_sitemap, stats.get("total_setores", 0), "Setores Gerenciados"),
        ]

        for i, (icon, value, label) in enumerate(stats_data):
            card = ctk.CTkFrame(
                stats_frame,
                fg_color=SURFACE,
                border_color=BORDER,
                border_width=1,
                corner_radius=12,
            )
            card.grid(
                row=0, column=i, padx=(0, 16) if i == 0 else (0, 0), sticky="nsew"
            )
            card.grid_columnconfigure(0, weight=0)
            card.grid_columnconfigure(1, weight=1)

            # Ícone
            ctk.CTkLabel(card, text="", image=icon).grid(
                row=0, column=0, rowspan=2, padx=(20, 16), pady=24
            )

            # Valor
            ctk.CTkLabel(
                card, text=str(value), font=fonts.TITULO_CARD, text_color=TEXT_PRIMARY
            ).grid(row=0, column=1, sticky="sw", padx=(0, 20), pady=(24, 0))

            # Label
            ctk.CTkLabel(
                card, text=label, font=fonts.SUBTITULO, text_color=TEXT_SECONDARY
            ).grid(row=1, column=1, sticky="nw", padx=(0, 20), pady=(4, 24))

        # === PAINEL DE AFASTAMENTOS ===
        leaves_panel = ctk.CTkFrame(
            main_container,
            fg_color=SURFACE,
            border_color=BORDER,
            border_width=1,
            corner_radius=12,
        )
        leaves_panel.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        leaves_panel.grid_rowconfigure(1, weight=1)
        leaves_panel.grid_columnconfigure(0, weight=1)

        # Cabeçalho do painel
        header_leaves = ctk.CTkFrame(leaves_panel, fg_color="transparent")
        header_leaves.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header_leaves,
            text="Próximos Afastamentos",
            font=fonts.LABEL_FONT,
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            header_leaves,
            text="(30 dias)",
            font=fonts.SUBTITULO,
            text_color=TEXT_TERTIARY,
        ).pack(side="left", padx=(8, 0))

        # Lista de afastamentos
        scrollable_leaves = ctk.CTkScrollableFrame(
            leaves_panel, fg_color="transparent", corner_radius=0
        )
        scrollable_leaves.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        if upcoming_leaves:
            for idx, leave in enumerate(upcoming_leaves):
                # Frame para cada item
                item_frame = ctk.CTkFrame(
                    scrollable_leaves,
                    fg_color=SURFACE_SECONDARY if idx % 2 == 0 else "transparent",
                    corner_radius=6,
                )
                item_frame.pack(fill="x", padx=8, pady=4)

                inicio_str = leave["afastamento_inicio"].strftime("%d/%m/%Y")
                fim_str = (
                    leave["afastamento_fim"].strftime("%d/%m/%Y")
                    if leave.get("afastamento_fim")
                    else "Indefinido"
                )

                # Nome do colaborador
                ctk.CTkLabel(
                    item_frame,
                    text=leave["nome"],
                    font=fonts.TEXTO_NORMAL,
                    text_color=TEXT_PRIMARY,
                ).pack(side="left", padx=(12, 8), pady=12)

                # Período
                ctk.CTkLabel(
                    item_frame,
                    text=f"{inicio_str} até {fim_str}",
                    font=fonts.SUBTITULO,
                    text_color=TEXT_SECONDARY,
                ).pack(side="left", padx=(0, 12))
        else:
            empty_frame = ctk.CTkFrame(scrollable_leaves, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=40)

            ctk.CTkLabel(
                empty_frame,
                text="Nenhum afastamento programado nos próximos 30 dias",
                font=fonts.SUBTITULO,
                text_color=TEXT_TERTIARY,
            ).pack(expand=True)

        # === BOTÕES DE AÇÃO ===
        action_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        action_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 16))
        action_frame.grid_columnconfigure((0, 1), weight=1, uniform="actions")

        # Botão principal
        ctk.CTkButton(
            action_frame,
            text="Gerar Nova Escala",
            image=self.icon_calendar,
            command=app_controller.show_escala_wizard,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color="white",
            corner_radius=8,
            compound="left",
            border_spacing=10,
        ).grid(row=0, column=0, padx=(0, 12), sticky="ew")

        # Botão secundário
        ctk.CTkButton(
            action_frame,
            text="Gerenciar Colaboradores",
            image=self.icon_user_cog,
            command=app_controller.show_colaboradores_view,
            height=44,
            font=fonts.BUTTON_FONT,
            fg_color=BUTTON_SECONDARY,
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            corner_radius=8,
            compound="left",
            border_spacing=10,
        ).grid(row=0, column=1, padx=(0, 0), sticky="ew")
