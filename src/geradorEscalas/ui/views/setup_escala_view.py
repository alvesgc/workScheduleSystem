from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime
from ... import fonts
from ..widgets.ctk_calendar import CTkCalendar # 1. Importa o nosso CTkCalendar

class SetupEscalaView(ctk.CTkToplevel):
    def __init__(self, master, colaboradores, save_callback):
        super().__init__(master)
        self.save_callback = save_callback

        self.title("Configuração Inicial de Escalas")
        self.geometry("600x450") # Ajustei o tamanho novamente
        self.resizable(False, False)
        
        self.colaboradores = colaboradores
        self.date_widgets = {} # Dicionário para guardar os widgets de entrada de data

        ctk.CTkLabel(self, text="Primeira Geração de Escala", font=fonts.TITULO_SECAO).pack(pady=10)
        ctk.CTkLabel(self, text="Selecione uma data de referência para o início do ciclo de cada colaborador.", justify="left").pack(pady=5, padx=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(expand=True, fill="both", padx=20, pady=10)

        for colab in self.colaboradores:
            nome = colab.get('nome')
            matricula = colab.get('matricula')
            
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8, padx=5)
            
            ctk.CTkLabel(row_frame, text=f"{nome}:", width=300, anchor="w", font=fonts.LABEL_FONT).pack(side="left", padx=(0, 10))

            # 2. Criamos um CTkEntry que será o campo de exibição da data
            date_display_entry = ctk.CTkEntry(row_frame, width=150, placeholder_text="Clique para selecionar", font=fonts.TEXTO_NORMAL)
            date_display_entry.pack(side="left", padx=(0, 5))
            date_display_entry.configure(state="readonly") # Deixa o campo apenas para visualização

            # 3. Adicionamos um botão que irá abrir o calendário pop-up
            select_date_button = ctk.CTkButton(row_frame, text="...", width=30, command=lambda entry=date_display_entry: self._open_calendar(entry))
            select_date_button.pack(side="left")
            
            # Guardamos o entry para poder pegar o valor depois
            self.date_widgets[matricula] = date_display_entry

        save_button = ctk.CTkButton(self, text="Salvar Datas e Continuar", command=self._on_save, height=40)
        save_button.pack(pady=20)

        self.transient(master)
        self.grab_set()
        self.focus()

    def _open_calendar(self, date_display_entry):
        """Abre a janela do calendário e atualiza o campo de exibição com a data selecionada."""
        def update_entry_callback(selected_date_obj):
            date_display_entry.configure(state="normal") # Temporariamente editável para atualizar
            date_display_entry.delete(0, ctk.END)
            date_display_entry.insert(0, selected_date_obj.strftime('%d/%m/%Y'))
            date_display_entry.configure(state="readonly") # Volta para somente leitura

        # Tenta pegar a data atual do entry para inicializar o calendário
        current_text = date_display_entry.get()
        initial_date = None
        if current_text:
            try:
                initial_date = datetime.strptime(current_text, '%d/%m/%Y').date()
            except ValueError:
                pass # Se o formato for inválido, inicia com a data atual

        calendar_popup = CTkCalendar(self, current_date=initial_date, callback=update_entry_callback)
        # O self.wait_window(calendar_popup) não é necessário aqui
        # porque o callback já cuida da atualização.

    def _on_save(self):
        """Coleta as datas formatadas do campo de exibição e chama o callback."""
        updates = {}
        for matricula, entry_widget in self.date_widgets.items():
            data_str = entry_widget.get()
            if not data_str:
                messagebox.showerror("Erro de Validação", "Todos os campos de data devem ser preenchidos.", parent=self)
                return
            try:
                # Converte para AAAA-MM-DD para o banco de dados
                data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
                updates[matricula] = data_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erro de Validação", f"Formato de data inválido para {matricula}. Use DD/MM/AAAA.", parent=self)
                return
        
        self.save_callback(updates)
        self.destroy()