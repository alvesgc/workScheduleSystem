import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox
from ... import database as db
from ... import fonts
import pandas as pd
from PIL import Image, ImageTk
import os
import tkfontawesome as fa
from ..widgets.CTkAdvancedTable import CTkAdvancedTable
from .quick_edit_dialog_view import QuickEditDialog

class GerenciarColaboradoresView(ctk.CTkFrame):
    def __init__(self, master, app_controller, data_to_load=None):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller

        self.selected_matriculas = set()
        self.table_data = []
        self.hovered_item = None
        self.select_all_var = ctk.BooleanVar(value=False)

        # === PALETA DE CORES HIERÁRQUICA ===
        self.PRIMARY = "#0078D7"
        self.PRIMARY_HOVER = "#005EA6"
        self.SURFACE = "#FFFFFF"
        self.BORDER = "#E1E4E8"
        self.TEXT_PRIMARY = "#1E1E1E"
        self.TEXT_SECONDARY = "#6B6B6B"
        self.TEXT_TERTIARY = "#9CA3AF"
        self.BUTTON_SECONDARY = "#FFFFFF"
        self.BUTTON_SECONDARY_HOVER = "#F5F5F5"
        self.BUTTON_SECONDARY_BORDER = "#D1D5DB"
        self.DANGER = "#DC2626"
        self.DANGER_HOVER = "#B91C1C"

        # --- Carregar Imagens dos Checkboxes ---
        try:
            icon_path = "src/geradorEscalas/assets/icons"
            pil_checked = Image.open(
                os.path.join(icon_path, "checkbox_checked.png")
            ).resize((16, 16), Image.Resampling.LANCZOS)
            pil_unchecked = Image.open(
                os.path.join(icon_path, "checkbox_unchecked.png")
            ).resize((16, 16), Image.Resampling.LANCZOS)
            self.img_checked = ImageTk.PhotoImage(pil_checked)
            self.img_unchecked = ImageTk.PhotoImage(pil_unchecked)
        except Exception as e:
            print(f"ERRO: Não foi possível carregar as imagens de checkbox: {e}")
            self.img_checked = self.img_unchecked = None

        # === LAYOUT PRINCIPAL ===
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # === ÍCONES ===
        icon_size = 16
        self.icon_add = fa.icon_to_image(
            "plus", fill="#FFFFFF", scale_to_height=icon_size
        )
        self.icon_import = fa.icon_to_image(
            "file-import", fill=self.TEXT_SECONDARY, scale_to_height=icon_size
        )
        self.icon_edit = fa.icon_to_image(
            "pencil-alt", fill="#FFFFFF", scale_to_height=icon_size
        )
        self.icon_delete = fa.icon_to_image(
            "trash-alt", fill="#FFFFFF", scale_to_height=icon_size
        )
        self.icon_search = fa.icon_to_image(
            "search", fill="#FFFFFF", scale_to_height=icon_size
        )

        # === CABEÇALHO ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))

        ctk.CTkLabel(
            header_frame,
            text="Gerenciar Colaboradores",
            font=fonts.TITULO_SECAO,
            text_color=self.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            header_frame,
            text="Visualize, adicione, edite ou remova colaboradores do sistema.",
            font=fonts.SUBTITULO,
            text_color=self.TEXT_SECONDARY,
        ).pack(anchor="w")

        # === BARRA DE AÇÕES ===
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 16))
        actions_frame.grid_columnconfigure(0, weight=1)

        # Botões à direita
        buttons_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_container.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            buttons_container,
            text="Adicionar Novo",
            font=fonts.SUBTITULO,
            image=self.icon_add,
            compound="left",
            command=self.app_controller.show_cadastro_manual_view,
            fg_color=self.PRIMARY,
            hover_color=self.PRIMARY_HOVER,
            height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            buttons_container,
            text="Importar",
            font=fonts.SUBTITULO,
            image=self.icon_import,
            compound="left",
            command=self.app_controller.on_import_colaboradores,
            fg_color=self.BUTTON_SECONDARY,
            hover_color=self.BUTTON_SECONDARY_HOVER,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BUTTON_SECONDARY_BORDER,
            height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        self.edit_button = ctk.CTkButton(
            buttons_container,
            text="Editar",
            font=fonts.SUBTITULO,
            image=self.icon_edit,
            compound="left",
            command=self.edit_selected,
            fg_color=self.PRIMARY,
            hover_color=self.PRIMARY_HOVER,
            height=36,
            corner_radius=8,
            state="disabled",
        )
        self.edit_button.pack(side="left", padx=(0, 8))

        self.delete_button = ctk.CTkButton(
            buttons_container,
            text="Excluir",
            font=fonts.SUBTITULO,
            image=self.icon_delete,
            compound="left",
            command=self.delete_selected,
            fg_color=self.DANGER,
            hover_color=self.DANGER_HOVER,
            height=36,
            corner_radius=8,
            state="disabled",
        )
        self.delete_button.pack(side="left")

        # === BARRA DE PESQUISA ===
        search_container = ctk.CTkFrame(
            self,
            fg_color=self.SURFACE,
            border_color=self.BORDER,
            border_width=1,
            corner_radius=12,
        )
        search_container.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))

        search_inner = ctk.CTkFrame(search_container, fg_color="transparent")
        search_inner.pack(fill="x", padx=16, pady=12)
        search_inner.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Pesquisar por nome ou matrícula...",
            font=fonts.SUBTITULO,
            height=36,
            fg_color=self.BUTTON_SECONDARY,
            border_color=self.BUTTON_SECONDARY_BORDER,
            corner_radius=8,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.search_entry.bind("<Return>", self.perform_search)

        ctk.CTkButton(
            search_inner,
            text="Buscar",
            image=self.icon_search,
            compound="left",
            font=fonts.SUBTITULO,
            width=100,
            height=36,
            command=self.perform_search,
            fg_color=self.PRIMARY,
            hover_color=self.PRIMARY_HOVER,
            corner_radius=8,
        ).grid(row=0, column=1)

        # === CONTAINER DA TABELA ===
        self.table_container = ctk.CTkFrame(
            self,
            fg_color=self.SURFACE,
            border_width=1,
            border_color=self.BORDER,
            corner_radius=12,
        )
        self.table_container.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.table_container.grid_rowconfigure(1, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        # === HEADER DA TABELA COM CHECKBOX ===
        table_header = ctk.CTkFrame(self.table_container, fg_color="transparent")
        table_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))

        # Checkbox customizado com imagens
        self.select_all_frame = ctk.CTkFrame(
            table_header, fg_color="transparent", cursor="hand2"
        )
        self.select_all_frame.pack(side="left")
        self.select_all_frame.bind("<Button-1>", lambda e: self.on_select_all_toggle())

        self.select_all_image_label = ctk.CTkLabel(
            self.select_all_frame, text="", image=self.img_unchecked, cursor="hand2"
        )
        self.select_all_image_label.pack(side="left", padx=(0, 8))
        self.select_all_image_label.bind(
            "<Button-1>", lambda e: self.on_select_all_toggle()
        )

        self.select_all_text_label = ctk.CTkLabel(
            self.select_all_frame,
            text="Selecionar Todos",
            font=fonts.SUBTITULO,
            text_color=self.TEXT_SECONDARY,
            cursor="hand2",
        )
        self.select_all_text_label.pack(side="left")
        self.select_all_text_label.bind(
            "<Button-1>", lambda e: self.on_select_all_toggle()
        )

        # === FRAME DA TABELA ===
        self.table_frame = ctk.CTkFrame(self.table_container, fg_color="transparent")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.update_table(invalid_rows=data_to_load)
        self.update_context_buttons()

    def update_table(self, search_term=None, invalid_rows=None):
        """Atualiza a tabela de colaboradores."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.selected_matriculas.clear()

        df = (
            db.get_all_collaborators_dataframe(search_term)
            if invalid_rows is None
            else pd.DataFrame(invalid_rows)
        )

        # === ESTADO VAZIO ===
        if df.empty:
            msg_text = "Nenhum colaborador cadastrado."
            if search_term:
                msg_text = f"Nenhum resultado encontrado para '{search_term}'."
            elif invalid_rows is not None:
                msg_text = (
                    "Todos os colaboradores da planilha foram importados com sucesso!"
                )

            empty_label = ctk.CTkLabel(
                self.table_frame,
                text=msg_text,
                font=fonts.SUBTITULO,
                text_color=self.TEXT_TERTIARY,
            )
            empty_label.place(relx=0.5, rely=0.5, anchor="center")

            self.update_context_buttons()
            self._update_select_all_checkbox_state()
            return

        df.fillna("", inplace=True)

        colunas_visiveis = [
            "nome",
            "matricula",
            "cargo",
            "setor",
            "escala",
            "tipo_turno",
        ]

        # Se há observações (dados inválidos), adiciona coluna
        if "_observacao" in df.columns:
            colunas_visiveis.append("_observacao")

        colunas_df = [col for col in colunas_visiveis if col in df.columns]

        # === CRIA TABELA ===
        self.tree = CTkAdvancedTable(
            self.table_frame, columns=colunas_df, show_checkbox_column=True
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # === CONFIGURA COLUNAS ===
        column_config = {
            "nome": {"text": "Nome", "width": 300},
            "matricula": {"text": "Matrícula", "width": 120},
            "cargo": {"text": "Cargo", "width": 200},
            "setor": {"text": "Setor", "width": 180},
            "escala": {"text": "Escala", "width": 100},
            "tipo_turno": {"text": "Tipo de Turno", "width": 120},
            "_observacao": {"text": "Observação", "width": 250},
        }

        for col in colunas_df:
            config = column_config.get(col, {"text": col.title(), "width": 120})
            self.tree.heading(col, text=config["text"], anchor="w")
            self.tree.column(col, width=config["width"], anchor="w", stretch=ctk.YES)

        # === PREENCHE DADOS ===
        self.table_data = df.to_dict("records")
        used_iids = set()  # Controle de IDs únicos

        for i, record in enumerate(self.table_data):
            # Gera um ID único para cada linha
            matricula = record.get("matricula", "")

            # Se matrícula está vazia ou já foi usada, cria ID temporário único
            if not matricula or str(matricula).strip() == "":
                iid = f"temp_sem_matricula_{i}"
            else:
                base_iid = str(matricula).strip()
                # Se o ID já existe, adiciona sufixo
                if base_iid in used_iids:
                    counter = 1
                    while f"{base_iid}_dup_{counter}" in used_iids:
                        counter += 1
                    iid = f"{base_iid}_dup_{counter}"
                else:
                    iid = base_iid

            used_iids.add(iid)

            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            valores = [record.get(col, "") for col in colunas_df]

            try:
                self.tree.insert(
                    "",
                    "end",
                    iid=iid,
                    image=self.img_unchecked,
                    values=valores,
                    tags=(row_tag,),
                )
            except Exception as e:
                print(f"ERRO ao inserir linha {i} com iid '{iid}': {e}")
                # Tenta com ID alternativo em caso de erro
                alternative_iid = f"row_{i}_{hash(str(record))}"
                try:
                    self.tree.insert(
                        "",
                        "end",
                        iid=alternative_iid,
                        image=self.img_unchecked,
                        values=valores,
                        tags=(row_tag,),
                    )
                except Exception as e2:
                    print(f"ERRO CRÍTICO ao inserir linha {i}: {e2}")

        self.tree.bind("<Button-1>", self.on_row_click)
        self.update_context_buttons()
        self._update_select_all_checkbox_state()

    def on_row_click(self, event):
        """Gerencia cliques nos checkboxes."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        if item_id in self.selected_matriculas:
            self.selected_matriculas.remove(item_id)
            self.tree.item(item_id, image=self.img_unchecked)
        else:
            self.selected_matriculas.add(item_id)
            self.tree.item(item_id, image=self.img_checked)

        if self.selected_matriculas:
            self.tree.selection_set(list(self.selected_matriculas))
        else:
            self.tree.selection_set([])

        self.update_context_buttons()
        self._update_select_all_checkbox_state()

    def update_context_buttons(self):
        """Habilita/desabilita botões baseado na seleção."""
        state = "normal" if self.selected_matriculas else "disabled"
        self.edit_button.configure(state=state)
        self.delete_button.configure(state=state)

    def get_selected_matriculas(self):
        """Retorna lista de matrículas selecionadas."""
        return list(self.selected_matriculas)

    def edit_selected(self):
        """Edita colaboradores selecionados."""
        matriculas_selecionadas = self.get_selected_matriculas()
        if not matriculas_selecionadas:
            messagebox.showwarning(
                "Nenhuma Seleção",
                "Selecione um ou mais colaboradores para editar.",
                parent=self,
            )
            return

        if len(matriculas_selecionadas) == 1:
            # Edição única
            iid_selecionado = matriculas_selecionadas[0]

            # Busca o registro correspondente na table_data
            registro_para_editar = None
            indice_registro = None

            for i, record in enumerate(self.table_data):
                # Verifica se é o registro correto comparando o IID
                matricula = record.get("matricula", "")

                # Recria a lógica do IID para encontrar o registro correto
                if not matricula or str(matricula).strip() == "":
                    iid_esperado = f"temp_sem_matricula_{i}"
                else:
                    iid_esperado = str(matricula).strip()

                # Verifica se o IID corresponde (considera duplicatas)
                if iid_selecionado == iid_esperado or iid_selecionado.startswith(
                    f"{iid_esperado}_dup_"
                ):
                    registro_para_editar = record
                    indice_registro = i
                    break
                elif iid_selecionado == f"temp_sem_matricula_{i}":
                    registro_para_editar = record
                    indice_registro = i
                    break

            if registro_para_editar:
                # Se tem matrícula válida, passa para edição normal
                matricula_valida = registro_para_editar.get("matricula", "")
                if matricula_valida and str(matricula_valida).strip():
                    self.app_controller.show_cadastro_manual_view(
                        matricula_para_editar=matricula_valida
                    )
                else:
                    # Se não tem matrícula, abre diálogo para completar os dados
                    self._open_quick_edit_dialog(
                        registro_para_editar, indice_registro, iid_selecionado
                    )
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível localizar o registro selecionado.",
                    parent=self,
                )
        else:
            # Edição em lote
            dados_selecionados = []
            registros_incompletos = []

            for iid_selecionado in matriculas_selecionadas:
                for i, record in enumerate(self.table_data):
                    matricula = record.get("matricula", "")

                    # Recria a lógica do IID
                    if not matricula or str(matricula).strip() == "":
                        iid_esperado = f"temp_sem_matricula_{i}"
                    else:
                        iid_esperado = str(matricula).strip()

                    # Verifica correspondência
                    if iid_selecionado == iid_esperado or iid_selecionado.startswith(
                        f"{iid_esperado}_dup_"
                    ):
                        # Verifica se tem dados completos
                        if matricula and str(matricula).strip():
                            dados_selecionados.append(record)
                        else:
                            registros_incompletos.append(record.get("nome", "Sem nome"))
                        break
                    elif iid_selecionado == f"temp_sem_matricula_{i}":
                        registros_incompletos.append(record.get("nome", "Sem nome"))
                        break

            if registros_incompletos:
                messagebox.showwarning(
                    "Edição em Lote Não Permitida",
                    f"A edição em lote não pode ser realizada porque {len(registros_incompletos)} "
                    f"registro(s) selecionado(s) possui(em) dados incompletos.\n\n"
                    f"Complete os dados obrigatórios (Nome e Matrícula) editando individualmente "
                    f"cada registro antes de usar a edição em lote.",
                    parent=self,
                )
                return

            if dados_selecionados:
                self.app_controller.show_edicao_lote_view(dados_selecionados)
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível localizar os registros selecionados.",
                    parent=self,
                )

    def _open_quick_edit_dialog(self, registro, indice, iid):
        # Define um dicionário com as cores necessárias para o diálogo
        colors_for_dialog = {
            "PRIMARY": self.PRIMARY,
            "PRIMARY_HOVER": self.PRIMARY_HOVER,
            "SURFACE": self.SURFACE,
            "BORDER": self.BORDER,
            "TEXT_PRIMARY": self.TEXT_PRIMARY,
            "TEXT_SECONDARY": self.TEXT_SECONDARY,
            "BUTTON_SECONDARY": self.BUTTON_SECONDARY,
            "BUTTON_SECONDARY_HOVER": self.BUTTON_SECONDARY_HOVER,
            "BUTTON_SECONDARY_BORDER": self.BUTTON_SECONDARY_BORDER,
            "DANGER": self.DANGER,
            "DANGER_HOVER": self.DANGER_HOVER,
        }

        # Função callback que será chamada pelo diálogo ao salvar
        def handle_quick_save(dados_completos):
            sucesso, msg = db.add_colaborador(dados_completos)
            if sucesso:
                self.update_table() # Atualiza a tabela principal
            else:
                messagebox.showerror("Erro ao Salvar", msg or "Erro desconhecido ao salvar.", parent=self)

        # Cria e espera o diálogo
        dialog = QuickEditDialog(
            master=self,
            registro=registro,
            save_callback=handle_quick_save,
            colors_dict=colors_for_dialog
        )
    def delete_selected(self):
        """Exclui colaboradores selecionados."""
        matriculas = self.get_selected_matriculas()
        if not matriculas:
            messagebox.showwarning(
                "Nenhuma Seleção",
                "Selecione um ou mais colaboradores para excluir.",
                parent=self,
            )
            return

        # Separa registros válidos e inválidos
        matriculas_validas = []
        registros_invalidos = []

        for iid_selecionado in matriculas:
            for i, record in enumerate(self.table_data):
                matricula = record.get("matricula", "")

                # Recria a lógica do IID
                if not matricula or str(matricula).strip() == "":
                    iid_esperado = f"temp_sem_matricula_{i}"
                else:
                    iid_esperado = str(matricula).strip()

                # Verifica correspondência
                if iid_selecionado == iid_esperado or iid_selecionado.startswith(
                    f"{iid_esperado}_dup_"
                ):
                    if matricula and str(matricula).strip():
                        matriculas_validas.append(matricula)
                    else:
                        registros_invalidos.append(i)
                    break
                elif iid_selecionado == f"temp_sem_matricula_{i}":
                    registros_invalidos.append(i)
                    break

        # Monta mensagem de confirmação
        msg_parts = []
        if matriculas_validas:
            msg_parts.append(f"{len(matriculas_validas)} colaborador(es) cadastrado(s)")
        if registros_invalidos:
            msg_parts.append(f"{len(registros_invalidos)} registro(s) incompleto(s)")

        mensagem = f"Tem certeza que deseja excluir {' e '.join(msg_parts)}?"

        if messagebox.askyesno("Confirmar Exclusão", mensagem, parent=self):
            # Exclui do banco os que têm matrícula
            if matriculas_validas:
                self.app_controller.on_delete_collaborators(matriculas_validas)

            # Remove registros inválidos da tabela
            if registros_invalidos:
                # Ordena de trás pra frente para não bagunçar os índices
                for idx in sorted(registros_invalidos, reverse=True):
                    if idx < len(self.table_data):
                        self.table_data.pop(idx)

                # Atualiza a tabela mantendo apenas os registros restantes
                registros_restantes = [
                    r
                    for i, r in enumerate(self.table_data)
                    if "_observacao" in r  # Mantém apenas os inválidos
                ]

                if registros_restantes:
                    self.update_table(invalid_rows=registros_restantes)
                else:
                    self.update_table()

                messagebox.showinfo(
                    "Exclusão Concluída",
                    f"{len(registros_invalidos)} registro(s) incompleto(s) removido(s) da lista.",
                    parent=self,
                )

    def perform_search(self, event=None):
        """Executa a busca."""
        search_term = self.search_entry.get()
        self.update_table(search_term=search_term)

    def on_select_all_toggle(self):
        """Seleciona ou desmarca todos os colaboradores."""
        if not hasattr(self, "tree") or not self.tree.get_children():
            return

        all_item_ids = self.tree.get_children()

        # Alterna o estado
        self.select_all_var.set(not self.select_all_var.get())

        if self.select_all_var.get():
            # Marca todos
            self.select_all_image_label.configure(image=self.img_checked)
            for item_id in all_item_ids:
                if item_id not in self.selected_matriculas:
                    self.selected_matriculas.add(item_id)
                    self.tree.item(item_id, image=self.img_checked)
        else:
            # Desmarca todos
            self.select_all_image_label.configure(image=self.img_unchecked)
            for item_id in all_item_ids:
                if item_id in self.selected_matriculas:
                    self.selected_matriculas.remove(item_id)
                    self.tree.item(item_id, image=self.img_unchecked)

        # Atualiza seleção visual
        if self.selected_matriculas:
            self.tree.selection_set(list(self.selected_matriculas))
        else:
            self.tree.selection_set([])

        self.update_context_buttons()

    def _update_select_all_checkbox_state(self):
        """Atualiza o estado do checkbox 'Selecionar Todos'."""
        if not hasattr(self, "tree") or not self.tree.get_children():
            if self.select_all_var.get() != False:
                self.select_all_var.set(False)
                self.select_all_image_label.configure(image=self.img_unchecked)
            self.select_all_frame.configure(cursor="arrow")
            self.select_all_image_label.configure(cursor="arrow")
            self.select_all_text_label.configure(
                cursor="arrow", text_color=self.TEXT_TERTIARY
            )
            return

        # Configura cursor apenas se necessário
        if self.select_all_frame.cget("cursor") != "hand2":
            self.select_all_frame.configure(cursor="hand2")
            self.select_all_image_label.configure(cursor="hand2")
            self.select_all_text_label.configure(
                cursor="hand2", text_color=self.TEXT_SECONDARY
            )

        total_items = len(self.tree.get_children())
        selected_items = len(self.selected_matriculas)

        # Atualiza apenas se o estado mudou
        should_be_checked = total_items > 0 and selected_items == total_items

        if self.select_all_var.get() != should_be_checked:
            self.select_all_var.set(should_be_checked)
            if should_be_checked:
                self.select_all_image_label.configure(image=self.img_checked)
            else:
                self.select_all_image_label.configure(image=self.img_unchecked)
