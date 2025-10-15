import os
import re
import shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import ttk
import bcrypt
import pandas as pd
from PIL import Image
import numpy as np
from . import fonts
import tkfontawesome as fa

# Importa as classes de "view" (que são Frames) e os módulos de apoio
from .ui.views import (
    LoginView,
    MainView,
    UserRegistrationView,
)
from . import database as db
from . import fonts

# --- CONFIGURAÇÕES GLOBAIS ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# --- FUNÇÕES DE LÓGICA DE NEGÓCIO (ISOLADAS) ---
def run_import_colaboradores(parent_window):
    """Lida com a importação e validação da planilha de colaboradores."""
    filepath = filedialog.askopenfilename(
        title="Selecione a planilha com os colaboradores",
        filetypes=[("Arquivos Excel", "*.xlsx")],
    )
    if not filepath:
        return

    required_columns = [
        "Nome",
        "Matrícula",
        "Cargo",
        "Setor",
        "Escala",
        "Tipo de Turno",
    ]
    try:
        df = pd.read_excel(filepath)
        # --- LINHA DE CORREÇÃO ADICIONADA ---
        # Substitui todos os valores NaN (nulos) por None, que vira NULL no SQL
        df = df.replace({np.nan: None})

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            messagebox.showerror(
                "Erro de Importação",
                f"Colunas obrigatórias faltando na planilha:\n\n- {', '.join(missing_columns)}",
                parent=parent_window,
            )
            return

        sucesso, falhas, erros_msg = 0, 0, []
        for index, row in df.iterrows():
            is_success, message = db.add_colaborador(row.to_dict())
            if is_success:
                sucesso += 1
            else:
                falhas += 1
                erros_msg.append(f"Linha {index + 2}: {message}")

        resultado_final = (
            f"{sucesso} colaboradores importados com sucesso!\n{falhas} falhas."
        )
        if falhas > 0:
            resultado_final += "\n\nDetalhes dos erros:\n" + "\n".join(erros_msg)

        messagebox.showinfo(
            "Importação Concluída", resultado_final, parent=parent_window
        )
    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Ocorreu um erro ao ler ou processar a planilha: {e}",
            parent=parent_window,
        )


def run_save_colaborador(dados_colaborador):
    pass

APP_VERSION = "1.0.0"

