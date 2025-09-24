
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import os
import calendar
import pandas as pd
from datetime import date, datetime

class WizardApp:
    def __init__(self, root, business_logic_callback):
        self.root = root
        self.root.title("Gerador de Escalas Assistente")
        self.root.geometry("600x550") # Aumentei um pouco a altura para conforto
        self.root.resizable(False, False)
        self.root.configure(bg='white')

        self.business_logic_callback = business_logic_callback
        self.current_step = 0
        self.data = {}

        # Variáveis Tkinter
        self.modelo_var = tk.StringVar(value="1")
        self.mes_var = tk.StringVar(value=str(date.today().month))
        self.ano_var = tk.StringVar(value=str(date.today().year))
        self.sector_vars = {}
        self.absence_combos = {}

        # Estilos
        style = ttk.Style(self.root)
        style.theme_use('vista')
        style.configure('TLabel', background='white')
        style.configure('TFrame', background='white')
        style.configure('TRadiobutton', background='white')
        style.configure('TCheckbutton', background='white')
        style.configure('Bold.TLabel', font=("Helvetica", 16, "bold"), background='white')
        style.configure('Header.TLabel', font=("Helvetica", 10), background='white')
        style.configure('TLabelframe', background='white', borderwidth=1)
        style.configure('TLabelframe.Label', background='white', font=("Helvetica", 9, "italic"))

        # --- Frames Principais ---
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        nav_frame = ttk.Frame(self.root, padding="0 10 10 10")
        nav_frame.pack(fill="x")
        
        self.progress_bar = ttk.Progressbar(self.root, mode='indeterminate')
        
        self.back_button = ttk.Button(nav_frame, text="< Voltar", command=self.prev_step)
        self.next_button = ttk.Button(nav_frame, text="Avançar >", command=self.next_step)
        self.back_button.pack(side="left")
        self.next_button.pack(side="right")
        
        self.show_step(1)

    def show_step(self, step):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_step = step
        if step == 1: self._build_step1_files(self.content_frame)
        elif step == 2: self._build_step2_params(self.content_frame)
        elif step == 3: self._build_step3_sectors(self.content_frame)
        elif step == 4: self._build_step4_absences(self.content_frame)
        elif step == 5: self._build_step5_confirm(self.content_frame)
        self.back_button.config(state="normal" if step > 1 else "disabled")
        if step == 5: self.next_button.config(text="✔ Gerar Escala Agora", command=self._run_logic)
        else: self.next_button.config(text="Avançar >", command=self.next_step)

    def next_step(self):
        if not self._validate_and_save_step(self.current_step): return
        next_step_number = self.current_step + 1
        if next_step_number == 3:
            if not self._load_data_for_next_step(): return
        self.show_step(next_step_number)

    def prev_step(self):
        self.show_step(self.current_step - 1)

    def _validate_and_save_step(self, step):
        # ... (lógica de validação e salvamento, sem alterações) ...
        if step == 1:
            if not self.data.get('caminho_modelo') or not self.data.get('pasta_destino'):
                messagebox.showwarning("Atenção", "Selecione o arquivo base e a pasta de destino.", parent=self.root); return False
        elif step == 2:
            try:
                self.data['modelo_tipo'] = self.modelo_var.get()
                self.data['mes'] = int(self.mes_var.get())
                self.data['ano'] = int(self.ano_var.get())
                assert 1 <= self.data['mes'] <= 12 and 1900 < self.data['ano'] < 2100
            except: messagebox.showwarning("Atenção", "Mês ou ano inválido.", parent=self.root); return False
        elif step == 3:
            self.data['setores_selecionados'] = [s for s, v in self.sector_vars.items() if v.get()]
            if not self.data['setores_selecionados']:
                messagebox.showwarning("Atenção", "Selecione pelo menos um setor.", parent=self.root); return False
        elif step == 4:
             self.data['afastados_com_motivo'] = {m: c.get().split(' ')[0] for m, c in self.absence_combos.items() if c.get()}
        return True

    def _load_data_for_next_step(self):
        try:
            df = pd.read_excel(self.data['caminho_modelo'], sheet_name="Cadastro_Colaboradores")
            self.data['df_colab_ativos'] = df[df["Ativo?"].str.upper() == "SIM"].copy()
            return True
        except Exception as e:
            messagebox.showerror("Erro ao Ler Excel", f"Não foi possível carregar os dados da planilha.\n\nErro: {e}", parent=self.root)
            return False

    def _run_logic(self):
        for widget in self.root.winfo_children(): widget.pack_forget()
        ttk.Label(self.root, text="Gerando escala, por favor aguarde...", style='Bold.TLabel', font=("Helvetica", 12)).pack(pady=40, anchor="center")
        self.progress_bar.pack(fill='x', padx=40, pady=10, anchor="center")
        self.progress_bar.start(10)
        self.root.update()
        try:
            success, message = self.business_logic_callback(self.data)
            if success: messagebox.showinfo("Sucesso", message, parent=self.root)
            else: messagebox.showerror("Erro", message, parent=self.root)
        except Exception as e: messagebox.showerror("Erro Crítico", f"Ocorreu um erro inesperado:\n{e}", parent=self.root)
        self.root.destroy()

    def _build_step1_files(self, container):
        step_content = ttk.Frame(container)
        step_content.pack(expand=True) # Centraliza verticalmente

        ttk.Label(step_content, text="Passo 1: Selecione os Arquivos", style='Bold.TLabel').pack(pady=(0, 5))
        ttk.Label(step_content, text="Selecione a planilha Excel e a pasta onde o arquivo final será salvo.", style='Header.TLabel').pack()
        ttk.Separator(step_content, orient='horizontal').pack(fill='x', pady=20, padx=5)

        file_label = ttk.Label(step_content, text=os.path.basename(self.data.get('caminho_modelo', "Nenhum arquivo selecionado.")))
        folder_label = ttk.Label(step_content, text=self.data.get('pasta_destino', "Nenhuma pasta selecionada."))

        def select_file():
            path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
            if path: self.data['caminho_modelo'] = path; file_label.config(text=os.path.basename(path))
        def select_folder():
            path = filedialog.askdirectory()
            if path: self.data['pasta_destino'] = path; folder_label.config(text=path)

        files_frame = ttk.LabelFrame(step_content, text="Arquivos Necessários", padding=15)
        files_frame.pack(pady=10)
        ttk.Button(files_frame, text="Selecionar Arquivo Base...", command=select_file).pack(fill="x", pady=5)
        file_label.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(files_frame, text="Selecionar Pasta de Destino...", command=select_folder).pack(fill="x", pady=5)
        folder_label.pack(fill="x", padx=10)

    def _build_step2_params(self, container):
        step_content = ttk.Frame(container)
        step_content.pack(expand=True)
        ttk.Label(step_content, text="Passo 2: Defina os Parâmetros", style='Bold.TLabel').pack(pady=(0, 5))
        ttk.Label(step_content, text="Escolha o modelo de escala e o período desejado.", style='Header.TLabel').pack()
        ttk.Separator(step_content, orient='horizontal').pack(fill='x', pady=20, padx=5)

        m_frame = ttk.LabelFrame(step_content, text="Modelo da Escala", padding=15)
        m_frame.pack(fill="x", pady=10)
        ttk.Radiobutton(m_frame, text="Misto", variable=self.modelo_var, value="1").pack(side="left", padx=10)
        ttk.Radiobutton(m_frame, text="Diarista", variable=self.modelo_var, value="2").pack(side="left", padx=10)
        
        p_frame = ttk.LabelFrame(step_content, text="Período", padding=15)
        p_frame.pack(fill="x", pady=10)
        ttk.Label(p_frame, text="Mês:").pack(side="left", padx=5)
        ttk.Combobox(p_frame, textvariable=self.mes_var, values=[str(i) for i in range(1, 13)], width=5, state="readonly").pack(side="left")
        ttk.Label(p_frame, text="Ano:").pack(side="left", padx=15)
        ttk.Entry(p_frame, textvariable=self.ano_var, width=7).pack(side="left")

    def _build_step3_sectors(self, container):
        ttk.Label(container, text="Passo 3: Escolha os Setores", style='Bold.TLabel').pack(pady=(0, 5), anchor="w")
        ttk.Label(container, text="Marque as caixas dos setores que deseja incluir na escala.", style='Header.TLabel').pack(anchor="w")
        ttk.Separator(container, orient='horizontal').pack(fill='x', pady=15, padx=5)

        canvas_frame = ttk.Frame(container)
        canvas_frame.pack(fill="both", expand=True) # Frame para a lista se expandir
        canvas = tk.Canvas(canvas_frame, borderwidth=0, highlightthickness=0, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.sector_vars = {}
        sectors = self.data['df_colab_ativos']["Setor"].dropna().unique()
        for sector in sorted(sectors):
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(scrollable_frame, text=sector, variable=var)
            cb.pack(anchor="w", padx=10, pady=5)
            self.sector_vars[sector] = var
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_step4_absences(self, container):
        ttk.Label(container, text="Passo 4: Gestão de Afastamentos", style='Bold.TLabel').pack(pady=(0, 5), anchor="w")
        ttk.Label(container, text="Para cada colaborador, selecione o motivo do afastamento.", style='Header.TLabel').pack(anchor="w")
        ttk.Separator(container, orient='horizontal').pack(fill='x', pady=15, padx=5)

        canvas_frame = ttk.Frame(container)
        canvas_frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(canvas_frame, borderwidth=0, highlightthickness=0, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.absence_combos = {}
        motivos = ["F - FOLGA", "AF - AFASTADO INSS", "AT - ATESTADO", "HE - HORA EXTRA", "LM - LICENÇA MATERNIDADE", "FE - FÉRIAS", "AFAST"]
        
        afastados_preview = {}
        mes, ano = self.data['mes'], self.data['ano']
        dias_mes = calendar.monthrange(ano, mes)[1]
        for _, row in self.data['df_colab_ativos'].iterrows():
            periodo = str(row.get("Período de Afastamento", "")).strip()
            if " a " in periodo:
                try:
                    inicio = datetime.strptime(periodo.split(" a ")[0], "%d/%m/%Y")
                    fim = datetime.strptime(periodo.split(" a ")[1], "%d/%m/%Y")
                    if inicio <= datetime(ano, mes, dias_mes) and fim >= datetime(ano, mes, 1):
                        afastados_preview[str(row["Matrícula"])] = row["Nome"]
                except ValueError: continue
        self.data['afastados_preview'] = afastados_preview
        
        if not afastados_preview:
            ttk.Label(scrollable_frame, text="Nenhum afastamento encontrado para este período.").pack(pady=20, padx=10)
        else:
            for matricula, nome in afastados_preview.items():
                row_frame = ttk.Frame(scrollable_frame)
                row_frame.pack(fill="x", pady=5, padx=10)
                ttk.Label(row_frame, text=f"{nome}:", width=35).pack(side="left")
                combo = ttk.Combobox(row_frame, values=motivos, state="readonly", width=25)
                combo.pack(side="left", padx=5)
                combo.set("AFAST")
                self.absence_combos[matricula] = combo

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
            
    def _build_step5_confirm(self, container):
        step_content = ttk.Frame(container)
        step_content.pack(expand=True)
        ttk.Label(step_content, text="Passo 5: Confirmação Final", style='Bold.TLabel').pack(pady=(0, 5))
        ttk.Label(step_content, text="Revise todas as configurações antes de gerar a escala.", style='Header.TLabel').pack()
        ttk.Separator(step_content, orient='horizontal').pack(fill='x', pady=20, padx=5)

        summary_frame = ttk.LabelFrame(step_content, text="Resumo da Configuração", padding=20)
        summary_frame.pack(pady=10)
        summary_label = ttk.Label(summary_frame, text="", wraplength=550, justify="left", font=("Courier", 10))
        summary_label.pack()
        
        modelo = "Misto" if self.data.get('modelo_tipo') == "1" else "Diarista"
        mes_nome = calendar.month_name[self.data.get('mes', 1)]
        ano = self.data.get('ano')
        setores = "\n    - ".join(self.data.get('setores_selecionados', []))
        summary_text = (
            f"{'Arquivo Base:':<20} {os.path.basename(self.data.get('caminho_modelo', ''))}\n"
            f"{'Pasta de Destino:':<20} {self.data.get('pasta_destino', '')}\n"
            f"{'Modelo:':<20} {modelo}\n"
            f"{'Período:':<20} {mes_nome.upper()} de {ano}\n\n"
            f"Setores Selecionados:\n    - {setores}"
        )
        summary_label.config(text=summary_text)