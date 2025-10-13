import customtkinter as ctk
import tkinter.ttk as ttk
from ... import fonts  # Importa o módulo de fontes


class CTkAdvancedTable(ttk.Treeview):
    def __init__(self, master, show_checkbox_column=False, **kwargs):
        # --- ESTILIZAÇÃO CENTRALIZADA ---
        style = ttk.Style()

        # Pega a cor de destaque do tema CustomTkinter
        select_bg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"][
            1
        ]  # [1] para modo dark

        # Define o layout para remover a borda "fantasma" do cabeçalho
        style.layout(
            "Treeview.Heading",
            [
                ("Treeview.Heading.cell", {"sticky": "nswe"}),
                (
                    "Treeview.Heading.border",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Treeview.Heading.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Treeview.Heading.image",
                                            {"side": "right", "sticky": ""},
                                        ),
                                        ("Treeview.Heading.text", {"sticky": "we"}),
                                    ],
                                },
                            )
                        ],
                    },
                ),
            ],
        )

        # Configura a aparência geral da tabela e do cabeçalho
        style.configure(
            "Treeview",
            rowheight=30,
            font=fonts.TEXTO_NORMAL,
            fieldbackground="white",
            background="white",
            foreground="white",
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            font=fonts.LABEL_FONT,
            background="white",
            foreground="white",
            padding=5,
            borderwidth=0,
        )
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        # Mapeia as cores para os estados (hover e selecionado)
        style.map("Treeview.Heading", background=[("active", "#white")])
        style.map(
            "Treeview",
            background=[("selected", select_bg_color)],
            foreground=[("selected", "white")],
        )

        kwargs['show'] = 'tree headings' if show_checkbox_column else 'headings'
        # Inicializa a classe base Treeview com o estilo
        super().__init__(master, style="Treeview", **kwargs)

        if show_checkbox_column:
            self.column("#0", width=50, stretch=False, anchor="center")
            self.heading("#0", text="")
        else:
            self.column("#0", width=0, stretch=False)
            
        # --- TAGS DE ESTILO PADRÃO ---
        # Todas as tabelas que usarem este componente já terão estas tags prontas
        self.tag_configure("evenrow", background="#2B2B2B")
        self.tag_configure("oddrow", background="#242424")
        self.tag_configure("critical_escala", font=fonts.LABEL_FONT)  # Negrito

        self.tag_configure("turno_X", foreground="#3C4FFC")     # Verde para Trabalho
        self.tag_configure("turno_F", foreground="gray50")      # Cinza para Folga
        self.tag_configure("afastamento", foreground="#F1C40F", font=('Calibri', 9, 'italic')) # Amarelo para Afastamento