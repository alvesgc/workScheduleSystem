# src/gerador_escalas/fonts.py

import customtkinter as ctk
import os

# --- VARIÁVEIS GLOBAIS PARA GUARDAR AS FONTES ---
# Começam vazias e serão preenchidas pela função init_fonts
TEXTO_NORMAL = None
LABEL_FONT = None
BUTTON_FONT = None
TITULO_SECAO = None
SUBTITULO = None

def init_fonts():
    """
    Esta função deve ser chamada APÓS a janela principal do app ser criada.
    Ela carrega os arquivos de fonte e cria os objetos CTkFont.
    """
    global TEXTO_NORMAL, LABEL_FONT, BUTTON_FONT, TITULO_SECAO, SUBTITULO

    try:
        # Caminhos para os arquivos da fonte
        font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets/fonts")
        poppins_regular = os.path.join(font_path, "Poppins-Regular.ttf")
        poppins_bold = os.path.join(font_path, "Poppins-Bold.ttf")

        # Definições dos estilos de fonte
        TEXTO_NORMAL = ctk.CTkFont(family=poppins_regular, size=14)
        LABEL_FONT = ctk.CTkFont(family=poppins_bold, size=14)
        BUTTON_FONT = ctk.CTkFont(family=poppins_bold, size=14)
        TITULO_SECAO = ctk.CTkFont(family=poppins_bold, size=28)
        SUBTITULO = ctk.CTkFont(family=poppins_regular, size=16)

        print("Fontes Poppins carregadas com sucesso.")
        return True

    except Exception as e:
        print(f"ERRO: Não foi possível carregar as fontes Poppins: {e}")
        print("Verifique se os arquivos .ttf estão na pasta 'src/gerador_escalas/assets/fonts/'.")
        print("Usando fontes padrão do sistema.")
        return False