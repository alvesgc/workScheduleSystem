import mysql.connector
import bcrypt
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# --- CONFIGURAÇÕES DE BANCO DE DADOS (CORRIGIDO) ---
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "1234", # <<< MUDE AQUI SE NECESSÁRIO
    'port': "3306",
    'database': "gerador_escala_db"
}

try:
    # 2. STRING DE CONEXÃO CORRIGIDA PARA USAR AS VARIÁVEIS CERTAS
    connection_string = (
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    engine = create_engine(connection_string)
except Exception as e:
    engine = None
    print(f"ERRO CRÍTICO: Falha ao criar o motor de conexão com SQLAlchemy: {e}")

def get_user_by_username(username):
    """Busca um usuário pelo nome de usuário e retorna seus dados."""
    if not engine: return None
    
    with engine.connect() as connection:
        query = text("SELECT * FROM usuarios WHERE username = :user")
        result = connection.execute(query, {"user": username}).fetchone()
        return result._asdict() if result else None

def add_user(username, password, role):
    """Adiciona um novo usuário ao banco de dados com senha criptografada."""
    if not engine: return False, "Motor de conexão com o banco de dados não está disponível."
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            query = text("INSERT INTO usuarios (username, password_hash, role) VALUES (:user, :pwd_hash, :role)")
            connection.execute(query, {"user": username, "pwd_hash": hashed_password.decode('utf-8'), "role": role})
            trans.commit()
            return True, f"Usuário '{username}' criado com sucesso!"
        except Exception as e:
            trans.rollback()
            if "Duplicate entry" in str(e):
                return False, f"Erro: O nome de usuário '{username}' já existe."
            return False, f"Erro de banco de dados: {e}"

def add_colaborador(dados_colaborador):
    """Adiciona um novo colaborador ao banco de dados."""
    if not engine: return False, "Motor de conexão com o banco de dados não está disponível."
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            sql = text("""
                INSERT INTO colaboradores 
                (nome, matricula, cargo, setor, escala, tipo_turno, horario_padrao, coren, ativo) 
                VALUES (:nome, :matricula, :cargo, :setor, :escala, :tipo_turno, :horario_padrao, :coren, :ativo)
            """)
            params = { "nome": dados_colaborador.get("Nome"), "matricula": dados_colaborador.get("Matrícula"), "cargo": dados_colaborador.get("Cargo"), "setor": dados_colaborador.get("Setor"), "escala": dados_colaborador.get("Escala"), "tipo_turno": dados_colaborador.get("Tipo de Turno"), "horario_padrao": dados_colaborador.get("Horário Padrão"), "coren": dados_colaborador.get("COREN (opcional)"), "ativo": True }
            connection.execute(sql, params)
            trans.commit()
            return True, f"Colaborador '{dados_colaborador.get('Nome')}' cadastrado com sucesso!"
        except Exception as e:
            trans.rollback()
            if "Duplicate entry" in str(e):
                return False, f"Erro: A matrícula '{dados_colaborador.get('Matrícula')}' já existe."
            return False, f"Erro de banco de dados: {e}"

def get_all_collaborators_dataframe(search_term=None):
    """Busca os colaboradores, opcionalmente filtrando, e retorna como DataFrame."""
    if not engine: return pd.DataFrame()
    
    query = """
        SELECT nome, matricula, cargo, setor, tipo_turno, horario_padrao, coren AS conselho
        FROM colaboradores WHERE ativo = TRUE
    """
    # Usaremos um dicionário para os parâmetros, que é mais robusto
    params = {}
    
    if search_term:
        # SQLAlchemy usa o formato :key para parâmetros nomeados
        query += " AND (nome LIKE :term OR matricula LIKE :term)"
        params['term'] = f"%{search_term}%"

    query += " ORDER BY nome"
    
    try:
        # Passa o dicionário de parâmetros para o pandas
        df = pd.read_sql(query, engine, params=params)
        return df
    except Exception as e:
        print(f"Erro ao executar a pesquisa no banco de dados: {e}")
        return pd.DataFrame()

def delete_collaborator_by_matricula(matricula):
    """Deleta um colaborador do banco de dados pela matrícula."""
    if not engine: return False, "Motor de conexão com o banco de dados não está disponível."
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            query = text("DELETE FROM colaboradores WHERE matricula = :matricula")
            result = connection.execute(query, {"matricula": matricula})
            trans.commit()
            if result.rowcount > 0:
                return True, "Colaborador excluído com sucesso."
            else:
                return False, "Nenhum colaborador encontrado com a matrícula fornecida."
        except Exception as e:
            trans.rollback()
            return False, f"Erro de banco de dados: {e}"
        
def update_collaborator(matricula, data):
    """Atualiza os dados de um colaborador existente."""
    if not engine: return False, "Motor de conexão não está disponível."
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # Constrói a query de atualização dinamicamente
            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query_str = f"UPDATE colaboradores SET {set_clause} WHERE matricula = :original_matricula"
            
            params = data
            params['original_matricula'] = matricula
            
            connection.execute(text(query_str), params)
            trans.commit()
            return True, "Colaborador atualizado com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro de banco de dados: {e}"
        
def get_dashboard_stats():
    """Busca estatísticas rápidas para o dashboard usando SQLAlchemy."""
    stats = {'total_colaboradores': 0, 'total_setores': 0}
    if not engine: return stats
    
    with engine.connect() as connection:
        try:
            query_colab = text("SELECT COUNT(id) FROM colaboradores WHERE ativo = TRUE")
            stats['total_colaboradores'] = connection.execute(query_colab).scalar_one_or_none() or 0
            
            query_setor = text("SELECT COUNT(DISTINCT setor) FROM colaboradores WHERE ativo = TRUE")
            stats['total_setores'] = connection.execute(query_setor).scalar_one_or_none() or 0
            
            return stats
        except Exception as e:
            print(f"Erro ao buscar estatísticas do dashboard: {e}")
            return {'total_colaboradores': 0, 'total_setores': 0}

def get_upcoming_leaves(days_ahead=30):
    """Busca afastamentos que começarão nos próximos X dias usando SQLAlchemy."""
    leaves = []
    if not engine: return leaves
    
    with engine.connect() as connection:
        try:
            query = text("SELECT nome, periodo_afastamento FROM colaboradores WHERE periodo_afastamento IS NOT NULL AND periodo_afastamento != '' AND ativo = TRUE")
            result = connection.execute(query)
            
            today = datetime.now()
            limit_date = today + timedelta(days=days_ahead)
            
            for row in result:
                row_dict = row._asdict()
                try:
                    start_date_str = row_dict['periodo_afastamento'].split(' a ')[0]
                    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
                    if today <= start_date <= limit_date:
                        leaves.append({'nome': row_dict['nome'], 'data_inicio': start_date.strftime('%d/%m/%Y')})
                except (ValueError, IndexError):
                    continue
            
            return sorted(leaves, key=lambda x: datetime.strptime(x['data_inicio'], '%d/%m/%Y'))
        except Exception as e:
            print(f"Erro ao buscar próximos afastamentos: {e}")
            return []
        
def batch_update_collaborators(matriculas, field_to_update, new_value):
    """Atualiza um campo específico para uma lista de colaboradores de uma só vez."""
    if not engine or not matriculas:
        return False, "Nenhum colaborador selecionado para atualização."
    
    # Lista de campos permitidos para evitar injeção de SQL no nome da coluna.
    # Garante que apenas estas colunas possam ser atualizadas em lote.
    allowed_fields = ["cargo", "setor", "escala", "tipo_turno", "horario_padrao"]
    if field_to_update.lower() not in allowed_fields:
        return False, f"O campo '{field_to_update}' não é permitido para edição em lote."
        
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # Construímos a query de forma segura
            query = text(f"UPDATE colaboradores SET {field_to_update} = :new_value WHERE matricula IN :matriculas_list")
            
            result = connection.execute(query, {
                "new_value": new_value, 
                "matriculas_list": tuple(matriculas)
            })
            
            trans.commit()
            return True, f"{result.rowcount} colaborador(es) atualizado(s) com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro de banco de dados: {e}"