# adicionar_usuario.py

import mysql.connector
from getpass import getpass  # Para digitar a senha de forma segura
import bcrypt  # Biblioteca de criptografia

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "1234", # <<< MUDE AQUI
    'database': "gerador_escala_db"
}

def adicionar_superusuario():
    try:
        print("--- Criando Superusuário 'dev' ---")
        
        # Coleta a senha de forma segura, sem mostrá-la na tela
        password = getpass("Digite a senha para o usuário 'dev': ")
        password_confirm = getpass("Confirme a senha: ")

        if password != password_confirm:
            print("\nERRO: As senhas não coincidem. Operação cancelada.")
            return

        # Criptografa a senha
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Conecta ao banco de dados e insere o novo usuário
        conexao = mysql.connector.connect(**DB_CONFIG)
        cursor = conexao.cursor()

        # Usamos INSERT IGNORE para não dar erro se o usuário 'dev' já existir
        query = "INSERT IGNORE INTO usuarios (username, password_hash, role) VALUES (%s, %s, %s)"
        valores = ('dev', hashed_password.decode('utf-8'), 'admin')
        
        cursor.execute(query, valores)
        conexao.commit()

        if cursor.rowcount > 0:
            print("\nUsuário 'dev' criado com sucesso!")
        else:
            print("\nO usuário 'dev' já existe no banco de dados.")

    except mysql.connector.Error as err:
        print(f"\nERRO de Banco de Dados: {err}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

if __name__ == "__main__":
    # Instale a biblioteca bcrypt antes de executar:
    # py -m pip install bcrypt
    adicionar_superusuario()