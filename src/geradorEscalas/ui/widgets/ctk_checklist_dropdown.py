import customtkinter as ctk
from ... import fonts

class ChecklistDropdown(ctk.CTkToplevel):
    def __init__(self, master_button, items_dict, update_callback):
        super().__init__(master_button)
        self.update_callback = update_callback
        self.items_dict = items_dict

        self.overrideredirect(True)

        # Posicionamento da janela
        x = master_button.winfo_rootx()
        y = master_button.winfo_rooty() + master_button.winfo_height()
        self.geometry(f"+{x}+{y}")

        main_frame = ctk.CTkFrame(self, border_width=1, border_color="gray50")
        main_frame.pack(expand=True, fill="both")

        # --- NOVO: Frame para o título e os links de ação ---
        actions_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=(5,0))
        actions_frame.grid_columnconfigure(0, weight=1) # Coluna do título expande

        ctk.CTkLabel(actions_frame, text="Selecione os itens", font=fonts.LABEL_FONT, anchor="w").grid(row=0, column=0, sticky="w")
        
        # Link "Selecionar Todos"
        select_all_button = ctk.CTkButton(actions_frame, text="Todos", width=40, font=("", 12, "underline"),
                                          fg_color="transparent", text_color="#3498DB", hover=False,
                                          command=self._select_all)
        select_all_button.grid(row=0, column=1, padx=5)

        # Link "Limpar Seleção"
        deselect_all_button = ctk.CTkButton(actions_frame, text="Nenhum", width=50, font=("", 12, "underline"),
                                            fg_color="transparent", text_color="#3498DB", hover=False,
                                            command=self._deselect_all)
        deselect_all_button.grid(row=0, column=2, padx=5)

        # --- Frame rolável para os checkboxes ---
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.pack(expand=True, fill="both", padx=5, pady=5)

        for key, var in self.items_dict.items():
            cb = ctk.CTkCheckBox(scroll_frame, text=key, variable=var, onvalue="on", offvalue="off")
            cb.pack(anchor="w", padx=10, pady=4)

        self.bind("<FocusOut>", self._on_focus_out)
        self.focus_set()

    def _on_focus_out(self, event):
        if self.update_callback:
            self.update_callback()
        self.destroy()
        
    # --- NOVO: Métodos para selecionar/desselecionar todos ---
    def _select_all(self):
        """Marca todos os checkboxes."""
        for var in self.items_dict.values():
            var.set("on")

    def _deselect_all(self):
        """Desmarca todos os checkboxes."""
        for var in self.items_dict.values():
            var.set("off")