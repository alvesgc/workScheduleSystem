import customtkinter as ctk
import tkinter.ttk as ttk
from ... import fonts


class CTkAdvancedTable(ttk.Treeview):
    def __init__(self, master, columns, show_checkbox_column=False, **kwargs):
        """
        Tabela avançada com tema claro.

        Args:
            master: Widget pai
            show_checkbox_column: Se deve mostrar coluna de checkbox
        """
        # --- CORES DO TEMA CLARO ---
        BG_COLOR = "#FFFFFF"
        FG_COLOR = "#1E1E1E"
        FIELD_BG = "#FFFFFF"
        HEADER_BG = "#0078D7"
        HEADER_FG = "#FFFFFF"
        HEADER_ACTIVE = "#005EA6"
        EVENROW_BG = "#FFFFFF"
        ODDROW_BG = "#F9FAFB"
        SELECT_BG = "#0078D7"
        SELECT_FG = "#FFFFFF"

        # --- ESTILIZAÇÃO ---
        style = ttk.Style()

        # Usa tema clam que dá mais controle
        style.theme_use("clam")

        # Usa um nome de estilo único para cada instância para evitar conflitos
        style_name = f"Custom{id(self)}.Treeview"

        # Configura aparência da tabela
        style.configure(
            style_name,
            rowheight=30,
            font=fonts.TEXTO_NORMAL,
            fieldbackground=FIELD_BG,
            background=BG_COLOR,
            foreground=FG_COLOR,
            borderwidth=0,
        )

        # Configura aparência do cabeçalho - SEM fieldbackground
        style.configure(
            f"{style_name}.Heading",
            font=fonts.LABEL_FONT,
            background=HEADER_BG,
            foreground=HEADER_FG,
            borderwidth=1,
            relief="flat",
            lightcolor=HEADER_BG,
            darkcolor=HEADER_BG,
        )

        # Mapeia estados (hover e seleção)
        style.map(
            f"{style_name}.Heading",
            background=[("active", HEADER_ACTIVE)],
            foreground=[("active", HEADER_FG), ("!active", HEADER_FG)],
        )
        style.map(
            style_name,
            background=[("selected", SELECT_BG)],
            foreground=[("selected", SELECT_FG)],
        )

        # Configuração da coluna de checkbox
        kwargs['columns'] = columns
        kwargs["show"] = "tree headings" if show_checkbox_column else "headings"

        # Inicializa com o estilo único
        super().__init__(master, style=style_name, **kwargs)

        if show_checkbox_column:
            # Para a coluna de checkbox, não definimos texto, apenas a largura
            self.column("#0", width=50, stretch=False, anchor="center")
            self.heading("#0", text="") # <-- Deixa o texto do cabeçalho vazio
        else:
            self.column("#0", width=0, stretch=False)
            
        # Define os cabeçalhos para todas as colunas de dados
        for col in columns:
             self.heading(col, text=col.replace('_', ' ').title(), anchor="w")

        # --- TAGS DE ESTILO PADRÃO ---
        self.tag_configure("evenrow", background=EVENROW_BG)
        self.tag_configure("oddrow", background=ODDROW_BG)
        self.tag_configure("critical_escala", font=fonts.LABEL_FONT)

        # Tags de cores específicas
        self.tag_configure("turno_X", foreground="#0078D7")
        self.tag_configure("turno_F", foreground="#6B6B6B")
        self.tag_configure(
            "afastamento", foreground="#DC2626", font=("Calibri", 9, "italic")
        )
        self.tag_configure("trabalho", foreground="#1E1E1E")
