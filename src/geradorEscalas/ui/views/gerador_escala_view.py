from calendar import monthrange, weekday
import os
import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from datetime import date, datetime
import tkfontawesome as fa
from ..widgets import ctk_checklist_dropdown as checklist
from .setup_escala_view import SetupEscalaView
from ... import exporters
from ... import fonts
from ...escala_engine import GeradorEscalaEngine
from ... import database as db
from .setup_escala_view import SetupEscalaView
from ..widgets.CTkAdvancedTable import CTkAdvancedTable

ChecklistDropdown = checklist.ChecklistDropdown


class GeradorEscalaView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller
        self.ultima_escala_gerada = None
        self.selected_matriculas = set()
        # === PALETA DE CORES HIERÁRQUICA ===
        PRIMARY = "#0078D7"
        PRIMARY_HOVER = "#005EA6"

        SURFACE = "#FFFFFF"
        SURFACE_SECONDARY = "#FAFAFA"
        BACKGROUND = "#F5F6FA"

        BORDER = "#E1E4E8"
        BORDER_LIGHT = "#F0F0F0"

        TEXT_PRIMARY = "#1E1E1E"
        TEXT_SECONDARY = "#6B6B6B"
        TEXT_TERTIARY = "#9CA3AF"

        BUTTON_SECONDARY = "#FFFFFF"
        BUTTON_SECONDARY_HOVER = "#F5F5F5"
        BUTTON_SECONDARY_BORDER = "#D1D5DB"

        SUCCESS = "#10B981"
        SUCCESS_HOVER = "#059669"

        try:
            icon_path = "src/geradorEscalas/assets/icons"
            pil_checked = Image.open(
                os.path.join(icon_path, "checkbox_checked.png")  # [cite: 4]
            ).resize((16, 16), Image.Resampling.LANCZOS)
            pil_unchecked = Image.open(
                os.path.join(icon_path, "checkbox_unchecked.png")
            ).resize((16, 16), Image.Resampling.LANCZOS)
            self.img_checked = ImageTk.PhotoImage(pil_checked)
            self.img_unchecked = ImageTk.PhotoImage(pil_unchecked)
        except Exception as e:
            print(
                f"ERRO: Não foi possível carregar as imagens de checkbox: {e}"
            )  # [cite: 5]
            self.img_checked = self.img_unchecked = None

        # --- Carrega os dados para os filtros ---
        self.escala_filter_vars = {
            escala: ctk.StringVar(value="on")
            for escala in db.get_distinct_escala_types()
        }
        all_collaborators = db.get_all_active_collaborators()
        self.colab_filter_vars = {
            colab["matricula"]: ctk.StringVar(value="on") for colab in all_collaborators
        }
        self.colab_matricula_to_name = {
            colab["matricula"]: colab["nome"] for colab in all_collaborators
        }
        self.setor_filter_vars = {
            setor: ctk.StringVar(value="on") for setor in db.get_distinct_setores()
        }

        # === ÍCONES ===
        icon_size = 16
        self.icons = {
            "filter": fa.icon_to_image(
                "filter", fill=TEXT_SECONDARY, scale_to_height=icon_size
            ),
            "users": fa.icon_to_image(
                "users", fill=TEXT_SECONDARY, scale_to_height=icon_size
            ),
            "generate": fa.icon_to_image(
                "cogs", fill="#FFFFFF", scale_to_height=icon_size
            ),
            "edit": fa.icon_to_image("edit", fill="#FFFFFF", scale_to_height=icon_size),
            "excel": fa.icon_to_image(
                "file-excel", fill="#FFFFFF", scale_to_height=icon_size
            ),
            "pdf": fa.icon_to_image(
                "file-pdf", fill="#FFFFFF", scale_to_height=icon_size
            ),
            "help": fa.icon_to_image(
                "question-circle", fill=TEXT_SECONDARY, scale_to_height=icon_size
            ),
        }

        # === LAYOUT PRINCIPAL ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # === CABEÇALHO ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))

        # Título principal (continua igual)
        ctk.CTkLabel(
            header_frame,
            text="Gerar Escala",
            font=fonts.TITULO_SECAO,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 4))

        # Frame para conter a descrição E o botão de ajuda
        desc_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        desc_frame.pack(anchor="w", fill="x")
        # Configura a coluna 0 (onde ficará o texto) para expandir
        desc_frame.grid_columnconfigure(0, weight=1)

        # Label da Descrição (agora dentro do desc_frame e usando grid)
        ctk.CTkLabel(
            desc_frame,  # <-- Master corrigido
            text="Configure o período e filtros para gerar a escala de trabalho.",
            font=fonts.SUBTITULO,
            text_color=TEXT_SECONDARY,
        ).grid(
            row=0, column=0, sticky="w"
        )  # <-- Usa grid na coluna 0

        # Botão de Ajuda (dentro do desc_frame e usando grid)
        ctk.CTkButton(
            desc_frame,  # <-- Master correto
            text="",
            image=self.icons.get("help"),
            compound="left",
            command=self._mostrar_legenda,
            fg_color="transparent",
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=TEXT_SECONDARY,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            height=28,
            width=28,
            corner_radius=6,
        ).grid(
            row=0, column=1, sticky="w", padx=(10, 0)
        )  # <-- Usa grid na coluna 1

        # === PAINEL DE CONTROLES ===
        controls_container = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            border_color=BORDER,
            border_width=1,
            corner_radius=12,
        )
        controls_container.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="ew")

        # Frame único com todos os controles
        controls_frame = ctk.CTkFrame(controls_container, fg_color="transparent")
        controls_frame.pack(fill="x", padx=16, pady=14)
        controls_frame.grid_columnconfigure(5, weight=1)

        # Período (Mês e Ano)
        meses_nomes = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
        self.meses_map = {nome: i + 1 for i, nome in enumerate(meses_nomes)}
        self.mes_var = ctk.StringVar(value=meses_nomes[datetime.now().month - 1])

        ctk.CTkLabel(
            controls_frame, text="Mês:", font=fonts.SUBTITULO, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=(0, 6), sticky="w")

        # Frame wrapper para simular borda no dropdown
        mes_wrapper = ctk.CTkFrame(
            controls_frame,
            fg_color="transparent",
            border_color=BUTTON_SECONDARY_BORDER,
            border_width=1,
            corner_radius=8,
        )
        mes_wrapper.grid(row=0, column=1, padx=(0, 12))

        ctk.CTkOptionMenu(
            mes_wrapper,
            variable=self.mes_var,
            values=meses_nomes,
            width=108,
            fg_color=BUTTON_SECONDARY,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            font=fonts.SUBTITULO,
            dropdown_fg_color=SURFACE,
            dropdown_hover_color=SURFACE_SECONDARY,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=7,
        ).pack(padx=1, pady=1)

        ctk.CTkLabel(
            controls_frame, text="Ano:", font=fonts.SUBTITULO, text_color=TEXT_PRIMARY
        ).grid(row=0, column=2, padx=(0, 6), sticky="w")

        self.ano_var = ctk.StringVar(value=str(datetime.now().year))
        ctk.CTkEntry(
            controls_frame,
            textvariable=self.ano_var,
            width=70,
            fg_color=BUTTON_SECONDARY,
            border_color=BUTTON_SECONDARY_BORDER,
            text_color=TEXT_PRIMARY,
            font=fonts.SUBTITULO,
            corner_radius=8,
        ).grid(row=0, column=3, padx=(0, 24))

        # Botões de Filtro
        self.escala_filter_button = ctk.CTkButton(
            controls_frame,
            text="Escalas (0/0)",
            font=fonts.SUBTITULO,
            image=self.icons.get("filter"),
            compound="left",
            command=self._open_escala_filter,
            fg_color=BUTTON_SECONDARY,
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            height=34,
            corner_radius=8,
        )
        self.escala_filter_button.grid(row=0, column=4, padx=(0, 6))

        self.setor_filter_button = ctk.CTkButton(
            controls_frame,
            text="Setores (0/0)",
            font=fonts.SUBTITULO,
            image=self.icons.get("filter"),
            compound="left",
            command=self._open_setor_filter,
            fg_color=BUTTON_SECONDARY,
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            height=34,
            corner_radius=8,
        )
        self.setor_filter_button.grid(row=0, column=5, padx=(0, 6))

        self.colab_filter_button = ctk.CTkButton(
            controls_frame,
            text="Colaboradores (0/0)",
            font=fonts.SUBTITULO,
            image=self.icons.get("users"),
            compound="left",
            command=self._open_colab_filter,
            fg_color=BUTTON_SECONDARY,
            hover_color=BUTTON_SECONDARY_HOVER,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BUTTON_SECONDARY_BORDER,
            height=34,
            corner_radius=8,
        )
        self.colab_filter_button.grid(row=0, column=6, padx=(0, 24))

        # Botão Gerar Prévia
        self.generate_button = ctk.CTkButton(
            controls_frame,
            text="Gerar Prévia",
            image=self.icons.get("generate"),
            compound="left",
            font=fonts.SUBTITULO,
            command=self._gerar_previa,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            height=34,
            corner_radius=8,
        )
        self.generate_button.grid(row=0, column=7, sticky="e")

        # === FRAME DE AÇÕES ===
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="e")

        self.modificar_button = ctk.CTkButton(
            actions_frame,
            text="Modificar Escala",
            font=fonts.BUTTON_FONT,
            image=self.icons.get("edit"),
            compound="left",
            state="disabled",
            command=self._modificar_escala_selecionados,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            height=36,
            corner_radius=8,
        )
        self.modificar_button.pack(side="left", padx=(0, 8))

        self.excel_button = ctk.CTkButton(
            actions_frame,
            text="Exportar Excel",
            font=fonts.BUTTON_FONT,
            image=self.icons.get("excel"),
            compound="left",
            state="disabled",
            command=self._exportar_para_excel,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            height=36,
            corner_radius=8,
        )
        self.excel_button.pack(side="left", padx=(0, 8))

        self.pdf_button = ctk.CTkButton(
            actions_frame,
            text="Exportar PDF",
            font=fonts.BUTTON_FONT,
            image=self.icons.get("pdf"),
            compound="left",
            state="disabled",
            command=self._exportar_para_pdf,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            height=36,
            corner_radius=8,
        )
        self.pdf_button.pack(side="left")

        # === CONTAINER DA TABELA ===
        table_container = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            corner_radius=12,
        )
        table_container.grid(row=3, column=0, padx=24, pady=(0, 24), sticky="nsew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        self.preview_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            self.preview_frame,
            text="Selecione o mês e ano e clique em 'Gerar Prévia' para começar.",
            font=fonts.SUBTITULO,
            text_color=TEXT_TERTIARY,
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self._update_escala_filter_button_text()
        self._update_colab_filter_button_text()
        self._update_setor_filter_button_text()

    def _setup_treeview(self):
        """Cria a tabela usando o componente CTkAdvancedTable."""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        colunas = ["Colaborador"] + [str(i) for i in range(1, 32)]

        # Cria a tabela com tema claro (padrão)
        self.tree = CTkAdvancedTable(
            self.preview_frame, columns=colunas, show_checkbox_column=True
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Button-1>", self.on_row_click)
        self.tree.configure(selectmode="extended")
        # Força a atualização do widget antes de configurar as colunas
        self.tree.update_idletasks()

        # Configuração das colunas
        self.tree.heading("Colaborador", text="Colaborador", anchor="w")
        self.tree.column(
            "Colaborador", width=350, minwidth=250, anchor="w", stretch=ctk.NO
        )

        for i in range(1, 32):
            self.tree.heading(str(i), text=str(i), anchor="center")
            # Colunas dinâmicas com largura suficiente para números de 2 dígitos
            self.tree.column(
                str(i), width=50, minwidth=50, anchor="center", stretch=ctk.YES
            )

        # Força outra atualização após configurar os headings
        self.tree.update_idletasks()

        # Scrollbars
        vsb = ctk.CTkScrollbar(self.preview_frame, command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ctk.CTkScrollbar(
            self.preview_frame, orientation="horizontal", command=self.tree.xview
        )
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    def _gerar_previa(self):
        unconfigured = db.get_unconfigured_collaborators()

        if unconfigured:
            # Formata a lista para a tela de setup (garante o campo data_base_atual)
            colabs_para_setup = [
                {
                    "matricula": c.get("matricula"),
                    "nome": c.get("nome"),
                    "data_base_atual": "",  # Vazio, para o SetupView usar today_str
                }
                for c in unconfigured
            ]

            messagebox.showinfo(
                "Configuração Pendente",
                f"Existem {len(colabs_para_setup)} colaborador(es) sem uma data de início de escala. "
                "Por favor, configure-os agora.",
                parent=self,
            )

            popup = SetupEscalaView(
                self,
                colaboradores=colabs_para_setup,
                save_callback=self._on_setup_save,
                title="Configuração Inicial de Escala",  # <-- ADICIONADO
                mode="initial",  # <-- ADICIONADO
            )
            self.wait_window(popup)
        else:
            self._executar_geracao()  # Chama a geração normal

    def _on_setup_save(self, updates):
        success, message = db.update_collaborator_base_dates(updates)
        if success:
            self._executar_geracao()
        else:
            messagebox.showerror("Erro ao Salvar", message)

    def _open_escala_filter(self):
        items_for_dropdown = {
            escala: var for escala, var in self.escala_filter_vars.items()
        }
        ChecklistDropdown(
            self.escala_filter_button,
            items_for_dropdown,
            self._update_escala_filter_button_text,
        )

    def _open_colab_filter(self):
        items_for_dropdown = {
            self.colab_matricula_to_name[mat]: var
            for mat, var in self.colab_filter_vars.items()
        }
        ChecklistDropdown(
            self.colab_filter_button,
            items_for_dropdown,
            self._update_colab_filter_button_text,
        )

    def _open_setor_filter(self):
        items_for_dropdown = {
            setor: var for setor, var in self.setor_filter_vars.items()
        }
        ChecklistDropdown(
            self.setor_filter_button,
            items_for_dropdown,
            self._update_setor_filter_button_text,
        )

    def _update_setor_filter_button_text(self):
        total = len(self.setor_filter_vars)
        selecionados = sum(
            1 for var in self.setor_filter_vars.values() if var.get() == "on"
        )
        self.setor_filter_button.configure(text=f"Setores ({selecionados}/{total})")

    def _update_escala_filter_button_text(self):
        total = len(self.escala_filter_vars)
        selecionados = sum(
            1 for var in self.escala_filter_vars.values() if var.get() == "on"
        )
        self.escala_filter_button.configure(text=f"Escalas ({selecionados}/{total})")

    def _update_colab_filter_button_text(self):
        total = len(self.colab_filter_vars)
        selecionados = sum(
            1 for var in self.colab_filter_vars.values() if var.get() == "on"
        )
        self.colab_filter_button.configure(
            text=f"Colaboradores ({selecionados}/{total})"
        )

    def _executar_geracao(self):
        """Coleta os filtros, busca os dados, chama o motor de geração e preenche a tabela."""
        self.selected_matriculas.clear()
        self._setup_treeview()
        loading_label = ctk.CTkLabel(
            self.tree,
            text="Gerando escala, por favor aguarde...",
            font=fonts.SUBTITULO,
            text_color="#6B6B6B",
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.generate_button.configure(state="disabled")
        self.update_context_buttons()
        self.excel_button.configure(state="disabled")
        self.pdf_button.configure(state="disabled")
        self.update_idletasks()

        try:
            filtros = {"escala_types": [], "matriculas": [], "setores": []}

            for escala, var in self.escala_filter_vars.items():
                if var.get() == "on":
                    filtros["escala_types"].append(escala)

            for matricula, var in self.colab_filter_vars.items():
                if var.get() == "on":
                    filtros["matriculas"].append(matricula)

            for setor, var in self.setor_filter_vars.items():
                if var.get() == "on":
                    filtros["setores"].append(setor)

            colaboradores_para_gerar = db.get_all_active_collaborators(filtros=filtros)

            if not colaboradores_para_gerar:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum colaborador corresponde aos filtros selecionados.",
                    parent=self,
                )
                return

            mes_numero = self.meses_map[self.mes_var.get()]
            ano = int(self.ano_var.get())

            self._marcar_dias_especiais(ano, mes_numero)

            self.engine = GeradorEscalaEngine(ano, mes_numero)
            dados_escala = self.engine.executar(colaboradores_para_gerar)

            self.ultima_escala_gerada = dados_escala
            self.colaboradores_carregados = self.engine.colaboradores
            self._preencher_tabela(dados_escala)

            # self.modificar_button.configure(state="normal")
            self.excel_button.configure(state="normal")
            self.pdf_button.configure(state="normal")

        except Exception as e:
            messagebox.showerror(
                "Erro na Geração", f"Ocorreu um erro ao gerar a escala: {e}"
            )

        finally:
            if loading_label.winfo_exists():
                loading_label.destroy()
            self.generate_button.configure(state="normal")

    def _marcar_dias_especiais(self, ano, mes):
        """Adiciona marcadores visuais nos cabeçalhos de dias especiais."""
        today = datetime.now()
        num_dias = monthrange(ano, mes)[1]
        for dia in range(1, 32):
            self.tree.heading(str(dia), text=str(dia))
            if dia <= num_dias:
                if weekday(ano, mes, dia) >= 5:
                    self.tree.heading(str(dia), text=f"•{dia}•")
                if ano == today.year and mes == today.month and dia == today.day:
                    self.tree.heading(str(dia), text=f"[{dia}]")

    def _mostrar_legenda(self):
        # Define as cores
        PRIMARY = "#0078D7"
        SURFACE = "#FFFFFF"
        BORDER = "#E1E4E8"
        TEXT_PRIMARY = "#1E1E1E"
        TEXT_SECONDARY = "#6B6B6B"
        SUCCESS = "#10B981"
        DANGER = "#DC2626"
        WARNING = "#F97316"
        INFO = "#7C3AED"

        popup = ctk.CTkToplevel(self)
        popup.title("Legenda da Escala")
        popup.geometry("460x440")
        popup.transient(self)
        popup.grab_set()
        popup.resizable(False, False)

        # Centralizar
        popup.update_idletasks()
        w, h = 460, 440
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")

        # --- CORREÇÃO: Container principal modificado ---
        # O container agora ocupa quase toda a janela e inclui o título
        container = ctk.CTkFrame(
            popup, fg_color=SURFACE, border_color=BORDER,
            border_width=1, corner_radius=12
        )
        # Ajustado pady para começar mais perto do topo
        container.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        # --- FIM DA CORREÇÃO ---


        # --- CORREÇÃO: Título movido para DENTRO do container ---
        # Removido o 'header' frame
        ctk.CTkLabel(
            container, # Master agora é o container principal
            text="Legenda da Escala",
            font=fonts.TITULO_SECAO,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=15, pady=(10, 5)) # Adicionado padx e ajustado pady
        # --- FIM DA CORREÇÃO ---


        # Scroll Frame (agora dentro do container, abaixo do título)
        scroll_frame = ctk.CTkScrollableFrame(
            container, fg_color=SURFACE, corner_radius=12,
            border_width=0 # Remove borda interna se houver
        )
        # Ajustado pady para ficar mais próximo do título
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # --- DADOS DA LEGENDA ---
        categorias = [
            ("SÍMBOLOS BÁSICOS", [
                ("X", "Dia de Trabalho", SUCCESS),
                ("F", "Folga / Descanso", TEXT_SECONDARY),
            ]),
            ("AFASTAMENTOS", [
                ("AT", "Atestado Médico", DANGER),
                ("AF", "Afastado INSS", SUCCESS),
                ("FE", "Férias", WARNING),
                ("LM", "Licença Maternidade", INFO),
            ]),
            ("MARCADORES DE CABEÇALHO", [
                ("•Dia•", "Final de Semana", TEXT_SECONDARY),
                ("[Dia]", "Dia Atual", PRIMARY),
            ])
        ]

        # --- Lógica de Layout (com linha separadora) ---
        for titulo, itens in categorias:
            ctk.CTkLabel(
                scroll_frame, text=titulo, font=fonts.SUBTITULO,
                text_color=TEXT_PRIMARY,
            ).pack(anchor="w", pady=(15, 2), padx=5)

            ctk.CTkFrame(
                scroll_frame, height=1, fg_color=BORDER, corner_radius=0
            ).pack(fill="x", padx=5, pady=(0, 5))

            for sigla, desc, cor in itens:
                linha = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                linha.pack(fill="x", pady=2, padx=5)
                linha.grid_columnconfigure(0, weight=0)
                linha.grid_columnconfigure(1, weight=1)

                sigla_label = ctk.CTkLabel(
                    linha, text=sigla, width=60,
                    font=fonts.TEXTO_NORMAL if sigla not in ["•Dia•", "[Dia]"] else fonts.TEXTO_NORMAL,
                    text_color=cor, anchor="w"
                )
                sigla_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

                desc_label = ctk.CTkLabel(
                    linha, text=desc, font=fonts.TEXTO_NORMAL,
                    text_color=TEXT_SECONDARY, anchor="w", wraplength=300
                )
                desc_label.grid(row=0, column=1, sticky="w")
        # --- FIM DA LÓGICA ---

        # Botão Entendi
        ctk.CTkButton(
            popup, text="Entendi", fg_color=PRIMARY, hover_color="#005EA6",
            font=fonts.BUTTON_FONT, corner_radius=8, height=42,
            command=popup.destroy,
        ).pack(pady=(5, 15))

    def _preencher_tabela(self, dados_escala):
        """Preenche a tabela com 'X' para trabalho, 'F' para folga e abreviações para afastamentos."""

        # Dicionário de abreviações (mesmo do PDF)
        MOTIVO_ABBREV = {
            "ATESTADO": "AT",
            "AFASTADO INSS.": "AF",
            "FÉRIAS": "FE",
            "FERIAS": "FE",
            "LICENÇA MATERNIDADE": "LM",
            "LICENCA MATERNIDADE": "LM",
            "HORA EXTRA": "HE",
            "FOLGA": "F",
        }

        mes_numero = self.meses_map[self.mes_var.get()]
        ano = int(self.ano_var.get())
        num_dias_no_mes = monthrange(ano, mes_numero)[1]

        row_count = 0
        for matricula, info in dados_escala.items():
            tags_da_linha = ["evenrow" if row_count % 2 == 0 else "oddrow"]

            dias_info = info.get("dias", [])
            dias_de_trabalho = {turno["dia"]: turno for turno in dias_info}

            # Obtém dados de afastamento
            escala_data_base = info.get("escala_data_base")
            afastamento_inicio = info.get("afastamento_inicio")
            afastamento_fim = info.get("afastamento_fim")
            afastamento_motivo = info.get("afastamento_motivo")

            # Determina quais dias estão em afastamento
            dias_afastamento = set()
            motivo_abbrev = ""

            if (
                afastamento_inicio
                and afastamento_fim
                and afastamento_motivo
                and isinstance(afastamento_inicio, date)
                and isinstance(afastamento_fim, date)
            ):
                primeiro_dia_mes = date(ano, mes_numero, 1)
                ultimo_dia_mes = date(ano, mes_numero, num_dias_no_mes)

                # Verifica se há interseção entre o período de afastamento e o mês atual
                if (
                    afastamento_inicio <= ultimo_dia_mes
                    and afastamento_fim >= primeiro_dia_mes
                ):
                    data_inicio_no_mes = max(afastamento_inicio, primeiro_dia_mes)
                    data_fim_no_mes = min(afastamento_fim, ultimo_dia_mes)

                    for dia_num in range(
                        data_inicio_no_mes.day, data_fim_no_mes.day + 1
                    ):
                        dias_afastamento.add(dia_num)

                    # Define a abreviação
                    motivo_upper = afastamento_motivo.upper().strip()
                    motivo_abbrev = MOTIVO_ABBREV.get(
                        motivo_upper, motivo_upper[:2].upper()
                    )

            valores_linha = [info.get("nome", matricula)]

            for dia in range(1, 32):
                valor_celula = ""

                if dia <= num_dias_no_mes:
                    # 1. PRIORIDADE: Verifica se está em afastamento
                    if dia in dias_afastamento:
                        valor_celula = motivo_abbrev

                    # 2. Se NÃO está afastado, aplica lógica normal
                    else:
                        data_do_dia = date(ano, mes_numero, dia)
                        if escala_data_base and data_do_dia >= escala_data_base:
                            # Dentro do período válido: padrão é Folga
                            valor_celula = "F"

                            # Se tem trabalho neste dia, marca como X
                            if dia in dias_de_trabalho:
                                valor_celula = "X"

                valores_linha.append(valor_celula)

            self.tree.insert(
                "",
                "end",
                iid=str(matricula),
                image=self.img_unchecked,
                values=valores_linha,
                tags=tuple(tags_da_linha),
            )
            row_count += 1

    # def _salvar_no_historico(self):
    #     """Salva a escala gerada no histórico."""
    #     if self.ultima_escala_gerada:
    #         mes_nome = self.mes_var.get()
    #         ano = self.ano_var.get()

    #         confirmar = messagebox.askyesno(
    #             "Confirmar",
    #             f"Deseja salvar a escala de {mes_nome}/{ano} no histórico?\n"
    #             "Isso irá sobrescrever qualquer escala salva anteriormente para este mesmo período.",
    #             parent=self,
    #         )

    #         if confirmar:
    #             mes_numero = self.meses_map[mes_nome]
    #             self.app_controller.on_save_escala_historico(
    #                 self.ultima_escala_gerada, mes_numero, int(ano)
    #             )
    #     else:
    #         messagebox.showwarning(
    #             "Aviso", "Nenhuma escala foi gerada para salvar.", parent=self
    #         )

    def _exportar_para_excel(self):
        if not self.ultima_escala_gerada:
            messagebox.showwarning(
                "Aviso", "Gere uma prévia da escala antes de exportar.", parent=self
            )
            return
        mes_nome = self.mes_var.get()
        ano = self.ano_var.get()
        caminho_arquivo = filedialog.asksaveasfilename(
            title="Salvar arquivo Excel",
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx")],
            initialfile=f"escala_{mes_nome.lower()}_{ano}.xlsx",
        )
        if caminho_arquivo:
            try:
                mes_numero = self.meses_map[mes_nome]
                exporters.exportar_para_excel(
                    self.ultima_escala_gerada, int(ano), mes_numero, caminho_arquivo
                )
                abrir_pasta = messagebox.askyesno(
                    "Sucesso",
                    f"Arquivo Excel salvo com sucesso!\n\nDeseja abrir a pasta onde o arquivo foi salvo?",
                    parent=self,
                )
                if abrir_pasta:
                    os.startfile(os.path.dirname(caminho_arquivo))

            except Exception as e:
                messagebox.showerror(
                    "Erro na Exportação",
                    f"Não foi possível salvar o arquivo Excel:\n{e}",
                    parent=self,
                )

    def _exportar_para_pdf(self):
        if not self.ultima_escala_gerada:
            messagebox.showwarning(
                "Aviso", "Gere uma prévia da escala antes de exportar.", parent=self
            )
            return
        mes_nome = self.mes_var.get()
        ano = self.ano_var.get()
        caminho_arquivo = filedialog.asksaveasfilename(
            title="Salvar arquivo PDF",
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            initialfile=f"escala_{mes_nome.lower()}_{ano}.pdf",
        )
        if caminho_arquivo:
            try:
                mes_numero = self.meses_map[mes_nome]
                exporters.exportar_para_pdf(
                    self.ultima_escala_gerada, int(ano), mes_numero, caminho_arquivo
                )
                abrir_pasta = messagebox.askyesno(
                    "Sucesso",
                    f"Arquivo PDF salvo com sucesso!\n\nDeseja abrir a pasta onde o arquivo foi salvo?",
                    parent=self,
                )
                if abrir_pasta:
                    os.startfile(os.path.dirname(caminho_arquivo))

            except Exception as e:
                messagebox.showerror(
                    "Erro na Exportação",
                    f"Não foi possível salvar o arquivo PDF:\n{e}",
                    parent=self,
                )

    def _handle_modificacao_save(self, updates_dict):
        """
        Esta função é chamada pelo SetupEscalaView quando o usuário clica em salvar.
        updates_dict: {'matricula': 'AAAA-MM-DD', ...}
        """
        try:
            for matricula, nova_data_str in updates_dict.items():
                # Aqui usamos a função de banco de dados que já tínhamos
                db.atualizar_data_base_e_sequencia_padrao(matricula, nova_data_str)

            messagebox.showinfo(
                "Sucesso",
                f"{len(updates_dict)} colaborador(es) atualizado(s) com sucesso!",
                parent=self,
            )

            # Regera a prévia para mostrar os dados atualizados
            self._executar_geracao()

        except Exception as e:
            messagebox.showerror(
                "Erro na Atualização",
                f"Ocorreu um erro ao atualizar os dados: {e}",
                parent=self,
            )

    def _modificar_escala_selecionados(self):
        selecionados_matriculas = (
            self.get_selected_matriculas()
        )  # Pega os IIDs (matrículas)
        if not selecionados_matriculas:
            messagebox.showwarning(
                "Ninguém Selecionado",
                "Por favor, selecione um ou mais colaboradores na tabela para modificar a escala.",  # [cite: 134]
                parent=self,
            )
            return

        # 1. Preparar a lista de colaboradores para a tela de setup
        colaboradores_para_modificar = []

        # Verifica se os dados dos colaboradores foram carregados
        if (
            not hasattr(self, "colaboradores_carregados")
            or not self.colaboradores_carregados
        ):
            messagebox.showerror(
                "Erro",
                "Dados de colaboradores não encontrados. Gere uma prévia primeiro.",
                parent=self,
            )
            return

        for colab in self.colaboradores_carregados:
            matricula = colab.get("matricula")
            # Se o colaborador da lista completa estiver entre os selecionados na tabela...
            if matricula in selecionados_matriculas:
                # Formata a data base atual para "DD/MM/AAAA"
                data_base_str = ""
                data_base_obj = colab.get("escala_data_base")
                if data_base_obj:
                    try:
                        data_base_str = data_base_obj.strftime("%d/%m/%Y")
                    except Exception:
                        pass  # Deixa em branco se a data for inválida

                colaboradores_para_modificar.append(
                    {
                        "matricula": matricula,
                        "nome": colab.get("nome"),
                        "data_base_atual": data_base_str,  # Envia no formato DD/MM/AAAA
                    }
                )

        # 2. Chamar a tela SetupEscalaView
        SetupEscalaView(
            master=self,
            colaboradores=colaboradores_para_modificar,
            save_callback=self._handle_modificacao_save,  # <-- AQUI ESTÁ A MUDANÇA
            title="Modificar Escala de Colaboradores",
            mode="initial",
        )

    def get_selected_matriculas(self):
        """Retorna lista de matrículas selecionadas."""
        return list(self.selected_matriculas)  # [cite: 39]

    def update_context_buttons(self):
        """Habilita/desabilita botões baseado na seleção."""
        # Adaptado de [cite: 38]
        state = "normal" if self.selected_matriculas else "disabled"
        self.modificar_button.configure(state=state)

    def on_row_click(self, event):
        """Gerencia cliques nos checkboxes."""
        # Baseado em [cite: 36-38]
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # Alterna a seleção
        if item_id in self.selected_matriculas:
            self.selected_matriculas.remove(item_id)
            self.tree.item(item_id, image=self.img_unchecked)  # [cite: 37]
        else:
            self.selected_matriculas.add(item_id)
            self.tree.item(item_id, image=self.img_checked)  # [cite: 37]

        # Atualiza a seleção visual do CTkAdvancedTable
        if self.selected_matriculas:
            self.tree.selection_set(list(self.selected_matriculas))  # [cite: 37]
        else:
            self.tree.selection_set([])  # [cite: 37]

        self.update_context_buttons()  # [cite: 38]
