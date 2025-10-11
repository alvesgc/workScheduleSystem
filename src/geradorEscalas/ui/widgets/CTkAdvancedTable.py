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
            fieldbackground="#242424",
            background="#242424",
            foreground="white",
            borderwidth=0,
        )
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        style.configure(
            "Treeview.Heading",
            font=fonts.LABEL_FONT,
            background="#333333",
            foreground="#E0E0E0",
            padding=5,
            borderwidth=0,
        )

        # Mapeia as cores para os estados (hover e selecionado)
        style.map("Treeview.Heading", background=[("active", "#4A4A4A")])
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

        # Tags de Cor de Texto (podem ser usadas conforme a necessidade de cada tela)
        self.tag_configure("turno_D", foreground="#63D471")  # Verde mais vibrante
        self.tag_configure("turno_N", foreground="#5DADE2")  # Azul mais suave
        self.tag_configure("turno_24H", foreground="#EC7063")  # Vermelho mais suave
        self.tag_configure(
            "afastamento", foreground="#F7DC6F", font=fonts.LABEL_FONT
        )  # Amarelo mais legível
