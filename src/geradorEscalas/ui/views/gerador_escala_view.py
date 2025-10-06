import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from ... import fonts
from ..widgets.ctk_calendar import CTkCalendar

class SetupEscalaView(ctk.CTkToplevel):
    def __init__(self, master, colaboradores, save_callback):
        super().__init__(master)
        self.save_callback = save_callback

        self.title("Configuração Inicial de Escalas")
        self.geometry("600x450")
        self.resizable(False, False)
        
        self.colaboradores = colaboradores
        # Dicionário para guardar as StringVars de cada campo de data
        self.date_vars = {} 
        self._trace_active = True # Flag para evitar recursão infinita na formatação

        ctk.CTkLabel(self, text="Primeira Geração de Escala", font=fonts.TITULO_SECAO).pack(pady=10)
        ctk.CTkLabel(self, text="Digite ou selecione uma data de referência para o início do ciclo (DD/MM/AAAA).", justify="left").pack(pady=5, padx=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(expand=True, fill="both", padx=20, pady=10)

        for colab in self.colaboradores:
            nome = colab.get('nome')
            matricula = colab.get('matricula')
            
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8, padx=5)
            
            ctk.CTkLabel(row_frame, text=f"{nome}:", width=300, anchor="w", font=fonts.LABEL_FONT).pack(side="left", padx=(0, 10))

            # Cria uma StringVar para cada campo de data
            date_var = ctk.StringVar()
            # "Observa" a variável. Toda vez que ela for alterada, chama a função _format_date
            date_var.trace_add("write", lambda name, index, mode, var=date_var: self._format_date(var))
            self.date_vars[matricula] = date_var

            # O Entry agora é editável e está conectado à StringVar
            date_display_entry = ctk.CTkEntry(row_frame, width=150, placeholder_text="DD/MM/AAAA", font=fonts.TEXTO_NORMAL, textvariable=date_var)
            date_display_entry.pack(side="left", padx=(0, 5))

            select_date_button = ctk.CTkButton(row_frame, text="...", width=30, command=lambda var=date_var: self._open_calendar(var))
            select_date_button.pack(side="left")

        save_button = ctk.CTkButton(self, text="Salvar Datas e Continuar", command=self._on_save, height=40)
        save_button.pack(pady=20)

        self.transient(master)
        self.grab_set()
        self.focus()

    def _format_date(self, var):
        """Função chamada a cada alteração no texto para auto-formatar a data."""
        if not self._trace_active:
            return

        current_text = var.get()
        cleaned_text = "".join(filter(str.isdigit, current_text))
        
        # Limita o número de dígitos a 8 (DDMMAAAA)
        cleaned_text = cleaned_text[:8]
        
        formatted_text = ""
        if len(cleaned_text) > 4:
            formatted_text = f"{cleaned_text[:2]}/{cleaned_text[2:4]}/{cleaned_text[4:]}"
        elif len(cleaned_text) > 2:
            formatted_text = f"{cleaned_text[:2]}/{cleaned_text[2:]}"
        else:
            formatted_text = cleaned_text

        # Lógica para evitar loop infinito de trace
        self._trace_active = False
        var.set(formatted_text)
        self._trace_active = True

    def _open_calendar(self, string_var_to_update):
        """Abre o calendário e define o valor da StringVar correspondente."""
        def update_var_callback(selected_date_obj):
            string_var_to_update.set(selected_date_obj.strftime('%d/%m/%Y'))

        initial_date = None
        if string_var_to_update.get():
            try:
                initial_date = datetime.strptime(string_var_to_update.get(), '%d/%m/%Y').date()
            except ValueError: pass
        
        CTkCalendar(self, current_date=initial_date, callback=update_var_callback)

    def _on_save(self):
        """Coleta as datas das StringVars e as formata para o banco de dados."""
        updates = {}
        for matricula, var in self.date_vars.items():
            data_str = var.get()
            if not data_str:
                messagebox.showerror("Erro de Validação", "Todos os campos de data devem ser preenchidos.", parent=self)
                return
            try:
                data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
                updates[matricula] = data_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erro de Validação", f"Formato de data inválido para {matricula}. Use DD/MM/AAAA.", parent=self)
                return
        
        self.save_callback(updates)
        self.destroy()