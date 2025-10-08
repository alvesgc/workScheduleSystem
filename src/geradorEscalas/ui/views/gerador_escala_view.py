from calendar import monthrange, weekday
import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from datetime import datetime

from ... import exporters
from ... import fonts
from ...escala_engine import GeradorEscalaEngine
from ... import database as db
from .setup_escala_view import SetupEscalaView


class GeradorEscalaView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app_controller = app_controller
        self.ultima_escala_gerada = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Frame de Controles (Topo) ---
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
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
        ctk.CTkLabel(controls_frame, text="Mês:", font=fonts.LABEL_FONT).pack(
            side="left", padx=(10, 5), pady=10
        )
        ctk.CTkOptionMenu(
            controls_frame, variable=self.mes_var, values=meses_nomes
        ).pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(controls_frame, text="Ano:", font=fonts.LABEL_FONT).pack(
            side="left", padx=(20, 5), pady=10
        )
        self.ano_var = ctk.StringVar(value=str(datetime.now().year))
        ctk.CTkEntry(controls_frame, textvariable=self.ano_var, width=80).pack(
            side="left", padx=5, pady=10
        )
        self.generate_button = ctk.CTkButton(
            controls_frame,
            text="Gerar Prévia da Escala",
            font=fonts.BUTTON_FONT,
            command=self._gerar_previa,
        )
        self.generate_button.pack(side="left", padx=20, pady=10)

        # --- Frame de Ações (Meio) ---
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")

        # --- CORREÇÃO: Comandos atribuídos diretamente na criação dos botões ---
        self.salvar_button = ctk.CTkButton(
            actions_frame,
            text="Salvar no Histórico",
            state="disabled",
            command=self._salvar_no_historico,
        )
        self.salvar_button.pack(side="left", padx=5)

        self.excel_button = ctk.CTkButton(
            actions_frame,
            text="Exportar para Excel",
            state="disabled",
            command=self._exportar_para_excel,
        )
        self.excel_button.pack(side="left", padx=5)

        self.pdf_button = ctk.CTkButton(
            actions_frame,
            text="Exportar para PDF",
            state="disabled",
            command=self._exportar_para_pdf,
        )
        self.pdf_button.pack(side="left", padx=5)

        # --- Frame da Pré-visualização (Principal) ---
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            self.preview_frame,
            text="Selecione o Mês e Ano e clique em 'Gerar Prévia' para começar.",
            font=fonts.SUBTITULO,
            text_color="gray60",
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def _setup_treeview(self):
        """Cria e configura o widget Treeview."""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        colunas = ["Colaborador"] + [str(i) for i in range(1, 32)]
        self.tree = ttk.Treeview(
            self.preview_frame, columns=colunas, show="headings", style="Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # --- CORREÇÃO: Configuração das tags movida para cá ---
        self.tree.tag_configure(
            "turno_D", foreground="#00A4FF", font=("Calibri", 9, "bold")
        )
        self.tree.tag_configure(
            "turno_N", foreground="#FFB800", font=("Calibri", 9, "bold")
        )
        self.tree.tag_configure(
            "turno_24h", foreground="#4CAF50", font=("Calibri", 9, "bold")
        )

        self.tree.heading("Colaborador", text="Colaborador")
        self.tree.column("Colaborador", width=250, anchor="w")
        for i in range(1, 32):
            self.tree.heading(str(i), text=str(i))
            self.tree.column(str(i), width=40, anchor="center")

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

    def _executar_geracao(self):
        self._setup_treeview()
        loading_label = ctk.CTkLabel(
            self.tree,
            text="Gerando escala, por favor aguarde...",
            font=fonts.SUBTITULO,
            bg_color="#2B2B2B",
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.generate_button.configure(state="disabled")
        self.update_idletasks()

        try:
            mes_numero = self.meses_map[self.mes_var.get()]
            ano = int(self.ano_var.get())
            self._marcar_fins_de_semana(ano, mes_numero)

            engine = GeradorEscalaEngine(ano, mes_numero)
            dados_escala = engine.executar()
            self.ultima_escala_gerada = dados_escala
            self._preencher_tabela(dados_escala)

            self.salvar_button.configure(state="normal")
            self.excel_button.configure(state="normal")
            self.pdf_button.configure(state="normal")
        except Exception as e:
            messagebox.showerror(
                "Erro na Geração", f"Ocorreu um erro ao gerar a escala: {e}"
            )
        finally:
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

    def _preencher_tabela(self, dados_escala):
        """Preenche a tabela com os dados da escala, usando D/N/24h."""
        for matricula, info in dados_escala.items():
            # Cria a linha apenas com o nome
            item_id = self.tree.insert("", "end", values=[info.get("nome", matricula)])

            # Preenche apenas as células dos dias de trabalho
            for turno_info in info.get("dias", []):
                dia = turno_info.get("dia")
                tipo_turno = turno_info.get("turno", "X")
                if dia:
                    self.tree.set(item_id, column=str(dia), value=tipo_turno)
                    # Aplica a tag à linha inteira para colorir o texto
                    self.tree.item(
                        item_id, tags=(f"turno_{tipo_turno.upper()}",)
                    )  # .upper() para segurança

    def _salvar_no_historico(self):
        if self.ultima_escala_gerada:
            mes_numero = self.meses_map[self.mes_var.get()]
            ano = int(self.ano_var.get())
            self.app_controller.on_save_escala_historico(
                self.ultima_escala_gerada, mes_numero, ano
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
            except Exception as e:
                messagebox.showerror(
                    "Erro na Exportação",
                    f"Não foi possível salvar o arquivo PDF:\n{e}",
                    parent=self,
                )
