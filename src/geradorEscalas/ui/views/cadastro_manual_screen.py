
import customtkinter as ctk
from tkinter import messagebox

class CadastroManualScreen:
    def __init__(self, root, save_callback, back_callback):
        self.root = root
        self.root.title("Cadastro Manual de Colaborador")
        self.root.geometry("500x600")
        
        self.save_callback = save_callback
        self.back_callback = back_callback

        self.campos = { "Nome": ctk.StringVar(), "Matrícula": ctk.StringVar(), "Cargo": ctk.StringVar(), "Setor": ctk.StringVar(), "Escala": ctk.StringVar(), "Tipo de Turno": ctk.StringVar(), "Horário Padrão": ctk.StringVar(), "COREN (opcional)": ctk.StringVar() }

        main_frame = ctk.CTkFrame(root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        ctk.CTkLabel(main_frame, text="Novo Colaborador", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        for label, var in self.campos.items():
            field_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            field_frame.pack(fill='x', pady=7)
            ctk.CTkLabel(field_frame, text=f"{label}:", width=120, anchor="w").pack(side='left')
            
            if label == "Escala":
                entry = ctk.CTkComboBox(field_frame, variable=var, values=["12x36", "Diarista"], state="readonly", height=35)
            elif label == "Tipo de Turno":
                entry = ctk.CTkComboBox(field_frame, variable=var, values=["Diurno 1", "Diurno 2", "Noturno 1", "Noturno 2", "-"], height=35)
            else:
                entry = ctk.CTkEntry(field_frame, textvariable=var, height=35)
            entry.pack(side='left', fill='x', expand=True)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20, fill='x')
        ctk.CTkButton(button_frame, text="Salvar Colaborador", command=self._save, height=40).pack(side='left', expand=True, padx=(0, 5))
        ctk.CTkButton(button_frame, text="Voltar ao Menu", command=self.back_callback, fg_color="#7A7A7A", hover_color="#5E5E5E").pack(side='left', expand=True, padx=(5, 0))

    def _save(self):
        dados_colaborador = {key: var.get() for key, var in self.campos.items()}
        if not dados_colaborador["Nome"] or not dados_colaborador["Matrícula"]:
            messagebox.showwarning("Campo Obrigatório", "Os campos 'Nome' e 'Matrícula' são obrigatórios.", parent=self.root)
            return
        self.save_callback(dados_colaborador)