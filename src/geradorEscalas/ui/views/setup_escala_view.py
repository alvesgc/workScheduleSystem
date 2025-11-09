import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

from ...utils import resource_path
from ... import fonts
from ..widgets.ctk_calendar import CTkCalendar
import tkfontawesome as fa
import os  # Necessário para carregar imagens
from PIL import Image, ImageTk  # Necessário para carregar imagens


    
class SetupEscalaView(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        colaboradores,
        save_callback,
        title="Configuração de Escalas",
        mode="modify",
    ):
        """
        Janela para configurar ou modificar datas base de colaboradores.
        'mode' pode ser 'modify' (padrão) ou 'initial' (começa tudo marcado).
        """
      
        self.SUCCESS = "#10B981"
        self.SUCCESS_HOVER = "#059669"
        
        super().__init__(master)
        self.save_callback = save_callback
        self.colaboradores = colaboradores

        self.title(title)
        self.geometry("700x450")
        self.resizable(False, False)

        # --- CORREÇÃO DO PROBLEMA 1 (AttributeError) ---
        # Defina as cores que você estava usando
        self.PRIMARY = "#1F6AA5"  # Cor primária (azul)
        self.PRIMARY_HOVER = "#144870"  # Tom mais escuro para hover
        # --- FIM DA CORREÇÃO ---

        # --- Variáveis de estado ---
        self.check_vars = {}
        self.date_vars = {}
        self.widget_map = {}
        self._trace_active = True

        is_initial_setup = mode == "initial"
        initial_check_state = is_initial_setup
        initial_widget_state = "normal" if is_initial_setup else "disabled"

        # --- Carregar ícones de Checkbox ---
        self.img_checked = None
        self.img_unchecked = None
        try:
            icon_path = resource_path(os.path.join("src", "geradorEscalas", "assets","icons"))
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

        today_str = datetime.now().strftime("%d/%m/%Y")
        initial_check_image = (
            self.img_checked if is_initial_setup else self.img_unchecked
        )

        # --- Título ---
        ctk.CTkLabel(self, text=title, font=fonts.TITULO_SECAO).pack(pady=10)
        ctk.CTkLabel(
            self,
            text="Marque os colaboradores e defina a nova data de início do ciclo.",
            justify="left",
        ).pack(pady=5, padx=20)

        # --- Frame de Rolagem ---
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Esta linha agora funciona, pois 'icon_color' foi removido
        icon_calendar = fa.icon_to_image(
            "calendar-alt", fill="#FFFFFF", scale_to_height=16
        )

        # --- Loop para criar as linhas de colaborador ---
        for colab in self.colaboradores:
            nome = colab.get("nome")
            matricula = colab.get("matricula")
            data_base_str = colab.get("data_base_atual") or today_str

            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8, padx=5)

            # --- WIDGET 1: Checkbox (com imagem) ---
            check_var = ctk.BooleanVar(value=initial_check_state)
            self.check_vars[matricula] = check_var

            check_button = ctk.CTkButton(
                row_frame,
                text="",
                image=initial_check_image,
                width=28,
                height=28,
                fg_color="transparent",
                hover=False,
            )
            if self.img_checked is None:
                check_button.destroy()
                check_button = ctk.CTkCheckBox(
                    row_frame, text="", variable=check_var, width=28
                )

            # --- WIDGET 2: Variável e Campo de Data ---
            # Deve ser criado ANTES do botão de calendário
            date_var = ctk.StringVar(value=data_base_str)
            date_var.trace_add(
                "write", lambda name, index, mode, var=date_var: self._format_date(var)
            )
            self.date_vars[matricula] = date_var

            date_display_entry = ctk.CTkEntry(
                row_frame,
                width=150,
                placeholder_text="DD/MM/AAAA",
                font=fonts.TEXTO_NORMAL,
                textvariable=date_var,
                state=initial_widget_state,
            )

            # --- WIDGET 3: Botão Calendário ---
            # Agora 'date_var' existe e pode ser usada no comando lambda
            select_date_button = ctk.CTkButton(
                row_frame,
                text="",
                image=icon_calendar,
                width=35,
                height=35,
                fg_color=self.PRIMARY,
                hover_color=self.PRIMARY_HOVER,
                command=lambda var=date_var: self._open_calendar(var),  # <-- CORRIGIDO
                state=initial_widget_state,
            )

            # --- WIDGET 4: Nome do Colaborador ---
            name_label = ctk.CTkLabel(
                row_frame, text=f"{nome}:", anchor="w", font=fonts.LABEL_FONT
            )

            # --- ORDEM DE EMPACOTAMENTO (Para corrigir o alinhamento) ---

            # 1. Empacota o Checkbox à ESQUERDA
            check_button.pack(side="left", padx=(0, 5))

            # 2. Empacota o Botão Calendário à DIREITA (fixo)
            select_date_button.pack(side="right")

            # 3. Empacota o Campo de Data à DIREITA (fixo)
            date_display_entry.pack(side="right", padx=(0, 5))

            # 4. Empacota o Nome à ESQUERDA (preenche o espaço)
            name_label.pack(side="left", padx=(0, 10), fill="x", expand=True)

            # --- Configuração final dos comandos ---
            check_button.configure(command=lambda m=matricula: self._toggle_check(m))

            self.widget_map[matricula] = (
                check_button,
                date_display_entry,
                select_date_button,
            )

        # --- Botão Salvar ---
        save_button = ctk.CTkButton(
            self,
            text="Salvar Alterações",
            font=fonts.BUTTON_FONT,
            command=self._on_save,
            fg_color=self.SUCCESS,
            hover_color=self.SUCCESS_HOVER,
            height=40,
        )
        save_button.pack(pady=20)

        # --- CORREÇÃO DO PROBLEMA 2 (Janela atrás) ---
        # Substitua a sequência antiga por esta:
        self.transient(master)  # Define como "filha" da janela principal
        self.lift()  # Puxa a janela para a frente
        self.focus_force()  # Força o foco do teclado para esta janela
        self.grab_set()  # Bloqueia interação com a janela principal

    def _toggle_check(self, matricula):
        """Ativa/desativa a linha quando o checkbox é clicado."""
        check_var = self.check_vars[matricula]
        new_state = not check_var.get()
        check_var.set(new_state)

        check_btn, entry, cal_btn = self.widget_map[matricula]

        if new_state:
            entry.configure(state="normal")
            cal_btn.configure(state="normal")
            if self.img_checked:  # Só troca a imagem se ela foi carregada
                check_btn.configure(image=self.img_checked)
        else:
            entry.configure(state="disabled")
            cal_btn.configure(state="disabled")
            if self.img_unchecked:  # Só troca a imagem se ela foi carregada
                check_btn.configure(image=self.img_unchecked)

    def _format_date(self, var):
        if not self._trace_active:
            return

        current_text = var.get()
        cleaned_text = "".join(filter(str.isdigit, current_text))
        cleaned_text = cleaned_text[:8]

        formatted_text = ""
        if len(cleaned_text) > 4:
            formatted_text = (
                f"{cleaned_text[:2]}/{cleaned_text[2:4]}/{cleaned_text[4:]}"
            )
        elif len(cleaned_text) > 2:
            formatted_text = f"{cleaned_text[:2]}/{cleaned_text[2:]}"
        else:
            formatted_text = cleaned_text

        self._trace_active = False
        var.set(formatted_text)
        self._trace_active = True

    def _open_calendar(self, string_var_to_update):
        def update_var_callback(selected_date_obj):
            string_var_to_update.set(selected_date_obj.strftime("%d/%m/%Y"))

        initial_date = None
        if string_var_to_update.get():
            try:
                initial_date = datetime.strptime(
                    string_var_to_update.get(), "%d/%m/%Y"
                ).date()
            except ValueError:
                pass

        CTkCalendar(self, current_date=initial_date, callback=update_var_callback)

    def _on_save(self):
        """
        Salva APENAS os colaboradores que foram marcados no checkbox.
        """
        updates = {}
        has_checked_item = False

        for matricula, check_var in self.check_vars.items():
            # Se o checkbox estiver marcado
            if check_var.get() is True:
                has_checked_item = True
                data_str = self.date_vars[matricula].get()

                if not data_str:
                    messagebox.showerror(
                        "Erro de Validação",
                        f"O campo de data para {matricula} está vazio.",
                        parent=self,
                    )
                    return
                try:
                    # Converte de DD/MM/AAAA para AAAA-MM-DD
                    data_obj = datetime.strptime(data_str, "%d/%m/%Y").date()
                    updates[matricula] = data_obj.strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Erro de Validação",
                        f"Formato de data inválido para {matricula}. Use DD/MM/AAAA.",
                        parent=self,
                    )
                    return

        if not has_checked_item:
            messagebox.showwarning(
                "Nenhuma Alteração",
                "Você não marcou nenhum colaborador para alterar a data.",
                parent=self,
            )
            return

        self.save_callback(updates)  # Chama o callback com o dict de atualizações
        self.destroy()
