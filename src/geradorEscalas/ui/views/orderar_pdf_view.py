import customtkinter as ctk


class OrdenacaoPdfDialog(ctk.CTkToplevel):
    """Pop-up para escolher o tipo de ordenação do PDF."""

    # Adiciona x e y aos parâmetros
    def __init__(self, master, x=None, y=None):
        super().__init__(master)
        self.title("Ordenar PDF Por")
        width, height = 300, 180  # Define a largura e altura
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # --- Posicionamento ---
        if x is not None and y is not None:
            # Usa as coordenadas recebidas (com um pequeno ajuste para não ficar colado)
            self.geometry(f"+{x+10}+{y+10}")
        else:
            # Fallback para centralizar se as coordenadas não forem passadas
            self.update_idletasks()
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x_center = (screen_width // 2) - (width // 2)
            y_center = (screen_height // 2) - (height // 2)
            self.geometry(f"+{x_center}+{y_center}")
        # --- Fim do Posicionamento ---

        self.ordenacao_escolhida = None

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Escolha como agrupar a escala no PDF:").pack(
            anchor="w", pady=(0, 10)
        )

        self.radio_var = ctk.StringVar(value="setor")

        radio_setor = ctk.CTkRadioButton(
            main_frame,
            text="Ordenar por Setor (Padrão)",
            variable=self.radio_var,
            value="setor",
        )
        radio_setor.pack(anchor="w", pady=2)

        radio_cargo = ctk.CTkRadioButton(
            main_frame, text="Ordenar por Cargo", variable=self.radio_var, value="cargo"
        )
        radio_cargo.pack(anchor="w", pady=2)

        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(15, 0))

        cancel_button = ctk.CTkButton(
            buttons_frame, text="Cancelar", command=self.destroy
        )
        cancel_button.pack(side="right")

        export_button = ctk.CTkButton(
            buttons_frame, text="Exportar", command=self._on_export
        )
        export_button.pack(side="right", padx=(0, 10))

        self.focus()

    def _on_export(self):
        """Define a ordenação escolhida e fecha o pop-up."""
        self.ordenacao_escolhida = self.radio_var.get()
        self.destroy()
