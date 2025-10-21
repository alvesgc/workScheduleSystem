# Em src/geradorEscalas/utils.py
import sys
import os

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando tanto em dev quanto no .exe """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se não estiver empacotado, o caminho base é a pasta raiz do projeto
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)