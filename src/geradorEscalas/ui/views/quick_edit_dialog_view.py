import customtkinter as ctk
from tkinter import messagebox
from ... import fonts
class QuickEditDialog(ctk.CTkToplevel):
    """Diálogo para completar rapidamente dados obrigatórios de colaborador."""
    def __init__(self, master, registro, save_callback, colors_dict):
        super().__init__(master)
        self.registro = registro
        self.save_callback = save_callback
        self.colors = colors_dict # Recebe as cores da view principal

        self.title("Completar Dados Obrigatórios")
        self.resizable(False, False)
        self.grab_set()

        width, height = 540, 540 # Aumentado de 480 para 520
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Layout principal
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))
        ctk.CTkLabel(
            header, text="Completar Dados Obrigatórios", font=fonts.TITULO_SECAO,
            text_color=self.colors["TEXT_PRIMARY"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Preencha os campos obrigatórios para salvar este colaborador.",
            font=fonts.SUBTITULO, text_color=self.colors["TEXT_SECONDARY"],
        ).pack(anchor="w", pady=(3, 10))

        # Formulário
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        form.grid_columnconfigure(1, weight=1)

        self.entries = {}
        self.entry_vars = {} # Para usar com trace_add
        campos = [
            ("nome", "Nome *"), ("matricula", "Matrícula *"),
            ("cargo", "Cargo"), ("setor", "Setor"), ("escala", "Escala"),
        ]
        self.required_fields = ["nome", "matricula"] # Lista de campos obrigatórios

        for i, (campo, label) in enumerate(campos):
            ctk.CTkLabel(
                form, text=label, font=fonts.SUBTITULO, text_color=self.colors["TEXT_PRIMARY"]
            ).grid(row=i, column=0, sticky="w", pady=(0, 6), padx=(0,10))

            # Cria StringVar para campos obrigatórios
            if campo in self.required_fields:
                var = ctk.StringVar()
                var.trace_add("write", self._validate) # Adiciona o rastreador
                self.entry_vars[campo] = var
            else:
                var = None # Campos não obrigatórios não precisam de var/trace

            entry = ctk.CTkEntry(
                form, font=fonts.SUBTITULO, height=36,
                fg_color=self.colors["BUTTON_SECONDARY"],
                border_color=self.colors["BUTTON_SECONDARY_BORDER"],
                textvariable=var # Vincula a StringVar se existir
            )
            entry.grid(row=i, column=1, sticky="ew", pady=(0, 10))
            if registro.get(campo):
                # Se tem var (obrigatório), usa set(); senão, usa insert()
                if var:
                    var.set(str(registro.get(campo)))
                else:
                    entry.insert(0, str(registro.get(campo)))

            self.entries[campo] = entry

        # Aviso de obrigatórios
        ctk.CTkLabel(
            self, text="* Campos obrigatórios", font=fonts.TEXTO_NORMAL,
            text_color=self.colors["TEXT_SECONDARY"],
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))

        # Botões
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="e", padx=20, pady=(10, 20))

        # --- CORREÇÃO: Botão Cancelar em Vermelho ---
        self.cancel_button = ctk.CTkButton(
            button_frame, text="Cancelar", font=fonts.BUTTON_FONT, command=self.destroy,
            fg_color=self.colors["DANGER"], # Cor vermelha
            hover_color=self.colors["DANGER_HOVER"], # Cor vermelha escura
            text_color="#FFFFFF", # Texto branco
            width=120, height=38,
        )
        self.cancel_button.pack(side="right", padx=(10, 0))
        # --- FIM DA CORREÇÃO ---

        self.save_button = ctk.CTkButton(
            button_frame, text="Salvar", command=self._salvar,
            fg_color=self.colors["PRIMARY"], font=fonts.BUTTON_FONT,
            hover_color=self.colors["PRIMARY_HOVER"],
            width=120, height=38,
            state="disabled" # Começa desabilitado
        )
        self.save_button.pack(side="right")

        self._validate() # Chama a validação inicial

    def _validate(self, *args):
        """Valida os campos obrigatórios e atualiza a UI."""
        is_valid = True
        required_values = {}

        for field_key in self.required_fields:
            value = self.entry_vars[field_key].get().strip()
            required_values[field_key] = value
            entry_widget = self.entries[field_key]

            if not value:
                is_valid = False
                # --- CORREÇÃO: Borda Vermelha ---
                entry_widget.configure(border_color=self.colors["DANGER"])
            else:
                entry_widget.configure(border_color=self.colors["BUTTON_SECONDARY_BORDER"])
            # --- FIM DA CORREÇÃO ---

        # --- CORREÇÃO: Habilita/Desabilita Botão Salvar ---
        if is_valid:
            self.save_button.configure(state="normal")
        else:
            self.save_button.configure(state="disabled")
        # --- FIM DA CORREÇÃO ---
        return is_valid, required_values

    def _salvar(self):
        """Coleta os dados e chama o callback de salvar."""
        is_valid, required_values = self._validate()
        if not is_valid:
            messagebox.showerror(
                "Campos Obrigatórios", "Nome e Matrícula são obrigatórios!", parent=self
            )
            return

        dados = {
            "nome": required_values["nome"],
            "matricula": required_values["matricula"],
            "cargo": self.entries["cargo"].get().strip() or None,
            "setor": self.entries["setor"].get().strip() or None,
            "escala": self.entries["escala"].get().strip() or None,
            # Mantém os outros campos como None ou padrão
            "tipo_turno": self.registro.get("tipo_turno"), # Preserva se já existia
            "conselho": self.registro.get("conselho"),   # Preserva se já existia
            "afastamento_inicio": self.registro.get("afastamento_inicio"),
            "afastamento_fim": self.registro.get("afastamento_fim"),
            "afastamento_motivo": self.registro.get("afastamento_motivo"),
            "ativo": True,
        }
        # Chama o callback da view principal
        self.save_callback(dados)
        self.destroy()

# --- FIM DA CLASSE QuickEditDialog ---