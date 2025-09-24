import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import bcrypt

from .ui import WizardApp, LoginScreen, MainMenuScreen, UserRegistrationScreen
from . import utils as util
from . import database as db

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---

def run_escala_wizard(data):
    # (Sua função run_business_logic completa vai aqui, lendo do banco de dados no futuro)
    print("Iniciando a lógica para gerar a escala com os dados:", data)
    return True, "Escala gerada com sucesso (simulação)!"

def run_import_colaboradores():
    filepath = filedialog.askopenfilename(title="Selecione a planilha", filetypes=[("Arquivos Excel", "*.xlsx")])
    if not filepath: return

    required_columns = ["Nome", "Matrícula", "Cargo", "Setor", "Escala", "Tipo de Turno"]
    try:
        df = pd.read_excel(filepath)
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messagebox.showerror("Erro de Importação", f"Colunas obrigatórias faltando:\n\n- {', '.join(missing_columns)}")
            return
        
        sucesso = 0
        falhas = 0
        erros_msg = []

        # Itera sobre cada linha da planilha e tenta adicionar
        for index, row in df.iterrows():
            dados_dict = row.to_dict()
            is_success, message = db.add_colaborador(dados_dict)
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
    # Chama a função do módulo de banco de dados para salvar
    success, message = db.add_colaborador(dados)
    
    if success:
        messagebox.showinfo("Sucesso", message)
    else:
        messagebox.showerror("Erro ao Salvar", message)
    
    return success

# --- CONTROLADOR PRINCIPAL DA APLICAÇÃO ---

# Em src/gerador_escalas/__main__.py, substitua a classe ApplicationController

class ApplicationController:
    def __init__(self, root):
        self.root = root
        self.show_login_screen()

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self._clear_window()
        self.root.title("Login")
        # Passa o novo callback para o registro
        LoginScreen(self.root, 
                    login_callback=self.on_login, 
                    register_callback=self.show_user_registration_screen)

    def on_login(self, username, password):
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            self.show_main_menu()
        else:
            messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.")

    def show_main_menu(self):
        # ... (sem alterações aqui)
        self._clear_window()
        self.root.title("Menu Principal")
        MainMenuScreen(self.root, self.on_main_menu_choice)

    def on_main_menu_choice(self, choice):
        # ... (sem alterações aqui)
        if choice == "gerar_escala":
            self.root.withdraw() 
            wizard_root = tk.Toplevel(self.root)
            wizard_root.protocol("WM_DELETE_WINDOW", lambda: self.on_child_window_close(wizard_root))
            WizardApp(wizard_root, business_logic_callback=run_escala_wizard)
        elif choice == "cadastrar_colaborador":
            self.show_cadastro_screen()

    def on_child_window_close(self, window):
        # ... (sem alterações aqui)
        window.destroy()
        self.root.deiconify()

    def show_cadastro_screen(self):
        # ... (sem alterações aqui)
        self._clear_window()
        self.root.title("Gestão de Colaboradores")
        CadastroScreen(self.root, self.on_cadastro_choice)

    def on_cadastro_choice(self, choice):
        # ... (sem alterações aqui)
        if choice == "importar":
            run_import_colaboradores()
        elif choice == "manual":
            self.show_cadastro_manual_screen()
    
    def show_cadastro_manual_screen(self):
        # ... (sem alterações aqui)
        self._clear_window()
        self.root.title("Cadastro Manual de Colaborador")
        CadastroManualScreen(self.root, 
                             save_callback=self.on_save_colaborador,
                             back_callback=self.show_main_menu)

    def on_save_colaborador(self, dados):
        # ... (sem alterações aqui)
        success = run_save_colaborador(dados)
        if success:
            self.show_cadastro_manual_screen()

    # --- NOVAS FUNÇÕES PARA CADASTRO DE USUÁRIO ---
    def show_user_registration_screen(self):
        self._clear_window()
        self.root.title("Cadastro de Usuário")
        UserRegistrationScreen(self.root,
                               save_callback=self.on_save_user,
                               back_callback=self.show_login_screen)

    def on_save_user(self, data):
        # Validações antes de tentar salvar
        username = data['username']
        password = data['password']
        confirm_password = data['confirm_password']
        role = data['role']

        if not username or not password:
            messagebox.showwarning("Campos Vazios", "Usuário e Senha são obrigatórios.", parent=self.root)
            return
        
        if password != confirm_password:
            messagebox.showerror("Erro de Senha", "As senhas não coincidem.", parent=self.root)
            return

        # Chama a função do banco de dados para adicionar o usuário
        success, message = db.add_user(username, password, role)
        
        if success:
            messagebox.showinfo("Sucesso", message, parent=self.root)
            self.show_login_screen() # Volta para o login após o sucesso
        else:
            messagebox.showerror("Erro no Cadastro", message, parent=self.root)

if __name__ == "__main__":
    main_root = tk.Tk()
    app = ApplicationController(main_root)
    main_root.mainloop()