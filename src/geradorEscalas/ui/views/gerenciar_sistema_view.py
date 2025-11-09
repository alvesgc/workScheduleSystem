import customtkinter as ctk
import tkfontawesome as fa
from tkinter import messagebox
from datetime import datetime

class GerenciarSistemaView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="#F5F6FA")
        self.app_controller = app_controller
        
        # Cores
        self.PRIMARY = "#0078D7"
        self.SURFACE = "#FFFFFF"
        self.BORDER = "#E1E4E8"
        self.TEXT_PRIMARY = "#1E1E1E"
        self.TEXT_SECONDARY = "#6B6B6B"
        self.DANGER = "#DC2626"
        self.SUCCESS = "#16A34A"
        self.WARNING = "#F59E0B"
        
        # Cores de fundo para badges (versões claras)
        self.SUCCESS_BG = "#D1FAE5"  # Verde claro
        self.PRIMARY_BG = "#DBEAFE"  # Azul claro
        self.DANGER_BG = "#FEE2E2"   # Vermelho claro
        
        self._criar_interface()
        self._carregar_usuarios()
    
    def _criar_interface(self):
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 24))
        
        # Título com ícone
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        icon_admin = fa.icon_to_image("user-shield", fill=self.PRIMARY, scale_to_height=32)
        ctk.CTkLabel(
            title_container,
            text="",
            image=icon_admin
        ).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(
            title_container,
            text="Gerenciar Sistema",
            font=("Segoe UI", 28, "bold"),
            text_color=self.TEXT_PRIMARY
        ).pack(side="left")
        
        # Botão adicionar usuário
        btn_add = ctk.CTkButton(
            header_frame,
            text="  Novo Usuário",
            image=fa.icon_to_image("user-plus", fill="#FFFFFF", scale_to_height=18),
            compound="left",
            command=self._adicionar_usuario,
            fg_color=self.PRIMARY,
            hover_color="#005EA6",
            height=40,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        )
        btn_add.pack(side="right")
        
        # Card de estatísticas
        stats_frame = ctk.CTkFrame(main_container, fg_color=self.SURFACE, corner_radius=12)
        stats_frame.pack(fill="x", pady=(0, 24))
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=24, pady=20)
        
        # Buscar estatísticas
        usuarios = self.app_controller.get_all_users()
        total_users = len(usuarios)
        admins = len([u for u in usuarios if u.get('role') == 'admin'])
        users_comuns = total_users - admins
        
        self._criar_stat_card(stats_container, "users", "Total de Usuários", str(total_users), "#0078D7", 0)
        self._criar_stat_card(stats_container, "user-shield", "Administradores", str(admins), "#16A34A", 1)
        self._criar_stat_card(stats_container, "user", "Usuários Comuns", str(users_comuns), "#F59E0B", 2)
        
        # Tabela de usuários
        self.table_frame = ctk.CTkFrame(main_container, fg_color=self.SURFACE, corner_radius=12)
        self.table_frame.pack(fill="both", expand=True)
        
        # Cabeçalho da tabela
        table_header = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        table_header.pack(fill="x", padx=24, pady=(20, 0))
        
        ctk.CTkLabel(
            table_header,
            text="Lista de Usuários",
            font=("Segoe UI", 18, "bold"),
            text_color=self.TEXT_PRIMARY
        ).pack(side="left")
        
        # Container da tabela
        self.users_container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.users_container.pack(fill="both", expand=True, padx=24, pady=20)
    
    def _criar_stat_card(self, parent, icon_name, label, value, color, column):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=0, column=column, padx=12, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        icon = fa.icon_to_image(icon_name, fill=color, scale_to_height=24)
        ctk.CTkLabel(card, text="", image=icon).pack(pady=(0, 8))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 32, "bold"),
            text_color=self.TEXT_PRIMARY
        ).pack()
        
        ctk.CTkLabel(
            card,
            text=label,
            font=("Segoe UI", 12),
            text_color=self.TEXT_SECONDARY
        ).pack()
    
    def _carregar_usuarios(self):
        # Limpar container
        for widget in self.users_container.winfo_children():
            widget.destroy()
        
        usuarios = self.app_controller.get_all_users()
        
        if not usuarios:
            ctk.CTkLabel(
                self.users_container,
                text="Nenhum usuário encontrado",
                font=("Segoe UI", 14),
                text_color=self.TEXT_SECONDARY
            ).pack(pady=40)
            return
        
        # Cabeçalho da lista
        header = ctk.CTkFrame(self.users_container, fg_color="#F9FAFB", height=50, corner_radius=8)
        header.pack(fill="x", pady=(0, 8))
        
        headers = [
            ("Usuário", 0.30),
            ("Perfil", 0.20),
            ("Foto", 0.20),
            ("Ações", 0.30)
        ]
        
        for texto, peso in headers:
            ctk.CTkLabel(
                header,
                text=texto,
                font=("Segoe UI", 12, "bold"),
                text_color=self.TEXT_SECONDARY
            ).place(relx=sum([h[1] for h in headers[:headers.index((texto, peso))]]), 
                    rely=0.5, anchor="w", x=20)
        
        # Linhas de usuários
        for user in usuarios:
            self._criar_linha_usuario(user)
    
    def _criar_linha_usuario(self, user):
        linha = ctk.CTkFrame(
            self.users_container,
            fg_color=self.SURFACE,
            height=70,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER
        )
        linha.pack(fill="x", pady=4)
        
        # Username
        ctk.CTkLabel(
            linha,
            text=user.get('username', 'N/A'),
            font=("Segoe UI", 13, "bold"),
            text_color=self.TEXT_PRIMARY,
            anchor="w"
        ).place(relx=0, rely=0.5, anchor="w", x=20, relwidth=0.29)
        
        # Perfil (Badge)
        role = user.get('role', 'user')
        role_text = "Administrador" if role == 'admin' else "Usuário"
        role_color = self.SUCCESS if role == 'admin' else self.PRIMARY
        role_bg_color = self.SUCCESS_BG if role == 'admin' else self.PRIMARY_BG
        
        role_badge = ctk.CTkFrame(
            linha,
            fg_color=role_bg_color,
            corner_radius=12,
            height=28
        )
        role_badge.place(relx=0.30, rely=0.5, anchor="w", x=20)
        
        ctk.CTkLabel(
            role_badge,
            text=role_text,
            font=("Segoe UI", 11, "bold"),
            text_color=role_color
        ).pack(padx=12, pady=4)
        
        # Foto Path (mostrar se existe)
        foto_text = "✓ Com foto" if user.get('foto_path') else "Sem foto"
        foto_color = self.SUCCESS if user.get('foto_path') else self.TEXT_SECONDARY
        
        ctk.CTkLabel(
            linha,
            text=foto_text,
            font=("Segoe UI", 11),
            text_color=foto_color,
            anchor="w"
        ).place(relx=0.50, rely=0.5, anchor="w", x=20, relwidth=0.19)
        
        # Ações
        actions_frame = ctk.CTkFrame(linha, fg_color="transparent")
        actions_frame.place(relx=0.70, rely=0.5, anchor="w", x=20)
        
        # Botão Editar
        btn_edit = ctk.CTkButton(
            actions_frame,
            text="",
            image=fa.icon_to_image("edit", fill=self.PRIMARY, scale_to_height=16),
            command=lambda u=user: self._editar_usuario(u),
            fg_color="transparent",
            hover_color="#E5E7EB",
            width=36,
            height=36,
            corner_radius=8
        )
        btn_edit.pack(side="left", padx=2)
        
        # Botão Trocar Senha
        btn_password = ctk.CTkButton(
            actions_frame,
            text="",
            image=fa.icon_to_image("key", fill=self.WARNING, scale_to_height=16),
            command=lambda u=user: self._trocar_senha(u),
            fg_color="transparent",
            hover_color="#E5E7EB",
            width=36,
            height=36,
            corner_radius=8
        )
        btn_password.pack(side="left", padx=2)
        
        # Botão Excluir (só se não for o usuário atual)
        current_user = self.app_controller.get_current_username()
        if user.get('username') != current_user:
            btn_delete = ctk.CTkButton(
                actions_frame,
                text="",
                image=fa.icon_to_image("trash", fill=self.DANGER, scale_to_height=16),
                command=lambda u=user: self._excluir_usuario(u),
                fg_color="transparent",
                hover_color="#FEE2E2",
                width=36,
                height=36,
                corner_radius=8
            )
            btn_delete.pack(side="left", padx=2)
    
    def _adicionar_usuario(self):
        dialog = UsuarioDialog(self, self.app_controller, titulo="Novo Usuário")
        if dialog.resultado:
            self._carregar_usuarios()
    
    def _editar_usuario(self, user):
        dialog = UsuarioDialog(self, self.app_controller, titulo="Editar Usuário", user_data=user)
        if dialog.resultado:
            self._carregar_usuarios()
    
    def _trocar_senha(self, user):
        dialog = TrocarSenhaDialog(self, self.app_controller, user)
        if dialog.resultado:
            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!", parent=self)
    
    def _excluir_usuario(self, user):
        # Verificar se não é o único admin
        usuarios = self.app_controller.get_all_users()
        admins = [u for u in usuarios if u.get('role') == 'admin']
        
        if user.get('role') == 'admin' and len(admins) <= 1:
            messagebox.showwarning(
                "Ação Negada",
                "Não é possível excluir o único administrador do sistema!",
                parent=self
            )
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário:\n\n{user.get('username')}?\n\nEsta ação não pode ser desfeita!",
            parent=self,
            icon="warning"
        )
        
        if resposta:
            success, msg = self.app_controller.delete_user(user.get('id'))
            if success:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self._carregar_usuarios()
            else:
                messagebox.showerror("Erro", msg, parent=self)


