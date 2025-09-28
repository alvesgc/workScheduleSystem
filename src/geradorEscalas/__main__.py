# src/geradorEscalas/__main__.py

import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt
import pandas as pd
from PIL import Image

# Importa as classes de "view" (que são Frames) e os módulos de apoio
from .ui.views import LoginView, MainView, UserRegistrationView, CorrecaoView
from . import database as db
from . import fonts

# --- CONFIGURAÇÕES GLOBAIS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
        self._show_view(MainView, app_controller=self)

    def show_registration_view(self):
        reg_window = ctk.CTkToplevel(self)
        view = UserRegistrationView(reg_window, 
                                    save_callback=lambda data: self.on_save_user(data, reg_window), 
                                    back_callback=reg_window.destroy)
        view.pack(expand=True, fill="both")
        reg_window.transient(self)
        reg_window.grab_set()
    
    def on_save_user(self, data, window_to_close):
        username, password, confirm_password, role = data.values()
        if not username or not password:
            messagebox.showwarning("Campos Vazios", "Usuário e Senha são obrigatórios.", parent=window_to_close)
            return
        if password != confirm_password:
            messagebox.showerror("Erro de Senha", "As senhas não coincidem.", parent=window_to_close)
            return
        success, message = db.add_user(username, password, role)
        if success:
            messagebox.showinfo("Sucesso", message, parent=window_to_close)
            window_to_close.destroy()
        else:
            messagebox.showerror("Erro no Cadastro", message, parent=window_to_close)

    def show_escala_wizard(self):
        messagebox.showinfo("Navegação", "Aqui abriremos o assistente de Gerar Escala.")

    def show_colaboradores_view(self):
        if isinstance(self.current_view, MainView):
            self.current_view.show_colaboradores_view()

    def on_import_colaboradores(self):
        filepath = filedialog.askopenfilename(title="Selecione a planilha", filetypes=[("Arquivos Excel", "*.xlsx")])
        if not filepath: return

        required_columns = ["Nome", "Matrícula", "Setor", "Escala"]
        try:
            df = pd.read_excel(filepath, dtype={'Matrícula': str})
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                messagebox.showerror("Erro de Importação", f"Colunas obrigatórias faltando:\n- {', '.join(missing_cols)}", parent=self)
                return

            corrected_rows = []
            for index, row in df.iterrows():
                is_valid = all(pd.notna(row.get(col)) and str(row.get(col)).strip() != "" for col in required_columns)
                
                if not is_valid:
                    correction_window = CorrecaoView(self, row_data=row.to_dict(), index=index + 2)
                    
                    # --- CORREÇÃO APLICADA AQUI ---
                    # 1. Torna a janela modal, capturando todo o foco.
                    correction_window.grab_set()
                    # 2. Pausa a execução do código até que a janela de correção seja fechada.
                    self.wait_window(correction_window)
                    
                    result = correction_window.result
                    if result == "skip":
                        continue
                    elif result is not None:
                        corrected_rows.append(result)
                else:
                    corrected_rows.append(row.to_dict())

            # Após o loop, insere todos os dados válidos/corrigidos no banco
            sucesso, falhas, erros_msg = 0, 0, []
            for row_data in corrected_rows:
                # Converte o dict de volta para o formato esperado por add_colaborador
                # (Se os nomes das colunas forem diferentes no BD, ajuste aqui)
                is_success, message = db.add_colaborador(row_data)
                if is_success: sucesso += 1
                else: falhas += 1; erros_msg.append(message)
            
            resultado_final = f"{sucesso} colaboradores importados com sucesso!\n{falhas} falhas."
            if falhas > 0:
                resultado_final += "\n\nDetalhes dos erros:\n" + "\n".join(erros_msg)
            messagebox.showinfo("Importação Concluída", resultado_final, parent=self)

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao processar a planilha: {e}", parent=self)
        
    def on_save_colaborador(self, dados):
        success, message = db.add_colaborador(dados)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            if isinstance(self.current_view, MainView):
                self.current_view.show_cadastro_manual_view()
        else:
            messagebox.showerror("Erro ao Salvar", message, parent=self)
    
    def logout(self):
        self.show_login_view()

if __name__ == "__main__":
    app = App()
    app.mainloop()