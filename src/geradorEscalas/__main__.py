import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt
import pandas as pd

from .ui.views import (
    LoginWindow, 
    MainWindow, 
    HomeView, 
    UserRegistrationWindow, 
    CadastroView, 
    CadastroManualView
)
from . import database as db
from . import utils as util

# --- CONFIGURAÇÕES GLOBAIS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---

def run_import_colaboradores():
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
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messagebox.showerror("Erro de Importação", f"Colunas obrigatórias faltando na planilha:\n\n- {', '.join(missing_columns)}")
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
        
        messagebox.showinfo("Importação Concluída", resultado_final)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao ler ou processar a planilha: {e}")

def run_save_colaborador(dados):
    """Chama a função do módulo de banco de dados para salvar um colaborador."""
    success, message = db.add_colaborador(dados)
    # A exibição da mensagem será tratada pelo controlador que chamou a função
    return success, message

# --- CONTROLADOR PRINCIPAL DA APLICAÇÃO ---

class ApplicationController:
    def __init__(self):
        self.login_window = None
        self.main_window = None
        self.show_login()

    def show_login(self):
        """Exibe a janela de login inicial."""
        self.login_window = LoginWindow(
            login_callback=self.on_login,
            register_callback=self.show_registration
        )
        self.login_window.mainloop()

    def on_login(self, username, password):
        """Valida as credenciais do usuário e decide o próximo passo."""
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            self.login_window.destroy()  # Fecha a janela de login
            self.show_main_window()      # Abre a janela principal
        else:
            messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.", parent=self.login_window)

    def show_registration(self):
        """Abre a janela de cadastro de usuário sobre a tela de login."""
        reg_window = UserRegistrationWindow(self.login_window, 
                                            save_callback=self.on_save_user, 
                                            back_callback=lambda: reg_window.destroy())
        reg_window.transient(self.login_window) # Faz a janela de registro aparecer na frente
        reg_window.grab_set() # Foco total na janela de registro

    def on_save_user(self, data):
        """Valida e salva um novo usuário no banco de dados."""
        username, password, confirm_password, role = data.values()
        if not username or not password:
            messagebox.showwarning("Campos Vazios", "Usuário e Senha são obrigatórios.", parent=self.login_window)
            return
        if password != confirm_password:
            messagebox.showerror("Erro de Senha", "As senhas não coincidem.", parent=self.login_window)
            return
            
        success, message = db.add_user(username, password, role)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self.login_window)
            # A janela de registro poderia ser fechada aqui se desejado
        else:
            messagebox.showerror("Erro no Cadastro", message, parent=self.login_window)

    def show_main_window(self):
        """Cria e exibe a janela principal da aplicação com a sidebar."""
        nav_callbacks = {
            "home": self.show_home_view,
            "gerar_escala": self.show_escala_wizard,
            "colaboradores": self.show_colaboradores_view,
            "sair": self.logout
        }
        self.main_window = MainWindow(nav_callbacks)
        self.show_home_view() # Exibe a tela Home por padrão
        self.main_window.mainloop()
        
    def show_home_view(self):
        """Exibe a tela Home na área de conteúdo da janela principal."""
        self.main_window.show_view(HomeView, 
                                   gerar_escala_callback=self.show_escala_wizard,
                                   gerenciar_colaboradores_callback=self.show_colaboradores_view)

    def show_escala_wizard(self):
        """Inicia o assistente de geração de escala."""
        messagebox.showinfo("Navegação", "Aqui abriremos o assistente de Gerar Escala.")

    def show_colaboradores_view(self):
        """Exibe a tela de escolha para gerenciamento de colaboradores."""
        self.main_window.show_view(CadastroView,
                                   choice_callback=self.on_cadastro_choice,
                                   back_callback=self.show_home_view)

    def on_cadastro_choice(self, choice):
        """Decide qual tela de cadastro mostrar (manual ou importação)."""
        if choice == "importar":
            run_import_colaboradores()
        elif choice == "manual":
            self.show_cadastro_manual_view()

    def show_cadastro_manual_view(self):
        """Exibe o formulário de cadastro manual de colaborador."""
        self.main_window.show_view(CadastroManualView,
                                   save_callback=self.on_save_colaborador,
                                   back_callback=self.show_colaboradores_view)
    
    def on_save_colaborador(self, dados):
        """Salva um novo colaborador e lida com a resposta."""
        success, message = run_save_colaborador(dados)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self.main_window)
            self.show_cadastro_manual_view() # Recarrega a tela para adicionar outro
        else:
            messagebox.showerror("Erro ao Salvar", message, parent=self.main_window)
    
    def logout(self):
        """Fecha a janela principal e volta para a tela de login."""
        if messagebox.askyesno("Sair", "Tem certeza que deseja sair do sistema?", parent=self.main_window):
            self.main_window.destroy()
            self.show_login()

if __name__ == "__main__":
    app = ApplicationController()