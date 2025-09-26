# src/geradorEscalas/ui/wizard_screen.py

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
import calendar
import os

class WizardApp:
    def __init__(self, root, df_collaborators, business_logic_callback):
        self.root = root
        self.root.title("Assistente de Geração de Escala")
        self.root.geometry("600x550")
        
        self.business_logic_callback = business_logic_callback
        self.current_step = 0
        self.data = {'df_colab_ativos': df_collaborators} # Dados já vêm do banco

        # Variáveis
        self.modelo_var = ctk.StringVar(value="1")
        self.mes_var = ctk.StringVar(value=str(date.today().month))
        self.ano_var = ctk.StringVar(value=str(date.today().year))
        self.sector_vars = {}
        self.absence_combos = {}

        # Layout
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        nav_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=10)
        self.progress_bar = ctk.CTkProgressBar(self.root, mode='indeterminate')
        
        self.back_button = ctk.CTkButton(nav_frame, text="< Voltar", command=self.prev_step, fg_color="#7A7A7A", hover_color="#5E5E5E")
        self.next_button = ctk.CTkButton(nav_frame, text="Avançar >", command=self.next_step)
        self.back_button.pack(side="left")
        self.next_button.pack(side="right")
        
        self.show_step(1)

    def show_step(self, step):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        self.current_step = step
        if step == 1: self._build_step1_folder(self.content_frame)
        elif step == 2: self._build_step2_params(self.content_frame)
        elif step == 3: self._build_step3_sectors(self.content_frame)
        elif step == 4: self._build_step4_absences(self.content_frame)
        elif step == 5: self._build_step5_confirm(self.content_frame)
        self.back_button.configure(state="normal" if step > 1 else "disabled")
        if step == 5: self.next_button.configure(text="✔ Gerar Escala Agora", command=self._run_logic)
        else: self.next_button.configure(text="Avançar >")

    def next_step(self):
        if not self._validate_and_save_step(self.current_step): return
        self.show_step(self.current_step + 1)

    def prev_step(self): self.show_step(self.current_step - 1)

    def _validate_and_save_step(self, step):
        if step == 1:
            if not self.data.get('pasta_destino'):
                messagebox.showwarning("Atenção", "Por favor, selecione a pasta de destino.", parent=self.root); return False
        elif step == 2:
            try:
                self.data.update({'modelo_tipo': self.modelo_var.get(), 'mes': int(self.mes_var.get()), 'ano': int(self.ano_var.get())})
                assert 1 <= self.data['mes'] <= 12 and 1900 < self.data['ano'] < 2100
            except: messagebox.showwarning("Atenção", "Mês ou ano inválido.", parent=self.root); return False
        elif step == 3:
            self.data['setores_selecionados'] = [s for s, v in self.sector_vars.items() if v.get()]
            if not self.data['setores_selecionados']:
                messagebox.showwarning("Atenção", "Selecione pelo menos um setor.", parent=self.root); return False
        elif step == 4:
             self.data['afastados_com_motivo'] = {m: c.get().split(' ')[0] for m, c in self.absence_combos.items() if c.get()}
        return True

    def _run_logic(self):
        for widget in self.root.winfo_children(): widget.pack_forget()
        ctk.CTkLabel(self.root, text="Gerando escala, por favor aguarde...", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=40, anchor="center")
        self.progress_bar.pack(fill='x', padx=40, pady=10, anchor="center")
        self.progress_bar.start()
        self.root.update()
        try:
            success, message = self.business_logic_callback(self.data)
            if success: messagebox.showinfo("Sucesso", message, parent=self.root)
            else: messagebox.showerror("Erro", message, parent=self.root)
        except Exception as e: messagebox.showerror("Erro Crítico", f"Ocorreu um erro inesperado:\n{e}", parent=self.root)
        self.root.destroy()

    def _build_step1_folder(self, container):
        step_content = ctk.CTkFrame(container, fg_color="transparent"); step_content.pack(expand=True)
        ctk.CTkLabel(step_content, text="Passo 1: Selecione a Pasta de Destino", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(step_content, text="Escolha a pasta onde a planilha da escala será salva.").pack(pady=(0, 20))
        folder_label = ctk.CTkLabel(step_content, text=self.data.get('pasta_destino', "Nenhuma pasta selecionada."), text_color="gray")
        def select_folder():
            path = filedialog.askdirectory()
            if path: self.data['pasta_destino'] = path; folder_label.configure(text=path, text_color="white")
        ctk.CTkButton(step_content, text="Selecionar Pasta...", command=select_folder, height=40).pack(fill="x", pady=10)
        folder_label.pack(fill="x", padx=10)

    def _build_step2_params(self, container):
        step_content = ctk.CTkFrame(container, fg_color="transparent"); step_content.pack(expand=True)
        ctk.CTkLabel(step_content, text="Passo 2: Defina os Parâmetros", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))
        m_frame = ctk.CTkFrame(step_content); m_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(m_frame, text="Modelo da Escala").pack(side="left", padx=10)
        ctk.CTkRadioButton(m_frame, text="Misto", variable=self.modelo_var, value="1").pack(side="left", padx=10)
        ctk.CTkRadioButton(m_frame, text="Diarista", variable=self.modelo_var, value="2").pack(side="left", padx=10)
        p_frame = ctk.CTkFrame(step_content); p_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(p_frame, text="Período").pack(side="left", padx=10)
        ctk.CTkLabel(p_frame, text="Mês:").pack(side="left")
        ctk.CTkComboBox(p_frame, variable=self.mes_var, values=[str(i) for i in range(1, 13)], width=70, state="readonly").pack(side="left", padx=5)
        ctk.CTkLabel(p_frame, text="Ano:").pack(side="left", padx=15)
        ctk.CTkEntry(p_frame, textvariable=self.ano_var, width=70).pack(side="left")

    def _build_step3_sectors(self, container):
        ctk.CTkLabel(container, text="Passo 3: Escolha os Setores", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20), anchor="w")
        scroll_frame = ctk.CTkScrollableFrame(container)
        scroll_frame.pack(fill="both", expand=True)
        self.sector_vars = {}
        sectors = self.data['df_colab_ativos']["setor"].dropna().unique()
        for sector in sorted(sectors):
            var = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(scroll_frame, text=sector, variable=var, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=5)
            self.sector_vars[sector] = var

    def _build_step4_absences(self, container):
        ctk.CTkLabel(container, text="Passo 4: Gestão de Afastamentos", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20), anchor="w")
        scroll_frame = ctk.CTkScrollableFrame(container)
        scroll_frame.pack(fill="both", expand=True)
        self.absence_combos = {}
        motivos = ["F - FOLGA", "AF - AFASTADO INSS", "AT - ATESTADO", "HE - HORA EXTRA", "LM - LICENÇA MATERNIDADE", "FE - FÉRIAS", "AFAST"]
        afastados_preview = {}
        mes, ano = self.data['mes'], self.data['ano']
        dias_mes = calendar.monthrange(ano, mes)[1]
        df_colab_ativos = self.data['df_colab_ativos']
        for _, row in df_colab_ativos[df_colab_ativos['periodo_afastamento'].notna()].iterrows():
            periodo = str(row.get("periodo_afastamento", "")).strip()
            if " a " in periodo:
                try:
                    inicio = datetime.strptime(periodo.split(" a ")[0], "%d/%m/%Y")
                    fim = datetime.strptime(periodo.split(" a ")[1], "%d/%m/%Y")
                    if inicio <= datetime(ano, mes, dias_mes) and fim >= datetime(ano, mes, 1):
                        afastados_preview[str(row["matricula"])] = row["nome"]
                except ValueError: continue
        self.data['afastados_preview'] = afastados_preview
        if not afastados_preview:
            ctk.CTkLabel(scroll_frame, text="Nenhum afastamento encontrado para este período.", font=ctk.CTkFont(size=14)).pack(pady=20, padx=10)
        else:
            for matricula, nome in afastados_preview.items():
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=5, padx=10)
                ctk.CTkLabel(row_frame, text=f"{nome}:", width=250, anchor="w").pack(side="left")
                combo = ctk.CTkComboBox(row_frame, values=motivos, state="readonly", width=200)
                combo.pack(side="left", padx=5)
                combo.set("AFAST")
                self.absence_combos[matricula] = combo

    def _build_step5_confirm(self, container):
        step_content = ctk.CTkFrame(container, fg_color="transparent"); step_content.pack(expand=True)
        ctk.CTkLabel(step_content, text="Passo 5: Confirmação Final", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))
        summary_frame = ctk.CTkFrame(step_content, border_width=1); summary_frame.pack(pady=10)
        summary_label = ctk.CTkLabel(summary_frame, text="", justify="left", font=("Courier", 12))
        summary_label.pack(padx=20, pady=20)
        modelo = "Misto" if self.data.get('modelo_tipo') == "1" else "Diarista"
        mes_nome = calendar.month_name[self.data.get('mes', 1)]
        ano = self.data.get('ano')
        setores = "\n    - ".join(self.data.get('setores_selecionados', []))
        summary_text = (f"{'Pasta de Destino:':<20} {self.data.get('pasta_destino', '')}\n"
                        f"{'Modelo:':<20} {modelo}\n"
                        f"{'Período:':<20} {mes_nome.upper()} de {ano}\n\n"
                        f"Setores Selecionados:\n    - {setores}")
        summary_label.configure(text=summary_text)