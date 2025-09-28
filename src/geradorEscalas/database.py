import mysql.connector
import bcrypt
import pandas as pd

from datetime import datetime, timedelta

DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "1234", # <<< MUDE AQUI
    'database': "gerador_escala_db"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o BD: {err}")
        return None

def get_user_by_username(username):
    conexao = get_db_connection()
    if not conexao: return None
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        return cursor.fetchone()
    finally:
        if conexao.is_connected(): conexao.close()

def add_user(username, password, role):
    conexao = get_db_connection()
    if not conexao: return False, "Não foi possível conectar ao banco de dados."
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor = conexao.cursor()
        sql = "INSERT INTO usuarios (username, password_hash, role) VALUES (%s, %s, %s)"
        valores = (username, hashed_password.decode('utf-8'), role)
        cursor.execute(sql, valores)
        conexao.commit()
        return True, f"Usuário '{username}' criado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1062: return False, f"Erro: O nome de usuário '{username}' já existe."
        return False, f"Erro de banco de dados: {err}"
    finally:
        if conexao.is_connected(): conexao.close()

def add_colaborador(dados_colaborador):
    conexao = get_db_connection()
    if not conexao: return False, "Não foi possível conectar ao banco de dados."
    try:
        cursor = conexao.cursor()
        sql = """
            INSERT INTO colaboradores 
            (nome, matricula, cargo, setor, escala, tipo_turno, horario_padrao, coren, ativo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados_colaborador.get("Nome"), dados_colaborador.get("Matrícula"),
            dados_colaborador.get("Cargo"), dados_colaborador.get("Setor"),
            dados_colaborador.get("Escala"), dados_colaborador.get("Tipo de Turno"),
            dados_colaborador.get("Horário Padrão"), dados_colaborador.get("COREN (opcional)"),
            True
        )
        cursor.execute(sql, valores)
        conexao.commit()
        return True, f"Colaborador '{dados_colaborador.get('Nome')}' cadastrado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1062: return False, f"Erro: A matrícula '{dados_colaborador.get('Matrícula')}' já existe."
        return False, f"Erro de banco de dados: {err}"
    finally:
        if conexao.is_connected(): conexao.close()

def get_active_collaborators_as_dataframe():
    conexao = get_db_connection()
    if not conexao: return pd.DataFrame()
    try:
        query = "SELECT * FROM colaboradores WHERE ativo = TRUE"
        return pd.read_sql(query, conexao)
    except Exception as e:
        print(f"Erro ao buscar colaboradores: {e}")
        return pd.DataFrame()
    finally:
        if conexao.is_connected(): conexao.close()

def get_dashboard_stats():
    """Busca estatísticas rápidas para o dashboard."""
    stats = {'total_colaboradores': 0, 'total_setores': 0}
    conexao = get_db_connection()
    if not conexao: return stats
    
    try:
        cursor = conexao.cursor()
        # Conta colaboradores ativos
        cursor.execute("SELECT COUNT(id) FROM colaboradores WHERE ativo = TRUE")
        stats['total_colaboradores'] = cursor.fetchone()[0]
        # Conta setores distintos
        cursor.execute("SELECT COUNT(DISTINCT setor) FROM colaboradores WHERE ativo = TRUE")
        stats['total_setores'] = cursor.fetchone()[0]
        return stats
    finally:
        if conexao.is_connected(): conexao.close()
def get_upcoming_leaves(days_ahead=30):
    leaves = []
    conexao = get_db_connection()
    if not conexao: return leaves
    try: 
        cursor = conexao.cursor(directonary=True)
        query = "SELECT nome, periodo_afastamento FROM colaboradores WHERE periodo_afastamento IS NOT NULL AND periodo_afastamento != '' AND ativo = TRUE"
        cursor.execute(query)
        
        today = datetime.now()
        limit_date = today + timedelta(days=days_ahead)
        
        for row in cursor.fetchall(): 
            try:
                # Extrai a data de início do texto "dd/mm/aaaa a dd/mm/aaaa"
                start_date_str = row['periodo_afastamento'].split('a')[0].strip()
                start_date = datetime.striptime(start_date_str, "%d/%m/%Y")
                # Verifica se a data de início está no nosso intervalo de tempo
                if today <= start_date <= limit_date:
                    leaves.append({'nome': row['nome'], 'data_inicio': start_date.strftime('%d/%m/%Y')})
            except (ValueError, IndexError):
                # Ignora formatos de data inválidos
                continue
        return sorted(leaves, key=lambda x: datetime.strptime(x['data_inicio'], '%d/%m/%Y'))
    finally:
        if conexao.is_connected(): conexao.close()
                