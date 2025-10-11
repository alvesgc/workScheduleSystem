from calendar import monthrange, weekday
import os
import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from datetime import datetime
import tkfontawesome as fa
from ..widgets import ctk_checklist_dropdown as checklist
from ... import exporters
from ... import fonts
from ...escala_engine import GeradorEscalaEngine
from ... import database as db
from .setup_escala_view import SetupEscalaView
from ..widgets.CTkAdvancedTable import CTkAdvancedTable

ChecklistDropdown = checklist.ChecklistDropdown


class GeradorEscalaView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.ultima_escala_gerada = None

        # --- Carrega os dados para os filtros ---
        self.escala_filter_vars = {escala: ctk.StringVar(value="on") for escala in db.get_distinct_escala_types()}
        all_collaborators = db.get_all_active_collaborators()
        self.colab_filter_vars = {colab['matricula']: ctk.StringVar(value="on") for colab in all_collaborators}
        self.colab_matricula_to_name = {colab['matricula']: colab['nome'] for colab in all_collaborators}
        self.setor_filter_vars = {setor: ctk.StringVar(value="on") for setor in db.get_distinct_setores()}

        # --- Ícones ---
        icon_color = "#DCE4EE"
        icon_size = 16
        self.icons = {
            "filter": fa.icon_to_image("filter", fill=icon_color, scale_to_height=icon_size),
            "users": fa.icon_to_image("users", fill=icon_color, scale_to_height=icon_size),
            "generate": fa.icon_to_image("cogs", fill=icon_color, scale_to_height=icon_size),
            "save": fa.icon_to_image("save", fill=icon_color, scale_to_height=icon_size),
            "excel": fa.icon_to_image("file-excel", fill=icon_color, scale_to_height=icon_size),
            "pdf": fa.icon_to_image("file-pdf", fill=icon_color, scale_to_height=icon_size)
        }

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # A linha 2 (tabela) expande

        # --- Frame de Controles (Topo) com Borda ---
        controls_frame = ctk.CTkFrame(self, border_width=1, border_color="gray30")
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1) # Coluna "vazia" para empurrar o botão Gerar

        # Frame interno para não ter borda dupla
        inner_controls_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        inner_controls_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        inner_controls_frame.grid_columnconfigure(5, weight=1)

        # Período (Mês e Ano)
        meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.meses_map = {nome: i + 1 for i, nome in enumerate(meses_nomes)}
        self.mes_var = ctk.StringVar(value=meses_nomes[datetime.now().month - 1])
        ctk.CTkLabel(inner_controls_frame, text="Mês:", font=fonts.LABEL_FONT).grid(row=0, column=0, padx=(0, 5), pady=10)
        ctk.CTkOptionMenu(inner_controls_frame, variable=self.mes_var, values=meses_nomes, width=120).grid(row=0, column=1, padx=(0, 20), pady=10)
        ctk.CTkLabel(inner_controls_frame, text="Ano:", font=fonts.LABEL_FONT).grid(row=0, column=2, padx=(0, 5), pady=10)
        self.ano_var = ctk.StringVar(value=str(datetime.now().year))
        ctk.CTkEntry(inner_controls_frame, textvariable=self.ano_var, width=80).grid(row=0, column=3, padx=(0, 20), pady=10)

        # Botões de Filtro
        filter_buttons_frame = ctk.CTkFrame(inner_controls_frame, fg_color="transparent")
        filter_buttons_frame.grid(row=0, column=4, sticky="w")
        self.escala_filter_button = ctk.CTkButton(filter_buttons_frame, text="Escalas",font=fonts.BUTTON_FONT, image=self.icons.get("filter"), compound="left", command=self._open_escala_filter)
        self.escala_filter_button.pack(side="left", padx=5)
        self.setor_filter_button = ctk.CTkButton(filter_buttons_frame, text="Setores",font=fonts.BUTTON_FONT, image=self.icons.get("filter"), compound="left", command=self._open_setor_filter)
        self.setor_filter_button.pack(side="left", padx=5)
        self.colab_filter_button = ctk.CTkButton(filter_buttons_frame, text="Colaboradores",font=fonts.BUTTON_FONT, image=self.icons.get("users"), compound="left", command=self._open_colab_filter)
        self.colab_filter_button.pack(side="left", padx=5)

        # Botão Gerar Prévia
        self.generate_button = ctk.CTkButton(inner_controls_frame, text="Gerar Prévia", image=self.icons.get("generate"), compound="left", font=fonts.BUTTON_FONT, command=self._gerar_previa)
        self.generate_button.grid(row=0, column=6, padx=(20, 0), pady=10, sticky="e")

        # --- Frame de Ações ---
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=1, column=0, padx=10, pady=0, sticky="e")

        self.salvar_button = ctk.CTkButton(actions_frame, text="Salvar",font=fonts.BUTTON_FONT, image=self.icons.get("save"), compound="left", state="disabled", command=self._salvar_no_historico)
        self.salvar_button.pack(side="left", padx=5)
        self.excel_button = ctk.CTkButton(actions_frame, text="Excel", font=fonts.BUTTON_FONT,image=self.icons.get("excel"), compound="left", state="disabled", command=self._exportar_para_excel)
        self.excel_button.pack(side="left", padx=5)
        self.pdf_button = ctk.CTkButton(actions_frame, text="PDF", font=fonts.BUTTON_FONT,image=self.icons.get("pdf"), compound="left", state="disabled", command=self._exportar_para_pdf)
        self.pdf_button.pack(side="left", padx=5)

        # --- ESTRUTURA DA TABELA CORRIGIDA ---
        # 1. Cria um "Container" que terá a borda e nunca será limpo.
        table_container = ctk.CTkFrame(self, border_width=1, border_color="gray30")
        table_container.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # 2. O 'preview_frame' agora vive DENTRO do container e não tem borda própria.
        # É este frame que será limpo e preenchido.
        self.preview_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=1, pady=1) # Padding para a borda ser visível
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        # --- FIM DA ESTRUTURA CORRIGIDA ---

        self.empty_label = ctk.CTkLabel(self.preview_frame, text="Selecione o Mês e Ano e clique em 'Gerar Prévia' para começar.", font=fonts.SUBTITULO, text_color="gray60")
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

        self._update_escala_filter_button_text()
        self._update_colab_filter_button_text()
        self._update_setor_filter_button_text()

    def _setup_treeview(self):
        """
        Cria a tabela usando o componente CTkAdvancedTable e define
        as colunas específicas para a tela de geração de escala.
        """
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        colunas = ["Colaborador"] + [str(i) for i in range(1, 32)]

        # 1. Cria a tabela usando nosso componente customizado
        self.tree = CTkAdvancedTable(self.preview_frame, columns=colunas, show_checkbox_column=False)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # 2. Configura as colunas (isso permanece aqui, pois é específico desta tela)
        self.tree.heading("Colaborador", text="Colaborador", anchor="w")
        self.tree.column(
            "Colaborador", width=350, minwidth=250, anchor="w", stretch=ctk.NO
        )

        for i in range(1, 32):
            self.tree.heading(str(i), text=str(i))
            min_width = 70 if i % 8 == 1 and i > 1 else 45
            self.tree.column(
                str(i), width=45, minwidth=min_width, anchor="center", stretch=ctk.NO
            )

        # 3. Configura os scrollbars
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
            popup = SetupEscalaView(
                self, colaboradores=unconfigured, save_callback=self._on_setup_save
            )
            self.wait_window(popup)
        else:
            self._executar_geracao()

    def _on_setup_save(self, updates):
        success, message = db.update_collaborator_base_dates(updates)
        if success:
            self._executar_geracao()
        else:
            messagebox.showerror("Erro ao Salvar", message)

    def _open_escala_filter(self):
        # Monta o dicionário de itens para o dropdown
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
        """
        Coleta os filtros, busca os dados, chama o motor de geração e preenche a tabela.
        """
        # --- LÓGICA DE FEEDBACK VISUAL (CARREGAMENTO) ---
        self._setup_treeview()  # Limpa e prepara a tabela para novos dados
        loading_label = ctk.CTkLabel(
            self.tree,
            text="Gerando escala, por favor aguarde...",
            font=fonts.SUBTITULO,
            bg_color="#2B2B2B",
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.generate_button.configure(state="disabled")
        # Desativa botões de ação para evitar cliques durante a geração
        self.salvar_button.configure(state="disabled")
        self.excel_button.configure(state="disabled")
        self.pdf_button.configure(state="disabled")
        self.update_idletasks()  # Força a UI a redesenhar e mostrar o "loading"

        try:
            # --- 1. COLETAR FILTROS DA TELA ---
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
            # --- 2. BUSCAR COLABORADORES JÁ FILTRADOS NO BANCO ---
            colaboradores_para_gerar = db.get_all_active_collaborators(filtros=filtros)

            if not colaboradores_para_gerar:
                messagebox.showinfo(
                    "Aviso",
                    "Nenhum colaborador corresponde aos filtros selecionados.",
                    parent=self,
                )
                return  # Encerra a execução se não houver ninguém para gerar a escala

            # --- 3. EXECUTAR O MOTOR COM OS DADOS FILTRADOS ---
            mes_numero = self.meses_map[self.mes_var.get()]
            ano = int(self.ano_var.get())

            self._marcar_dias_especiais(ano, mes_numero)

            engine = GeradorEscalaEngine(ano, mes_numero)
            # Passa a lista já filtrada para o motor
            dados_escala = engine.executar(colaboradores_para_gerar)

            # Guarda a escala gerada para poder salvar/exportar depois
            self.ultima_escala_gerada = dados_escala

            self._preencher_tabela(dados_escala)

            # --- 4. ATIVAR BOTÕES DE AÇÃO ---
            self.salvar_button.configure(state="normal")
            self.excel_button.configure(state="normal")
            self.pdf_button.configure(state="normal")

        except Exception as e:
            messagebox.showerror(
                "Erro na Geração", f"Ocorreu um erro ao gerar a escala: {e}"
            )

        finally:
            # --- 5. LIMPEZA FINAL ---
            # Garante que o label de loading seja removido e o botão reativado, mesmo se der erro
            if loading_label.winfo_exists():
                loading_label.destroy()
            self.generate_button.configure(state="normal")

    def _marcar_fins_de_semana(self, ano, mes):
        """Adiciona um marcador visual nos cabeçalhos de Sábados e Domingos."""
        try:
            num_dias = monthrange(ano, mes)[1]
            for dia in range(1, 32):
                # Reseta o cabeçalho para o padrão
                self.tree.heading(str(dia), text=str(dia))
                if dia <= num_dias and weekday(ano, mes, dia) >= 5:  # 5=Sáb, 6=Dom
                    self.tree.heading(str(dia), text=f"•{dia}•")
        except Exception as e:
            print(f"Erro ao marcar fins de semana: {e}")

    def _marcar_dias_especiais(self, ano, mes):
        """Adiciona marcadores visuais nos cabeçalhos de dias especiais."""
        today = datetime.now()
        num_dias = monthrange(ano, mes)[1]
        for dia in range(1, 32):
            # Reseta o cabeçalho para o padrão
            self.tree.heading(str(dia), text=str(dia))
            if dia <= num_dias:
                # Marca fins de semana
                if weekday(ano, mes, dia) >= 5:  # 5=Sáb, 6=Dom
                    self.tree.heading(str(dia), text=f"•{dia}•")
                # Marca o dia atual com um destaque diferente
                if ano == today.year and mes == today.month and dia == today.day:
                    self.tree.heading(str(dia), text=f"[{dia}]")

    def _preencher_tabela(self, dados_escala):
        """Preenche a tabela com os dados, aplicando estilos de linha corretamente."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        row_count = 0
        for matricula, info in dados_escala.items():
            tags_da_linha = []

            # 1. Adiciona a tag de cor de fundo (par ou ímpar)
            tags_da_linha.append("evenrow" if row_count % 2 == 0 else "oddrow")

            # 2. Determina a tag de cor de TEXTO e FONTE prioritária para a linha inteira
            tem_afastamento = any(
                turno.get("em_afastamento") for turno in info.get("dias", [])
            )
            tem_24h = any(
                turno["turno"].upper() == "24H" for turno in info.get("dias", [])
            )
            tem_noturno = any(
                turno["turno"].upper() == "N" for turno in info.get("dias", [])
            )
            tem_diurno = any(
                turno["turno"].upper() == "D" for turno in info.get("dias", [])
            )

            if tem_afastamento:
                tags_da_linha.append("afastamento")
                tags_da_linha.append(
                    "afastamento_font"
                )  # Adiciona o estilo de fonte itálico
            elif tem_24h:
                tags_da_linha.append("turno_24H")
                tags_da_linha.append(
                    "critical_escala"
                )  # Adiciona o estilo de fonte negrito
            elif tem_noturno:
                tags_da_linha.append("turno_N")
            elif tem_diurno:
                tags_da_linha.append("turno_D")

            # Adiciona o negrito para 24h mesmo se houver afastamento (nome fica em negrito)
            if tem_24h and "critical_escala" not in tags_da_linha:
                tags_da_linha.append("critical_escala")

            # 3. Insere a linha com o nome, aplicando TODAS as tags
            item_id = self.tree.insert(
                "",
                "end",
                values=[info.get("nome", matricula)],
                tags=tuple(tags_da_linha),
            )

            # 4. Preenche as células com o texto dos turnos
            for turno_info in info.get("dias", []):
                dia = turno_info.get("dia")
                tipo_turno = turno_info.get("turno", "X").upper()
                esta_afastado = turno_info.get("em_afastamento", False)

                if dia:
                    valor_celula = f"{tipo_turno}(A)" if esta_afastado else tipo_turno
                    self.tree.set(item_id, column=str(dia), value=valor_celula)

            row_count += 1

    def _salvar_no_historico(self):
        """Pega a última escala gerada e pede ao controller para salvá-la, com confirmação."""
        if self.ultima_escala_gerada:
            mes_nome = self.mes_var.get()
            ano = self.ano_var.get()

            # --- ADIÇÃO DA CONFIRMAÇÃO ---
            confirmar = messagebox.askyesno(
                "Confirmar",
                f"Deseja salvar a escala de {mes_nome}/{ano} no histórico?\n"
                "Isso irá sobrescrever qualquer escala salva anteriormente para este mesmo período.",
                parent=self,
            )

            if confirmar:
                mes_numero = self.meses_map[mes_nome]
                self.app_controller.on_save_escala_historico(
                    self.ultima_escala_gerada, mes_numero, int(ano)
                )
        else:
            messagebox.showwarning(
                "Aviso", "Nenhuma escala foi gerada para salvar.", parent=self
            )

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
                messagebox.showinfo(
                    "Sucesso",
                    f"Arquivo Excel salvo em:\n{caminho_arquivo}",
                    parent=self,
                )
                abrir_pasta = messagebox.askyesno(
                    "Sucesso",
                    f"Arquivo Excel salvo com sucesso!\n\nDeseja abrir a pasta onde o arquivo foi salvo?",
                    parent=self,
                )
                if abrir_pasta:
                    # Abre o explorador de arquivos na pasta do arquivo salvo
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
                messagebox.showinfo(
                    "Sucesso", f"Arquivo PDF salvo em:\n{caminho_arquivo}", parent=self
                )
                abrir_pasta = messagebox.askyesno(
                    "Sucesso",
                    f"Arquivo Excel salvo com sucesso!\n\nDeseja abrir a pasta onde o arquivo foi salvo?",
                    parent=self,
                )
                if abrir_pasta:
                    # Abre o explorador de arquivos na pasta do arquivo salvo
                    os.startfile(os.path.dirname(caminho_arquivo))

            except Exception as e:
                messagebox.showerror(
                    "Erro na Exportação",
                    f"Não foi possível salvar o arquivo PDF:\n{e}",
                    parent=self,
                )
