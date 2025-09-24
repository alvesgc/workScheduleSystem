import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import sys
import mysql.connector
import bcrypt

from .ui import WizardApp, LoginScreen, MainMenuScreen
from . import utils as util

# --- CONFIGURAÇÕES DE BANCO DE DADOS ---
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "1234", # <<< MUDE AQUI
    'database': "gerador_escala_db"
}

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---

def run_escala_wizard(data):
    # (Sua função run_business_logic completa vai aqui)
    print("Iniciando a lógica para gerar a escala com os dados:", data)
    return True, "Escala gerada com sucesso (simulação)!"

def run_import_colaboradores():
    filepath = filedialog.askopenfilename(title="Selecione a planilha", filetypes=[("Arquivos Excel", "*.xlsx")])
    if not filepath: return

    required_columns = ["Nome", "Matrícula", "Cargo", "Setor", "Escala", "Tipo de Turno", "Ativo?"]
    try:
        df = pd.read_excel(filepath)
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messagebox.showerror("Erro de Importação", f"Colunas obrigatórias faltando:\n\n- {', '.join(missing_columns)}")
            return
        
        # Lógica para inserir no banco de dados (futuro)
        messagebox.showinfo("Sucesso", f"{len(df)} colaboradores validados com sucesso.")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao ler a planilha: {e}")

def run_save_colaborador(dados):
    # Lógica para salvar um único colaborador no banco de dados (futuro)
    print("Salvando no banco de dados:", dados)
    messagebox.showinfo("Sucesso", f"Colaborador '{dados['Nome']}' salvo com sucesso (simulação).")


# --- CONTROLADOR PRINCIPAL DA APLICAÇÃO ---

class ApplicationController:
    def __init__(self, root):
        self.root = root
        self.show_login_screen()

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self._clear_window()
        self.login_view = LoginScreen(self.root, self.on_login)

    def on_login(self, username, password):
        try:
            conexao = mysql.connector.connect(**DB_CONFIG)
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                print(f"Login bem-sucedido para o usuário: {user['username']} (Role: {user['role']})")
                self.show_main_menu()
            else:
                messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.")

        except mysql.connector.Error as err:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível conectar: {err}")
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def show_main_menu(self):
        self._clear_window()
        self.main_menu_view = MainMenuScreen(self.root, self.on_main_menu_choice)

    def on_main_menu_choice(self, choice):
        if choice == "gerar_escala":
            self.root.withdraw() 
            wizard_root = tk.Toplevel(self.root)
            wizard_root.protocol("WM_DELETE_WINDOW", self.on_wizard_close) # Lida com o fechamento da janela
            WizardApp(wizard_root, business_logic_callback=run_escala_wizard)
            
        elif choice == "cadastrar_colaborador":
            self.show_cadastro_screen()
    
    def on_wizard_close(self):
        # Mostra a janela de menu novamente quando o wizard for fechado
        self.root.deiconify()

    def show_cadastro_screen(self):
        self._clear_window()
        self.cadastro_view = CadastroScreen(self.root, self.on_cadastro_choice)

    def on_cadastro_choice(self, choice):
        if choice == "importar":
            run_import_colaboradores()
        elif choice == "manual":
            self.show_cadastro_manual_screen()
    
    def show_cadastro_manual_screen(self):
        self._clear_window()
        self.cadastro_manual_view = CadastroManualScreen(self.root, 
                                                         save_callback=self.on_save_colaborador,
                                                         back_callback=self.show_main_menu)

    def on_save_colaborador(self, dados):
        run_save_colaborador(dados)
        # Após salvar, volta para a tela de cadastro manual (para adicionar outro)
        self.show_cadastro_manual_screen()


if __name__ == "__main__":
    main_root = tk.Tk()
    app = ApplicationController(main_root)
    main_root.mainloop()