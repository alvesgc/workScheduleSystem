import customtkinter as ctk
import os

# --- VARIÁVEIS GLOBAIS PARA GUARDAR AS FONTES ---
TEXTO_NORMAL = None
LABEL_FONT = None
BUTTON_FONT = None
TITULO_SECAO = None
SUBTITULO = None
TITULO_CARD = None
TEXTO_PEQUENO = None

def init_fonts():
    """
    Esta função deve ser chamada UMA VEZ no início da aplicação.
    Ela carrega os arquivos de fonte .ttf/.otf e cria os objetos CTkFont.
    """
    global TEXTO_NORMAL, LABEL_FONT, BUTTON_FONT, TITULO_SECAO, SUBTITULO,TITULO_CARD

    try:
        # Caminho para a pasta de fontes
        font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts")
        
        poppins_regular_path = os.path.join(font_path, "Poppins-Regular.ttf")
        poppins_bold_path = os.path.join(font_path, "Poppins-Bold.ttf")

        # --- Carregando as fontes Poppins ---
        ctk.FontManager.load_font(poppins_regular_path)
        ctk.FontManager.load_font(poppins_bold_path)

        # --- Definições dos estilos de fonte usando os nomes das famílias ---
        # (Após carregar com FontManager, podemos usar o nome da família da fonte)
        TEXTO_PEQUENO = ctk.CTkFont(family="Poppins", size=12)
        TEXTO_NORMAL = ctk.CTkFont(family="Poppins", size=14)
        LABEL_FONT = ctk.CTkFont(family="Poppins Bold", size=14)
        BUTTON_FONT = ctk.CTkFont(family="Poppins Bold", size=14)
        TITULO_SECAO = ctk.CTkFont(family="Poppins Bold", size=28)
        TITULO_CARD = ctk.CTkFont(family="Poppins Bold", size=48)
        SUBTITULO = ctk.CTkFont(family="Poppins", size=16)


        print("Fontes Poppins carregadas com sucesso.")
        return True

    except Exception as e:
        print(f"ERRO: Não foi possível carregar as fontes: {e}")
        print("Verifique se os arquivos .ttf estão na pasta 'src/geradorEscalas/assets/fonts/'.")
        print("Usando fontes padrão do sistema.")
        # Define fontes padrão como fallback
        TEXTO_NORMAL = ctk.CTkFont(size=14)
        LABEL_FONT = ctk.CTkFont(size=14, weight="bold")
        BUTTON_FONT = ctk.CTkFont(size=14, weight="bold")
        TITULO_SECAO = ctk.CTkFont(size=28, weight="bold")
        SUBTITULO = ctk.CTkFont(size=16)
        return False