# Dialog para adicionar/editar usuário
class UsuarioDialog(ctk.CTkToplevel):
    def __init__(self, parent, app_controller, titulo="Usuário", user_data=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.user_data = user_data
        self.resultado = None
        
        # Configurações da janela
        self.title(titulo)
        self.geometry("500x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centralizar janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (480 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._criar_interface()
        
        if user_data:
            self._preencher_dados()
    
    def _criar_interface(self):
        # Container principal
        container = ctk.CTkFrame(self, fg_color="#FFFFFF")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Título
        ctk.CTkLabel(
            container,
            text="Dados do Usuário",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 20))
        
        # Username
        ctk.CTkLabel(container, text="Nome de Usuário:", anchor="w").pack(fill="x", pady=(10, 5))
        self.entry_username = ctk.CTkEntry(container, height=40, placeholder_text="usuario.login")
        self.entry_username.pack(fill="x")
        
        # Se estiver editando, desabilita o username
        if self.user_data:
            self.entry_username.configure(state="disabled")
        
        # Senha (apenas para novo usuário)
        if not self.user_data:
            ctk.CTkLabel(container, text="Senha:", anchor="w").pack(fill="x", pady=(15, 5))
            self.entry_senha = ctk.CTkEntry(container, height=40, placeholder_text="Mínimo 6 caracteres", show="*")
            self.entry_senha.pack(fill="x")
            
            ctk.CTkLabel(container, text="Confirmar Senha:", anchor="w").pack(fill="x", pady=(15, 5))
            self.entry_confirma_senha = ctk.CTkEntry(container, height=40, placeholder_text="Digite a senha novamente", show="*")
            self.entry_confirma_senha.pack(fill="x")
        
        # Perfil
        ctk.CTkLabel(container, text="Perfil de Acesso:", anchor="w").pack(fill="x", pady=(15, 5))
        self.combo_role = ctk.CTkComboBox(
            container,
            values=["user", "admin"],
            height=40,
            state="readonly"
        )
        self.combo_role.pack(fill="x")
        self.combo_role.set("user")
        
        # Botões
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563",
            height=40,
            width=120
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Salvar",
            command=self._salvar,
            fg_color="#0078D7",
            hover_color="#005EA6",
            height=40,
            width=120
        ).pack(side="right")
    
    def _preencher_dados(self):
        self.entry_username.insert(0, self.user_data.get('username', ''))
        self.combo_role.set(self.user_data.get('role', 'user'))
    
    def _salvar(self):
        username = self.entry_username.get().strip()
        
        if not username:
            messagebox.showwarning("Atenção", "Preencha o nome de usuário!", parent=self)
            return
        
        # Validar senha para novo usuário
        if not self.user_data:
            senha = self.entry_senha.get()
            confirma = self.entry_confirma_senha.get()
            
            if len(senha) < 6:
                messagebox.showwarning("Atenção", "A senha deve ter no mínimo 6 caracteres!", parent=self)
                return
            
            if senha != confirma:
                messagebox.showwarning("Atenção", "As senhas não coincidem!", parent=self)
                return
        
        role = self.combo_role.get()
        
        try:
            if self.user_data:
                # Editar usuário existente
                success, msg = self.app_controller.update_user_role(
                    self.user_data.get('id'),
                    role
                )
            else:
                # Criar novo usuário
                success, msg = self.app_controller.create_user(
                    username,
                    self.entry_senha.get(),
                    role
                )
            
            if success:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.resultado = True
                self.destroy()
            else:
                messagebox.showerror("Erro", msg, parent=self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}", parent=self)


