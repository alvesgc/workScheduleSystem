
import mysql.connector
import bcrypt
import pandas as pd

DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "1234",
    'database': "gerador_escala_db"
}

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o BD: {err}")
        return None

def get_user_by_username(username):
    """Busca um usuário pelo nome de usuário e retorna seus dados."""
    conexao = get_db_connection()
    if not conexao: return None
    
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as err:
        print(f"Erro ao buscar usuário: {err}")
        return None
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def add_colaborador(dados_colaborador):
    """
    Adiciona um novo colaborador ao banco de dados.
    Retorna (True, "Mensagem de sucesso") ou (False, "Mensagem de erro").
    """
    conexao = get_db_connection()
    if not conexao: 
        return False, "Não foi possível conectar ao banco de dados."

    try:
        cursor = conexao.cursor()
        
        # Mapeia os dados do formulário para as colunas da tabela
        sql = """
            INSERT INTO colaboradores 
            (nome, matricula, cargo, setor, escala, tipo_turno, horario_padrao, coren, ativo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados_colaborador.get("Nome"),
            dados_colaborador.get("Matrícula"),
            dados_colaborador.get("Cargo"),
            dados_colaborador.get("Setor"),
            dados_colaborador.get("Escala"),
            dados_colaborador.get("Tipo de Turno"),
            dados_colaborador.get("Horário Padrão"),
            dados_colaborador.get("Conselho (opcional)"),
            True  # Define como ativo por padrão
        )
        
        cursor.execute(sql, valores)
        conexao.commit()
        
        return True, f"Colaborador '{dados_colaborador.get('Nome')}' cadastrado com sucesso!"

    except mysql.connector.Error as err:
        # Erro específico para matrícula duplicada
        if err.errno == 1062: # Código de erro para 'Duplicate entry'
            return False, f"Erro: A matrícula '{dados_colaborador.get('Matrícula')}' já existe no banco de dados."
        return False, f"Erro de banco de dados: {err}"
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

def add_user(username, password, role):
    """
    Adiciona um novo usuário ao banco de dados com senha criptografada.
    Retorna (True, "Mensagem de sucesso") ou (False, "Mensagem de erro").
    """
    conexao = get_db_connection()
    if not conexao:
        return False, "Não foi possível conectar ao banco de dados."

    try:
        # Criptografa a senha antes de salvar
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        cursor = conexao.cursor()
        sql = "INSERT INTO usuarios (username, password_hash, role) VALUES (%s, %s, %s)"
        valores = (username, hashed_password.decode('utf-8'), role)
        
        cursor.execute(sql, valores)
        conexao.commit()
        
        return True, f"Usuário '{username}' criado com sucesso!"

    except mysql.connector.Error as err:
        if err.errno == 1062: # Erro de entrada duplicada
            return False, f"Erro: O nome de usuário '{username}' já existe."
        return False, f"Erro de banco de dados: {err}"
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()
            
def get_active_collaborators_as_dataframe():
    """Busca todos os colaboradores ativos e retorna como um DataFrame do Pandas."""
    conexao = get_db_connection()
    if not conexao:
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de falha na conexão
    
    try:
        query = "SELECT * FROM colaboradores WHERE ativo = TRUE"
        df = pd.read_sql(query, conexao)
        return df
    except Exception as e:
        print(f"Erro ao buscar colaboradores: {e}")
        return pd.DataFrame()
    finally:
        if conexao.is_connected():
            conexao.close()