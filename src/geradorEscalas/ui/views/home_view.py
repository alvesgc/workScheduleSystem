import customtkinter as ctk
from ... import database as db # Importa o módulo de banco de dados

class HomeView(ctk.CTkFrame):
    def __init__(self, master, gerar_escala_callback, gerenciar_colaboradores_callback):
        super().__init__(master, fg_color="transparent")

        # --- Carrega os dados do Dashboard ---
        stats = db.get_dashboard_stats()
        upcoming_leaves = db.get_upcoming_leaves()

        # --- Layout do Grid ---
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1) # Linha dos painéis de info expande

        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(header_frame, text="Bem-vindo ao Gerador de Escalas", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Este é o seu painel de controle com informações importantes do sistema.", font=ctk.CTkFont(size=16)).pack(anchor="w")
        
        # --- Cards de Estatísticas ---
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Colaboradores Ativos
        card1 = ctk.CTkFrame(stats_frame, border_width=1)
        card1.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(card1, text=stats.get('total_colaboradores', 0), font=ctk.CTkFont(size=40, weight="bold")).pack(pady=(10, 0))
        ctk.CTkLabel(card1, text="Colaboradores Ativos").pack(pady=(0, 10))

        # Card 2: Setores Gerenciados
        card2 = ctk.CTkFrame(stats_frame, border_width=1)
        card2.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        ctk.CTkLabel(card2, text=stats.get('total_setores', 0), font=ctk.CTkFont(size=40, weight="bold")).pack(pady=(10, 0))
        ctk.CTkLabel(card2, text="Setores Gerenciados").pack(pady=(0, 10))

        # --- Painéis de Informação ---
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)

        # Painel da Esquerda: Próximos Afastamentos
        leaves_panel = ctk.CTkFrame(info_frame)
        leaves_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(leaves_panel, text="Próximos Afastamentos (30 dias)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=10, anchor="w")
        
        scrollable_leaves = ctk.CTkScrollableFrame(leaves_panel, fg_color="transparent")
        scrollable_leaves.pack(fill="both", expand=True, padx=5)

        if upcoming_leaves:
            for leave in upcoming_leaves:
                ctk.CTkLabel(scrollable_leaves, text=f"• {leave['nome']} - Início: {leave['data_inicio']}").pack(anchor="w", padx=10)
        else:
            ctk.CTkLabel(scrollable_leaves, text="Nenhum afastamento programado.").pack(padx=10)

        # --- Botões de Ação ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            action_frame, text="Gerar Nova Escala",
            command=gerar_escala_callback,
            height=50, font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        ctk.CTkButton(
            action_frame, text="Gerenciar Colaboradores",
            command=gerenciar_colaboradores_callback,
            height=50, font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")