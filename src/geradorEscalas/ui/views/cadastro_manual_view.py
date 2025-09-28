import customtkinter as ctk
from tkinter import messagebox

class CadastroManualView(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback, matricula_para_editar=None):
        super().__init__(master, fg_color="transparent")
        self.save_callback = save_callback
        self.back_callback = back_callback
        self.matricula_para_editar = matricula_para_editar

        if self.matricula_para_editar:
            self.load_data_for_editing()

    def load_data_for_editing(self):
        # Título
        self.title_label.configure(text="Editar Colaborador")
        
        # Busca dados do BD
        data = db.get_collaborator_by_matricula(self.matricula_para_editar)
        if not data:
            messagebox.showerror("Erro", "Colaborador não encontrado.", parent=self)
            self.back_callback()
            return
        
        # Preenche os campos
        self.campos["Nome"].set(data.get("nome", ""))
        self.campos["Matrícula"].set(data.get("matricula", ""))
        # ... preencher todos os outros campos ...

        # Desabilita o campo de matrícula para não ser alterado
        self.matricula_entry.configure(state="disabled")

    def _save(self):
        dados = {key: var.get() for key, var in self.campos.items()}
        # Remove a matrícula dos dados a serem atualizados, pois ela não muda
        if self.matricula_para_editar:
            dados.pop("Matrícula", None)

        self.save_callback(dados, self.matricula_para_editar)