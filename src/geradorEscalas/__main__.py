import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt
import pandas as pd
from PIL import Image
import numpy as np

# Importa as classes de "view" (que são Frames) e os módulos de apoio
from .ui.views import (
    LoginView, 
    MainView, 
    UserRegistrationView,
    HomeView,
    CadastroView,
    CadastroManualView
)
from . import database as db
from . import fonts

# --- CONFIGURAÇÕES GLOBAIS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO (ISOLADAS) ---
def run_import_colaboradores(parent_window):
    """Lida com a importação e validação da planilha de colaboradores."""
    filepath = filedialog.askopenfilename(
        title="Selecione a planilha com os colaboradores",
        filetypes=[("Arquivos Excel", "*.xlsx")]
    )
    if not filepath:
        return

    required_columns = ["Nome", "Matrícula", "Cargo", "Setor", "Escala", "Tipo de Turno"]
    try:
        df = pd.read_excel(filepath)

        # --- LINHA DE CORREÇÃO ADICIONADA ---
        # Substitui todos os valores NaN (nulos) por None, que vira NULL no SQL
        df = df.replace({np.nan: None})

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messagebox.showerror("Erro de Importação", f"Colunas obrigatórias faltando na planilha:\n\n- {', '.join(missing_columns)}", parent=parent_window)
            return
        
        sucesso, falhas, erros_msg = 0, 0, []
        for index, row in df.iterrows():
            is_success, message = db.add_colaborador(row.to_dict())
            if is_success:
                sucesso += 1
            else:
                falhas += 1
                erros_msg.append(f"Linha {index + 2}: {message}")
        
        resultado_final = f"{sucesso} colaboradores importados com sucesso!\n{falhas} falhas."
        if falhas > 0:
            resultado_final += "\n\nDetalhes dos erros:\n" + "\n".join(erros_msg)
        
        messagebox.showinfo("Importação Concluída", resultado_final, parent=parent_window)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao ler ou processar a planilha: {e}", parent=parent_window)

def run_save_colaborador(dados_colaborador):
    pass
# --- CONTROLADOR PRINCIPAL / JANELA DA APLICAÇÃO ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        fonts.init_fonts()

        self.title("Gerador de Escalas")
        self.state("zoomed")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.current_view = None
        self.show_login_view()

    def _show_view(self, ViewClass, *args, **kwargs):
        """Limpa a janela e exibe uma nova view principal nela."""
        if self.current_view:
            self.current_view.destroy()
        
        self.current_view = ViewClass(self, *args, **kwargs)
        self.current_view.pack(expand=True, fill="both")

    def show_login_view(self):
        self.title("Acesso ao Sistema")
        self._show_view(LoginView, 
                        login_callback=self.on_login, 
                        register_callback=self.show_registration_view)

    def on_login(self, username, password):
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            self.show_main_view()
        else:
            messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.", parent=self)

    def show_main_view(self):
        self.title("Gerador de Escalas - Painel Principal")
        self._show_view(MainView, app_controller=self)

    def show_registration_view(self):
        reg_window = ctk.CTkToplevel(self)
        view = UserRegistrationView(reg_window, 
                                    save_callback=lambda data: self.on_save_user(data, reg_window), 
                                    back_callback=reg_window.destroy)
        view.pack(expand=True, fill="both")
        reg_window.transient(self)
        reg_window.grab_set()
    
    def on_save_colaborador(self, dados, matricula_original=None):
        if matricula_original: # Modo Edição
            # Remove a matrícula dos dados a serem atualizados, pois ela não deve mudar
            dados.pop("matricula", None)
            success, message = db.update_collaborator(matricula_original, dados)
        else: # Modo Adição
            success, message = db.add_colaborador(dados)
        
        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            if isinstance(self.current_view, MainView):
                self.current_view.show_colaboradores_view() # Volta para a lista
        else:
            messagebox.showerror("Erro ao Salvar", message, parent=self)

    # --- Métodos de Navegação chamados pela MainView ---
    def show_home_view(self):
        if isinstance(self.current_view, MainView):
            self.current_view.show_home_view()

    def show_escala_wizard(self):
        if isinstance(self.current_view, MainView):
            self.current_view.show_escala_wizard()

    def show_colaboradores_view(self):
        if isinstance(self.current_view, MainView):
            self.current_view.show_colaboradores_view()

    # --- MÉTODO ADICIONADO ---
    def show_cadastro_manual_view(self, matricula_para_editar=None):
        if isinstance(self.current_view, MainView):
             self.current_view.show_cadastro_manual_view(matricula_para_editar)

    def on_import_colaboradores(self):
        run_import_colaboradores(self)
        if isinstance(self.current_view, MainView) and hasattr(self.current_view.content_frame.winfo_children()[0], 'update_table'):
             self.current_view.content_frame.winfo_children()[0].update_table()

    def on_save_colaborador(self, dados):
        success, message = run_save_colaborador(dados)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            if isinstance(self.current_view, MainView):
                self.current_view.show_colaboradores_view() # Volta para a lista após salvar
        else:
            messagebox.showerror("Erro ao Salvar", message, parent=self)
            
    def on_delete_collaborators(self, matriculas):
        """Deleta múltiplos colaboradores e atualiza a tabela."""
        success, message = db.delete_collaborators_by_matriculas(matriculas)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            if isinstance(self.current_view, MainView):
                 self.current_view.show_colaboradores_view()
        else:
            messagebox.showerror("Erro", message, parent=self)
            
    def show_edicao_lote_view(self, matriculas):
        """Instrui a MainView a mostrar a tela de edição em lote."""
        if isinstance(self.current_view, MainView):
            self.current_view.show_edicao_lote_view(matriculas)
            
    def on_batch_update(self, matriculas, changes):
        """
        Recebe um dicionário de mudanças e aplica cada uma em lote.
        Ex: changes = {'setor': 'UTI', 'cargo': 'ENFERMEIRO JR'}
        """
        for field, new_value in changes.items():
            success, message = db.batch_update_collaborators(matriculas, field, new_value)
            if not success:
                messagebox.showerror("Erro na Atualização em Lote", message, parent=self)
                return # Interrompe em caso de erro

        messagebox.showinfo("Sucesso", f"{len(matriculas)} colaborador(es) atualizado(s) com sucesso!", parent=self)
        
        # Volta para a tela de gerenciamento atualizada
        if isinstance(self.current_view, MainView):
            self.current_view.show_colaboradores_view()
    
    def logout(self):
        self.show_login_view()

if __name__ == "__main__":
    app = App()
    app.mainloop()