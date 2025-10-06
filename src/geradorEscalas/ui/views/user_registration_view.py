import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import os


class UserRegistrationView(ctk.CTkFrame):
    def __init__(self, master, save_callback, back_callback):
        super().__init__(master)
        self.save_callback = save_callback
        self.back_callback = back_callback

        # Guarda o caminho do arquivo da foto que o usuário selecionou
        self.selected_photo_path = None

        # --- Layout Principal ---
        self.pack_propagate(False)  # Impede que o frame se ajuste aos widgets internos

        # Frame interno para centralizar o conteúdo
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            main_frame, text="Cadastro de Usuário", font=("", 24, "bold")
        ).pack(pady=(0, 20))

        # --- Seção da Foto de Perfil ---
        ctk.CTkLabel(main_frame, text="Foto de Perfil (Opcional):").pack(anchor="w")

        # Label para mostrar a pré-visualização da imagem
        self.photo_preview = ctk.CTkLabel(main_frame, text="")
        self.photo_preview.pack(pady=10)
        self._load_and_display_image()  # Carrega a imagem padrão inicial

        ctk.CTkButton(
            main_frame, text="Selecionar Foto...", command=self._select_photo
        ).pack(pady=(0, 20))

        # --- Campos de Dados ---
        ctk.CTkLabel(main_frame, text="Nome de Usuário:").pack(anchor="w")
        self.user_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Digite o nome de usuário"
        )
        self.user_entry.pack(fill="x", pady=5)

        ctk.CTkLabel(main_frame, text="Senha:").pack(anchor="w", pady=(10, 0))
        self.pass_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Digite a senha", show="*"
        )
        self.pass_entry.pack(fill="x", pady=5)

        ctk.CTkLabel(main_frame, text="Confirmar Senha:").pack(anchor="w", pady=(10, 0))
        self.confirm_pass_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Confirme a senha", show="*"
        )
        self.confirm_pass_entry.pack(fill="x", pady=5)

        ctk.CTkLabel(main_frame, text="Tipo de Acesso (Role):").pack(
            anchor="w", pady=(10, 0)
        )
        self.role_menu = ctk.CTkOptionMenu(main_frame, values=["user", "admin"])
        self.role_menu.pack(fill="x", pady=5)

        # --- Botões de Ação ---
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(30, 0))
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame, text="Salvar", command=self._on_save, height=40
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(
            button_frame,
            text="Voltar",
            command=self.back_callback,
            height=40,
            fg_color="#7A7A7A",
            hover_color="#5E5E5E",
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _load_and_display_image(self, path=None):
        """Carrega e exibe uma imagem na tela, usando uma genérica como padrão."""
        # Caminho para sua imagem genérica. Verifique se este caminho está correto.
        generic_path = "src/geradorEscalas/assets/icons/user_generic.png"

        image_path = generic_path
        if path and os.path.exists(path):
            image_path = path

        try:
            image = ctk.CTkImage(Image.open(image_path), size=(100, 100))
            self.photo_preview.configure(image=image)
        except Exception as e:
            print(f"Erro ao carregar imagem de perfil: {e}")
            self.photo_preview.configure(image=None, text="Erro ao\ncarregar\nimagem")

    def _select_photo(self):
        """Abre uma janela para o usuário selecionar uma foto de perfil."""
        filepath = filedialog.askopenfilename(
            title="Selecione uma foto de perfil",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg")],
        )
        if filepath:
            self.selected_photo_path = filepath
            self._load_and_display_image(filepath)

    def _on_save(self):
        """Coleta todos os dados do formulário e os envia para o controlador principal."""
        data = {
            "username": self.user_entry.get(),
            "password": self.pass_entry.get(),
            "confirm_password": self.confirm_pass_entry.get(),
            "role": self.role_menu.get(),
            "photo_path": self.selected_photo_path,  # Envia o caminho do arquivo original selecionado
        }
        self.save_callback(data)  # Chama a função on_save_user no __main__.py
