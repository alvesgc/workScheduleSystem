import customtkinter as ctk
from tkinter import messagebox

class CadastroManualView(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback):
        super().__init__(master, fg_color="transparent")
        self.save_callback = save_callback
        self.back_callback = back_callback

        self.campos = { "Nome": ctk.StringVar(), "Matrícula": ctk.StringVar(), "Cargo": ctk.StringVar(), "Setor": ctk.StringVar(), "Escala": ctk.StringVar(), "Tipo de Turno": ctk.StringVar(), "Horário Padrão": ctk.StringVar(), "COREN (opcional)": ctk.StringVar(), "Período de Afastamento": ctk.StringVar(value="dd/mm/aaaa a dd/mm/aaaa") }

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Cadastro Manual de Colaborador", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure(1, weight=1)

        for i, (label, var) in enumerate(self.campos.items()):
            ctk.CTkLabel(scrollable_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=20, pady=10)
            
            if label == "Escala":
                entry = ctk.CTkComboBox(scrollable_frame, variable=var, values=["12x36", "Diarista"], state="readonly", height=35)
            elif label == "Tipo de Turno":
                entry = ctk.CTkComboBox(scrollable_frame, variable=var, values=["Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2", "-"], height=35)
            else:
                entry = ctk.CTkEntry(scrollable_frame, textvariable=var, height=35)
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(button_frame, text="Salvar Colaborador", command=self._save, height=45).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(button_frame, text="Voltar", command=self.back_callback, height=45, fg_color="#7A7A7A", hover_color="#5E5E5E").grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _save(self):
        dados = {key: var.get() for key, var in self.campos.items()}
        if not dados["Nome"] or not dados["Matrícula"]:
            messagebox.showwarning("Campo Obrigatório", "Os campos 'Nome' e 'Matrícula' são obrigatórios.", parent=self)
            return
        if "dd/mm/aaaa" in dados["Período de Afastamento"]:
            dados["Período de Afastamento"] = "" # Limpa se o valor padrão não foi alterado
        self.save_callback(dados)