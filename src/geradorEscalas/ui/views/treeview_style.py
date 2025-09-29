from tkinter import ttk

def setup_treeview_style():
    """Configura um estilo personalizado para o ttk.Treeview se parecer com o tema escuro."""
    style = ttk.Style()
    
    # Cores
    bg_color = "#2A2D2E"
    text_color = "#FFFFFF"
    header_bg_color = "#343638"
    selected_color = "#3A7EBF"
    
    # Cores alternadas para as linhas
    odd_row_color = "#343638"
    even_row_color = "#2A2D2E"

    style.theme_use("default")
    style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
    style.configure("Treeview.Heading", background=header_bg_color, foreground=text_color, font=("Arial", 12, "bold"), padding=(10, 10))
    style.map("Treeview.Heading", relief=[('active', 'flat'), ('!active', 'flat')], background=[('active', header_bg_color), ('!active', header_bg_color)])
    
    # --- NOVAS TAGS PARA CORES ALTERNADAS ---
    style.configure('oddrow.Treeview', background=odd_row_color)
    style.configure('evenrow.Treeview', background=even_row_color)
    
    # Mantém a cor de seleção com prioridade
    style.map('Treeview',
              background=[('selected', selected_color)],
              foreground=[('selected', text_color)])