# Dialog para trocar senha
class TrocarSenhaDialog(ctk.CTkToplevel):
    def __init__(self, parent, app_controller, user):
        super().__init__(parent)
        self.app_controller = app_controller
        self.user = user
        self.resultado = None
        
        self.title("Trocar Senha")
        self.geometry("450x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (320 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._criar_interface()
    
    def _criar_interface(self):
        container = ctk.CTkFrame(self, fg_color="#FFFFFF")
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(
            container,
            text=f"Trocar Senha de: {self.user.get('username')}",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(container, text="Nova Senha:", anchor="w").pack(fill="x", pady=(10, 5))
        self.entry_senha = ctk.CTkEntry(container, height=40, placeholder_text="Mínimo 6 caracteres", show="*")
        self.entry_senha.pack(fill="x")
        
        ctk.CTkLabel(container, text="Confirmar Senha:", anchor="w").pack(fill="x", pady=(15, 5))
        self.entry_confirma = ctk.CTkEntry(container, height=40, placeholder_text="Digite a senha novamente", show="*")
        self.entry_confirma.pack(fill="x")
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563",
            height=40,
            width=120
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Alterar Senha",
            command=self._alterar_senha,
            fg_color="#0078D7",
            hover_color="#005EA6",
            height=40,
            width=140
        ).pack(side="right")
    
    def _alterar_senha(self):
        senha = self.entry_senha.get()
        confirma = self.entry_confirma.get()
        
        if len(senha) < 6:
            messagebox.showwarning("Atenção", "A senha deve ter no mínimo 6 caracteres!", parent=self)
            return
        
        if senha != confirma:
            messagebox.showwarning("Atenção", "As senhas não coincidem!", parent=self)
            return
        
        success, msg = self.app_controller.change_user_password(
            self.user.get('id'),
            senha
        )
        
        if success:
            self.resultado = True
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)