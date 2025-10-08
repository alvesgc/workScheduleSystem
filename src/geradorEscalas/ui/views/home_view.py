import customtkinter as ctk
from ... import database as db
from ... import fonts
import tkfontawesome as fa


class HomeView(ctk.CTkFrame):
    def __init__(self, master, gerar_escala_callback, gerenciar_colaboradores_callback):
        super().__init__(master, fg_color="transparent")

        # --- Carrega os dados do Dashboard ---
        stats = db.get_dashboard_stats()
        upcoming_leaves = db.get_upcoming_leaves()

        # --- Layout do Grid ---
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)  # Linha dos painéis de info expande

        # --- Ícones para o Dashboard ---
        icon_color = "#DCE4EE"
        icon_size = 32
        self.icon_users = fa.icon_to_image(
            "users", fill=icon_color, scale_to_height=icon_size
        )
        self.icon_sitemap = fa.icon_to_image(
            "sitemap", fill=icon_color, scale_to_height=icon_size
        )
        self.icon_calendar = fa.icon_to_image(
            "calendar-plus", fill=icon_color, scale_to_height=20
        )
        self.icon_user_cog = fa.icon_to_image(
            "user-cog", fill=icon_color, scale_to_height=20
        )

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(
            header_frame,
            text="Bem-vindo ao Gerador de Escalas",
            font=fonts.TITULO_SECAO,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame,
            text="Este é o seu painel de controle com informações importantes do sistema.",
            font=fonts.SUBTITULO,
        ).pack(anchor="w")

        # --- Cards de Estatísticas ---
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Colaboradores Ativos
        card1 = ctk.CTkFrame(stats_frame)
        card1.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        card1.grid_columnconfigure(1, weight=1)  # Faz a coluna do texto expandir
        ctk.CTkLabel(card1, text="", image=self.icon_users).grid(
            row=0, column=0, rowspan=2, padx=20, pady=20
        )
        ctk.CTkLabel(
            card1, text=stats.get("total_colaboradores", 0), font=fonts.TITULO_CARD
        ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(card1, text="Colaboradores Ativos", text_color="gray60").grid(
            row=1, column=1, sticky="nw"
        )

        # Card 2: Setores Gerenciados
        card2 = ctk.CTkFrame(stats_frame)
        card2.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        card2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card2, text="", image=self.icon_sitemap).grid(
            row=0, column=0, rowspan=2, padx=20, pady=20
        )
        ctk.CTkLabel(
            card2, text=stats.get("total_setores", 0), font=fonts.TITULO_CARD
        ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(card2, text="Setores Gerenciados", text_color="gray60").grid(
            row=1, column=1, sticky="nw"
        )

        # --- Painéis de Informação ---
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)

        # Painel da Esquerda: Próximos Afastamentos
        leaves_panel = ctk.CTkFrame(self)  # Fundo sólido para melhor agrupamento visual
        leaves_panel.grid(row=2, column=0, columnspan=2, pady=20, sticky="nsew")
        ctk.CTkLabel(
            leaves_panel, text="Próximos Afastamentos (30 dias)", font=fonts.LABEL_FONT
        ).pack(pady=10, padx=20, anchor="w")

        scrollable_leaves = ctk.CTkScrollableFrame(leaves_panel, fg_color="transparent")
        scrollable_leaves.pack(fill="both", expand=True, padx=5)

        if upcoming_leaves:
            for leave in upcoming_leaves:
                ctk.CTkLabel(
                    scrollable_leaves,
                    text=f"• {leave['nome']} - Início: {leave['data_inicio']}",
                    font=fonts.TEXTO_NORMAL,
                ).pack(anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(
                scrollable_leaves,
                text="Nenhum afastamento programado.",
                text_color="gray60",
            ).pack(expand=True)

        # --- Botões de Ação ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            action_frame,
            text="Gerar Nova Escala",
            command=gerar_escala_callback,
            height=50,
            font=fonts.BUTTON_FONT,
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            action_frame,
            text="Gerenciar Colaboradores",
            command=gerenciar_colaboradores_callback,
            height=50,
            font=fonts.BUTTON_FONT,
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")
