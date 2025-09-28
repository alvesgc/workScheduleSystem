import customtkinter as ctk
import pandas as pd
from ... import fonts

class CorrecaoView(ctk.CTkToplevel):
    def __init__(self, master, row_data, index):
        super().__init__(master)

        self.title(f"Revisar Linha {index}")
        self.geometry("500x650")
        self.resizable(False, False)
        self.result = None

        self.campos = {
            "Nome": ctk.StringVar(), "Matrícula": ctk.StringVar(), "Cargo": ctk.StringVar(),
            "Setor": ctk.StringVar(), "Escala": ctk.StringVar(), "Tipo de Turno": ctk.StringVar(),
            "Horário Padrão": ctk.StringVar(), "COREN (opcional)": ctk.StringVar(),
            "Período de Afastamento": ctk.StringVar()
        }
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main_frame, text=f"Corrigir Colaborador (Linha {index})", font=fonts.TITULO_SECAO).grid(row=0, column=0, pady=(0, 10))
        ctk.CTkLabel(main_frame, text="Um ou mais campos obrigatórios estão vazios. Por favor, corrija para continuar.", wraplength=450).grid(row=1, column=0, pady=(0, 20))
        
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.grid(row=2, column=0, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)

        required_fields = ["Nome", "Matrícula", "Setor", "Escala"]

        for i, (label, var) in enumerate(self.campos.items()):
            # --- LÓGICA DE CORREÇÃO DO NaN ---
            original_value = row_data.get(label)
            # Verifica se o valor é nulo ou a string 'NaN' e limpa se for o caso
            clean_value = "" if pd.isna(original_value) or str(original_value).lower() == 'nan' else str(original_value)
            var.set(clean_value)

            ctk.CTkLabel(form_frame, text=f"{label}:", font=fonts.LABEL_FONT).grid(row=i, column=0, sticky="w", padx=20, pady=10)
            entry = ctk.CTkEntry(form_frame, textvariable=var, height=35, font=fonts.TEXTO_NORMAL)
            
            # --- LÓGICA DA BORDA VERMELHA E PLACEHOLDER ---
            if label in required_fields and not var.get():
                entry.configure(border_color="#D63031", placeholder_text="* Campo Obrigatório")

            entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)
        ctk.CTkButton(button_frame, text="Salvar e Continuar", command=self._save).pack(side='left', padx=10)
        ctk.CTkButton(button_frame, text="Pular Colaborador", command=self._skip, fg_color="#7A7A7A").pack(side='left')

    def _save(self):
        self.result = {key: var.get() for key, var in self.campos.items()}
        self.destroy()

    def _skip(self):
        self.result = "skip"
        self.destroy()