# --- CONTROLADOR PRINCIPAL / JANELA DA APLICAÇÃO ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()   
             
        style = ttk.Style()
        style.theme_use("clam")
        fonts.init_fonts()

        try:
            font_path = os.path.join(
                os.path.dirname(__file__), "assets", "fonts", "fa-solid.otf"
            )
            fa.set_font_path(font_path)
            print("Fonte FontAwesome carregada com sucesso.")
        except Exception as e:
            print(f"ERRO: Não foi possível carregar a fonte FontAwesome: {e}")
            print("Os ícones podem não ser exibidos corretamente.")

        self.title("Acesso ao Sistema")
        self.geometry("400x500")  # Tamanho fixo e menor para o login
        self.resizable(False, False)  # A tela de login não deve ser redimensionável
        self.center_window()  # Nova função para centralizar a janela
        self.protocol("WM_DELETE_WINDOW", self.quit)

        self.current_view = None
        self.show_login_view()
        self.current_user_info = None

    def center_window(self):
        """Centraliza a janela atual no meio da tela."""
        self.update_idletasks()  # Garante que as dimensões da janela estejam atualizadas
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def on_login(self, username, password):
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(
            password.encode("utf-8"), user["password_hash"].encode("utf-8")
        ):
            self.state("zoomed")
            self.geometry("1280x720")
            self.resizable(True, True)
            self.center_window()
            self.current_user_info = user
            self.show_main_view()
        else:
            messagebox.showerror(
                "Falha no Login", "Usuário ou senha inválidos.", parent=self
            )

    def show_main_view(self):
        self.title(f"Gerador de Escalas - Painel Principal - v{APP_VERSION}")
        if self.current_user_info:
            self._show_view(
                MainView, 
                app_controller=self, 
                user_data=self.current_user_info,
                app_version=APP_VERSION # <-- Passa a versão para a MainView
            )
        else:
            messagebox.showerror(
                "Erro de Acesso", "Não foi possível carregar os dados do usuário."
            )
            self.show_login_view()

    def logout(self):
        self.current_user_info = None  # Limpa o usuário ao sair
        self.geometry("400x500")
        self.resizable(False, False)
        self.show_login_view()

    def show_login_view(self):
        """Prepara e exibe a tela de login inicial."""
        self.title("Acesso ao Sistema")
        self._show_view(
            LoginView,
            login_callback=self.on_login,
            register_callback=self.show_registration_view,
        )

    def _show_view(self, ViewClass, *args, **kwargs):
        if self.current_view:
            self.current_view.destroy()

        # Agora, o método apenas cria a view com os argumentos que recebeu.
        self.current_view = ViewClass(self, *args, **kwargs)
        self.current_view.pack(expand=True, fill="both")

    def show_registration_view(self):
        self.center_window() 
        reg_window = ctk.CTkToplevel(self)
        reg_window.title("Cadastro de Novo Usuário")  # Define o título da janela
        reg_window.geometry("400x500")  # Define a largura x altura
        reg_window.resizable(False, False)  # Impede que o usuário redimensione
    
        view = UserRegistrationView(
            reg_window,
            save_callback=lambda data, win=reg_window: self.on_save_user(data, win),
            back_callback=reg_window.destroy,
        )
        view.pack(expand=True, fill="both")

        reg_window.transient(self)
        reg_window.grab_set()
        reg_window.focus()
        
    def on_save_colaborador(self, dados, matricula_original=None):
        """
        Salva um novo colaborador ou atualiza um existente.
        """
        if matricula_original:  # Modo de Edição
            # Remove a matrícula dos 'dados' se ela existir, pois não deve ser alterada
            dados.pop("matricula", None)
            success, message = db.update_collaborator(matricula_original, dados)
        else:  # Modo de Adição
            success, message = db.add_colaborador(dados)

        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            # Após salvar, atualiza e volta para a tela de gerenciamento
            if isinstance(self.current_view, MainView):
                self.current_view.show_colaboradores_view()
        else:
            messagebox.showerror("Erro ao Salvar", message, parent=self)

    def on_save_user(self, data, window_to_close):
        """--- REFATORADO: Lógica unificada para salvar usuário com ou sem foto ---"""
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        role = data.get("role")
        original_photo_path = data.get("photo_path")

        # --- 1. VALIDAÇÃO DO FORMATO DO NOME DE USUÁRIO (NICKNAME) ---
        # Permite apenas letras (a-z, A-Z), números (0-9), underscore (_) e hífen (-).
        if not re.match("^[a-zA-Z0-9_-]+$", username):
            messagebox.showerror(
                "Nome de Usuário Inválido",
                "O nome de usuário deve conter apenas letras (sem acentos), números, underscore (_) ou hífen (-). Nenhum espaço é permitido.",
                parent=window_to_close,
            )
            return

        if not username or not password:
            messagebox.showwarning(
                "Campos Vazios",
                "Usuário e Senha são obrigatórios.",
                parent=window_to_close,
            )
            return

        if password != confirm_password:
            messagebox.showerror(
                "Erro de Senha", "As senhas não coincidem.", parent=window_to_close
            )
            return

        db_photo_path = None
        if original_photo_path:
            profile_pics_dir = "src/geradorEscalas/assets/user_profiles"
            os.makedirs(profile_pics_dir, exist_ok=True)
            file_extension = os.path.splitext(original_photo_path)[1]
            new_filename = f"{username.lower()}{file_extension}"
            destination_path = os.path.join(profile_pics_dir, new_filename)
            try:
                shutil.copy(original_photo_path, destination_path)
                db_photo_path = destination_path
            except Exception as e:
                messagebox.showerror(
                    "Erro ao Salvar Foto",
                    f"Não foi possível salvar a imagem: {e}",
                    parent=window_to_close,
                )
                return
            
        role_padrao = "user"
        success, message = db.add_user(
            username, password, role_padrao, photo_path=db_photo_path
        )

        if success:
            messagebox.showinfo("Sucesso", message, parent=window_to_close)
            window_to_close.destroy()
        else:
            messagebox.showerror("Erro no Cadastro", message, parent=window_to_close)

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
        """Abre a tela de cadastro/edição manual diretamente."""
        # Esta função agora usa o _show_view para trocar o conteúdo da MainView
        if isinstance(self.current_view, MainView):
            self.current_view.show_cadastro_manual_view(matricula_para_editar=matricula_para_editar)

    def on_import_colaboradores(self):
        """
        Lida com a importação, validação, salva os registros válidos
        e move os inválidos para a tela de gerenciamento para correção.
        """
        filepath = filedialog.askopenfilename(
            title="Selecione a planilha com os colaboradores",
            filetypes=[("Arquivos Excel", "*.xlsx")],
        )
        if not filepath:
            return

        # Colunas obrigatórias no arquivo Excel
        required_file_columns = [
            "Nome",
            "Matrícula",
            "Cargo",
            "Setor",
            "Escala",
            "Tipo de Turno",
        ]
        # Colunas obrigatórias para um registro ser considerado válido no BD
        required_db_fields = ["Nome", "Matrícula"]

        try:
            # Força as colunas esperadas a serem lidas como texto (string)
            tipos_de_dados = {
                "Nome": str,
                "Matrícula": str,
                "Cargo": str,
                "Setor": str,
                "Escala": str,
                "Tipo de Turno": str,
            }
            df = pd.read_excel(filepath, dtype=tipos_de_dados)
            # Limpa os valores nulos do Pandas para None do Python
            df = df.replace({np.nan: None})

            # 1. Validação Estrutural (Verifica se as colunas existem no arquivo)
            missing_cols = [
                col for col in required_file_columns if col not in df.columns
            ]
            if missing_cols:
                messagebox.showerror(
                    "Erro de Importação",
                    f"A planilha não pode ser importada.\nColunas obrigatórias faltando:\n\n- {', '.join(missing_cols)}",
                    parent=self,
                )
                return

            valid_rows = []
            invalid_rows = []

            # 2. Separa as linhas em válidas e inválidas
            for index, row in df.iterrows():
                # Verifica se os campos obrigatórios da linha têm conteúdo
                is_valid = all(
                    row.get(col) and str(row.get(col)).strip() not in ["", "None"]
                    for col in required_db_fields
                )
                if is_valid:
                    valid_rows.append(row.to_dict())
                else:
                    invalid_rows.append(row.to_dict())

            # 3. Insere as linhas válidas no banco de dados
            sucesso, falhas = 0, 0
            for row_data in valid_rows:
                is_success, _ = db.add_colaborador(row_data)
                if is_success:
                    sucesso += 1
                else:
                    falhas += 1

            # 4. Prepara a mensagem de resumo
            info_message = f"{sucesso} colaboradores válidos importados com sucesso."
            if falhas > 0:
                info_message += f"\n{falhas} falharam (ex: matrículas duplicadas)."

            # 5. Se houver linhas inválidas, navega para a tela de gerenciamento com elas
            if invalid_rows:
                info_message += f"\n\n{len(invalid_rows)} colaboradores com dados faltantes foram carregados na tabela para sua revisão."
                messagebox.showinfo("Importação Parcial", info_message, parent=self)
                # Navega para a tela de colaboradores, passando apenas os inválidos
                if isinstance(self.current_view, MainView):
                    self.current_view.show_colaboradores_view(invalid_rows=invalid_rows)
            else:
                messagebox.showinfo("Importação Concluída", info_message, parent=self)
                # Se tudo estiver ok, apenas atualiza a tabela com todos os dados do banco
                if isinstance(self.current_view, MainView):
                    self.current_view.show_colaboradores_view()

        except Exception as e:
            messagebox.showerror(
                "Erro", f"Ocorreu um erro ao processar a planilha: {e}", parent=self
            )

    def on_delete_collaborators(self, matriculas):
        """Deleta múltiplos colaboradores e atualiza a tabela."""
        success, message = db.delete_collaborators_by_matriculas(matriculas)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self)
            if isinstance(self.current_view, MainView):
                self.current_view.show_colaboradores_view()
        else:
            messagebox.showerror("Erro", message, parent=self)

    def show_edicao_lote_view(self, dados_selecionados):
        """Abre a tela de edição em lote diretamente."""
        if isinstance(self.current_view, MainView):
            self.current_view.show_edicao_lote_view(dados_selecionados)

    def on_batch_update(self, matriculas, changes):
        """
        Recebe um dicionário de mudanças e aplica cada uma em lote.
        Ex: changes = {'setor': 'UTI', 'cargo': 'ENFERMEIRO JR'}
        """
        for field, new_value in changes.items():
            success, message = db.batch_update_collaborators(
                matriculas, field, new_value
            )
            if not success:
                messagebox.showerror(
                    "Erro na Atualização em Lote", message, parent=self
                )
                return  # Interrompe em caso de erro

        messagebox.showinfo(
            "Sucesso",
            f"{len(matriculas)} colaborador(es) atualizado(s) com sucesso!",
            parent=self,
        )

        # Volta para a tela de gerenciamento atualizada
        if isinstance(self.current_view, MainView):
            self.current_view.show_colaboradores_view()

    def on_save_escala_historico(self, dados_escala, mes, ano):
        """Chama a função do banco de dados para salvar a escala e exibe o resultado."""
        success, message = db.salvar_escala_no_historico(dados_escala, ano, mes)
        if success:
            messagebox.showinfo("Sucesso", message, parent=self.current_view)
        else:
            messagebox.showerror("Erro", message, parent=self.current_view)


if __name__ == "__main__":
    app = App()
    app.mainloop()
