import mysql.connector
import bcrypt
import pandas as pd
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text

# --- CONFIGURAÇÕES DE BANCO DE DADOS (CORRIGIDO) ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "port": "3306",
    "database": "gerador_escala_db",
}


def _get_engine():
    """Cria e retorna o motor de conexão do SQLAlchemy."""
    try:
        connection_string = (
            f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        return create_engine(connection_string)
    except Exception as e:
        print(f"ERRO CRÍTICO: Falha ao criar o motor de conexão: {e}")
        return None


def setup_database():
    """Garante que o banco de dados e todas as tabelas necessárias existam."""
    try:
        # 1. Conecta ao MySQL sem especificar o banco de dados
        db_connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
        )
        cursor = db_connection.cursor()

        # 2. Cria o banco de dados se ele não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(
            f"Banco de dados '{DB_CONFIG['database']}' verificado/criado com sucesso."
        )

        cursor.close()
        db_connection.close()

        # 3. Agora conecta ao banco específico para criar as tabelas
        engine = _get_engine()
        with engine.connect() as connection:
            trans = connection.begin()

            # --- Definição das Tabelas ---
            tabela_usuarios = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                foto_path VARCHAR(255) NULL
            );"""

            tabela_colaboradores = """
            CREATE TABLE IF NOT EXISTS colaboradores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                matricula VARCHAR(50) NOT NULL UNIQUE,
                cargo VARCHAR(100),
                setor VARCHAR(100),
                escala VARCHAR(50),
                tipo_turno VARCHAR(50),
                conselho VARCHAR(50),
                ativo BOOLEAN DEFAULT TRUE,
                escala_data_base DATE NULL DEFAULT NULL,
                escala_sequencia_atual VARCHAR(10) DEFAULT 'IMPAR',
                afastamento_inicio DATE NULL DEFAULT NULL,
                afastamento_fim DATE NULL DEFAULT NULL,
                afastamento_motivo VARCHAR(255)
            );"""

            tabela_escalas_geradas = """
            CREATE TABLE IF NOT EXISTS escalas_geradas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                colaborador_matricula VARCHAR(50) NOT NULL,
                data_turno DATE NOT NULL,
                hora_inicio TIME NULL,
                hora_fim TIME NULL,
                mes_referencia INT NOT NULL,
                ano_referencia INT NOT NULL,
                data_geracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_colaborador_data (colaborador_matricula, ano_referencia, mes_referencia),
                FOREIGN KEY (colaborador_matricula) REFERENCES colaboradores(matricula) ON DELETE CASCADE
            );"""

            # Executa a criação das tabelas
            connection.execute(text(tabela_usuarios))
            connection.execute(text(tabela_colaboradores))
            connection.execute(text(tabela_escalas_geradas))

            trans.commit()
            print("Tabelas verificadas/criadas com sucesso.")

    except Exception as e:
        print(f"ERRO CRÍTICO no setup do banco de dados: {e}")
        return None


# --- Executa o setup e cria o motor principal ---
setup_database()
engine = _get_engine()


def get_user_by_username(username):
    """Busca um usuário pelo nome de usuário e retorna seus dados."""
    if not engine:
        return None

    with engine.connect() as connection:
        query = text("SELECT *, foto_path FROM usuarios WHERE username = :user")
        result = connection.execute(query, {"user": username}).fetchone()
        return result._asdict() if result else None


def add_user(username, password, role, photo_path=None):
    """Adiciona um novo usuário ao banco de dados com senha criptografada."""
    if not engine:
        return False, "Motor de conexão com o banco de dados não está disponível."
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            query = text(
                "INSERT INTO usuarios (username, password_hash, role,  foto_path) VALUES (:user, :pwd_hash, :role, :photo)"
            )
            connection.execute(
                query,
                {
                    "user": username,
                    "pwd_hash": hashed_password.decode("utf-8"),
                    "role": role,
                    "photo": photo_path,
                },
            )
            trans.commit()
            return True, f"Usuário '{username}' criado com sucesso!"
        except Exception as e:
            trans.rollback()
            if "Duplicate entry" in str(e):
                return False, f"Erro: O nome de usuário '{username}' já existe."
            return False, f"Erro de banco de dados: {e}"


def add_colaborador(dados_colaborador):
    """Adiciona um novo colaborador ao banco de dados."""
    if not engine:
        return False, "Motor de conexão com o banco de dados não está disponível."
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            sql = text(
                """
                INSERT INTO colaboradores 
                (nome, matricula, cargo, setor, escala, tipo_turno, conselho, 
                afastamento_inicio, afastamento_fim, afastamento_motivo, ativo) 
                VALUES (:nome, :matricula, :cargo, :setor, :escala, :tipo_turno,:conselho,
                :afastamento_inicio, :afastamento_fim, :afastamento_motivo, :ativo)
            """
            )
            # Usa .get() com None como padrão para os campos que podem vir vazios
            params = {
                "nome": dados_colaborador.get("Nome"),
                "matricula": dados_colaborador.get("Matrícula"),
                "cargo": dados_colaborador.get("Cargo"),
                "setor": dados_colaborador.get("Setor"),
                "escala": dados_colaborador.get("Escala"),
                "tipo_turno": dados_colaborador.get("Tipo de Turno"),
                "conselho": dados_colaborador.get("conselho (opcional)"),
                "afastamento_inicio": dados_colaborador.get("Início do Afastamento")
                or None,
                "afastamento_fim": dados_colaborador.get("Fim do Afastamento") or None,
                "afastamento_motivo": dados_colaborador.get("Motivo do Afastamento")
                or None,
                "ativo": True,
            }
            connection.execute(sql, params)
            trans.commit()
            return (
                True,
                f"Colaborador '{dados_colaborador.get('Nome')}' cadastrado com sucesso!",
            )
        except Exception as e:
            trans.rollback()
            if "Duplicate entry" in str(e):
                return (
                    False,
                    f"Erro: A matrícula '{dados_colaborador.get('Matrícula')}' já existe.",
                )
            return False, f"Erro de banco de dados: {e}"


def get_all_collaborators_dataframe(search_term=None):
    """Busca os colaboradores, opcionalmente filtrando, e retorna como DataFrame."""
    if not engine:
        return pd.DataFrame()

    # A construção da query está correta
    query_str = """
        SELECT nome, matricula, cargo, setor, escala
        FROM colaboradores WHERE ativo = TRUE
    """
    params = {}

    if search_term:
        query_str += " AND (nome LIKE :term OR matricula LIKE :term OR cargo LIKE :term OR setor LIKE :term)"
        params["term"] = f"%{search_term}%"
        
    query_str += " ORDER BY nome"

    try:
        # --- A CORREÇÃO ESTÁ AQUI ---
        # Envolvemos a string da query com a função text() do SQLAlchemy
        # para garantir que os parâmetros sejam processados corretamente.
        df = pd.read_sql(text(query_str), engine, params=params)
        return df
    except Exception as e:
        print(f"Erro ao executar a pesquisa no banco de dados: {e}")
        return pd.DataFrame()


def get_collaborator_by_matricula(matricula):
    """Busca os dados de um colaborador, incluindo os campos de afastamento."""
    if not engine:
        return None
    with engine.connect() as connection:
        query = text("SELECT * FROM colaboradores WHERE matricula = :matricula")
        result = connection.execute(query, {"matricula": matricula}).fetchone()
        return result._asdict() if result else None


def delete_collaborators_by_matriculas(matriculas):
    """Deleta múltiplos colaboradores do banco de uma só vez."""
    if not matriculas:
        return False, "Nenhuma matrícula fornecida para exclusão."
    if not engine:
        return False, "Motor de conexão não está disponível."

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # 1. Cria placeholders nomeados para a cláusula IN (ex: :m_0, :m_1, ...)
            # Isso é crucial para a segurança e evita injeção de SQL.
            in_placeholders = ", ".join([f":m_{i}" for i in range(len(matriculas))])

            # 2. Constrói a query final
            query_str = (
                f"DELETE FROM colaboradores WHERE matricula IN ({in_placeholders})"
            )

            # 3. Monta o dicionário de parâmetros para o SQLAlchemy
            # (Ex: {'m_0': '123', 'm_1': '456'})
            params = {f"m_{i}": mat for i, mat in enumerate(matriculas)}

            # 4. Executa a query com os parâmetros
            result = connection.execute(text(query_str), params)

            trans.commit()
            return True, f"{result.rowcount} colaborador(es) excluído(s) com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro de banco de dados ao excluir em lote: {e}"


def update_collaborator(matricula, data):
    """Atualiza os dados de um colaborador existente."""
    if not engine or not data:
        return False, "Nenhum dado fornecido para atualização."

    # --- LÓGICA CORRIGIDA ---

    # 1. Remove a matrícula do dicionário de dados, pois ela é a chave de busca.
    data.pop("matricula", None)

    # 2. Se não houver mais nada para atualizar, retorna.
    if not data:
        return True, "Nenhuma alteração para salvar."

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # 3. Constrói a cláusula SET dinamicamente com TODOS os dados recebidos.
            # Agora, se um campo for None (ex: afastamento_inicio), ele será SETado para NULL no banco.
            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query_str = f"UPDATE colaboradores SET {set_clause} WHERE matricula = :original_matricula"

            params = data  # Usa o dicionário 'data' diretamente
            params["original_matricula"] = matricula

            connection.execute(text(query_str), params)
            trans.commit()
            return True, "Colaborador atualizado com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro de banco de dados: {e}"


def get_dashboard_stats():
    """Busca estatísticas rápidas para o dashboard usando SQLAlchemy."""
    stats = {"total_colaboradores": 0, "total_setores": 0}
    if not engine:
        return stats

    with engine.connect() as connection:
        try:
            query_colab = text("SELECT COUNT(id) FROM colaboradores WHERE ativo = TRUE")
            stats["total_colaboradores"] = (
                connection.execute(query_colab).scalar_one_or_none() or 0
            )

            query_setor = text(
                "SELECT COUNT(DISTINCT setor) FROM colaboradores WHERE ativo = TRUE"
            )
            stats["total_setores"] = (
                connection.execute(query_setor).scalar_one_or_none() or 0
            )

            return stats
        except Exception as e:
            print(f"Erro ao buscar estatísticas do dashboard: {e}")
            return {"total_colaboradores": 0, "total_setores": 0}


def get_upcoming_leaves(days_ahead=30):
    """Busca TODOS os afastamentos que começarão nos próximos X dias a partir de hoje."""
    if not engine:
        return []

    with engine.connect() as connection:
        query = text(
            """
            SELECT nome, afastamento_inicio, afastamento_fim
            FROM colaboradores
            WHERE ativo = 1
            AND afastamento_inicio IS NOT NULL AND afastamento_fim IS NOT NULL
            AND afastamento_fim >= CURDATE()
            AND afastamento_inicio <= DATE_ADD(CURDATE(), INTERVAL :days DAY)
            ORDER BY afastamento_inicio ASC
        """
        )
        # Usa .fetchall() para pegar TODAS as linhas, não apenas a primeira
        result = connection.execute(query, {"days": days_ahead}).fetchall()
        return [row._asdict() for row in result]


def batch_update_collaborators(matriculas, field_to_update, new_value):
    """Atualiza um campo específico para uma lista de colaboradores de uma só vez."""
    if not engine or not matriculas:
        return False, "Nenhum colaborador selecionado para atualização."

    allowed_fields = ["cargo", "setor", "escala", "tipo_turno"]
    if field_to_update.lower() not in allowed_fields:
        return (
            False,
            f"O campo '{field_to_update}' não é permitido para edição em lote.",
        )

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # --- LÓGICA DE QUERY CORRIGIDA E ROBUSTA ---

            # 1. Cria placeholders nomeados para a cláusula IN (ex: :m_0, :m_1, ...)
            in_placeholders = ", ".join([f":m_{i}" for i in range(len(matriculas))])

            # 2. Constrói a query final usando o formato de parâmetro nomeado
            query_str = f"UPDATE colaboradores SET {field_to_update} = :new_value WHERE matricula IN ({in_placeholders})"

            # 3. Monta o dicionário de parâmetros
            params = {"new_value": new_value}
            # Adiciona os valores das matrículas ao dicionário (ex: {'m_0': '123', 'm_1': '456'})
            matriculas_dict = {f"m_{i}": mat for i, mat in enumerate(matriculas)}
            params.update(matriculas_dict)

            # 4. Executa a query com o dicionário de parâmetros
            result = connection.execute(text(query_str), params)

            trans.commit()
            return True, f"{result.rowcount} colaborador(es) atualizado(s) com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro de banco de dados: {e}"


def get_all_active_collaborators(filtros=None):
    """
    Busca colaboradores ativos, aplicando filtros opcionais.
    Filtros é um dicionário: {'escala_types': ['12x36'], 'matriculas': ['123']}
    """
    if not engine:
        return []

    params = {}
    query_str = """
        SELECT matricula, nome, escala, escala_data_base, escala_sequencia_atual,
               afastamento_inicio, afastamento_fim
        FROM colaboradores
        WHERE ativo = 1
    """
    if filtros:
        if filtros.get("escala_types"):
            in_placeholders = ", ".join(
                [f":escala_{i}" for i in range(len(filtros["escala_types"]))]
            )
            query_str += f" AND escala IN ({in_placeholders})"
            params.update(
                {f"escala_{i}": val for i, val in enumerate(filtros["escala_types"])}
            )

        if filtros.get("matriculas"):
            in_placeholders = ", ".join(
                [f":mat_{i}" for i in range(len(filtros["matriculas"]))]
            )
            query_str += f" AND matricula IN ({in_placeholders})"
            params.update(
                {f"mat_{i}": val for i, val in enumerate(filtros["matriculas"])}
            )

        if filtros.get("setores"):
            in_placeholders = ", ".join(
                [f":setor_{i}" for i in range(len(filtros["setores"]))]
            )
            query_str += f" AND setor IN ({in_placeholders})"
            params.update(
                {f"setor_{i}": val for i, val in enumerate(filtros["setores"])}
            )
    query_str += " ORDER BY nome"

    with engine.connect() as connection:
        query = text(query_str)
        result = connection.execute(query, params).fetchall()
        return [row._asdict() for row in result]


def get_unconfigured_collaborators():
    """Busca colaboradores com escalas cíclicas que não têm uma data base definida."""
    if not engine:
        return []
    with engine.connect() as connection:
        # Seleciona apenas os que têm escalas conhecidas que precisam de data base
        query = text(
            """
            SELECT matricula, nome, escala
            FROM colaboradores
            WHERE ativo = TRUE
            AND escala IN ('12x36', '24x72', '24x120')
            AND escala_data_base IS NULL
        """
        )
        result = connection.execute(query).fetchall()
        return [row._asdict() for row in result]


def update_collaborator_base_dates(updates):
    """
    Atualiza a escala_data_base para múltiplos colaboradores.
    'updates' deve ser um dicionário como: {'matricula': 'YYYY-MM-DD', ...}
    """
    if not engine or not updates:
        return False, "Nenhum dado para atualizar."

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            for matricula, data_base in updates.items():
                query = text(
                    """
                    UPDATE colaboradores
                    SET escala_data_base = :data_base
                    WHERE matricula = :matricula
                """
                )
                connection.execute(
                    query, {"data_base": data_base, "matricula": matricula}
                )
            trans.commit()
            return True, "Datas de referência salvas com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro ao salvar datas de referência: {e}"


def update_sequencia_colaborador(matricula, nova_sequencia):
    """Atualiza a coluna escala_sequencia_atual para um colaborador específico."""
    if not engine:
        return False, "Motor de conexão não está disponível."

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            query = text(
                """
                UPDATE colaboradores 
                SET escala_sequencia_atual = :nova_sequencia 
                WHERE matricula = :matricula
            """
            )
            connection.execute(
                query, {"nova_sequencia": nova_sequencia, "matricula": matricula}
            )
            trans.commit()
            return True, "Sequência atualizada com sucesso."
        except Exception as e:
            trans.rollback()
            return False, f"Erro ao atualizar sequência: {e}"


def salvar_escala_no_historico(dados_escala, ano, mes):
    """
    Salva uma escala gerada na tabela 'escalas_geradas'.
    Primeiro, apaga qualquer escala antiga para o mesmo período/colaboradores.
    """
    if not engine or not dados_escala:
        return False, "Nenhum dado de escala para salvar."

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # Pega a lista de matrículas da escala gerada
            matriculas_na_escala = list(dados_escala.keys())

            # 1. (Opcional, mas recomendado) Deleta o histórico antigo para este mês/ano/colaboradores
            # para evitar duplicatas se o usuário gerar e salvar várias vezes.
            delete_query = text(
                """
                DELETE FROM escalas_geradas 
                WHERE ano_referencia = :ano AND mes_referencia = :mes AND colaborador_matricula IN :matriculas
            """
            )
            connection.execute(
                delete_query,
                {"ano": ano, "mes": mes, "matriculas": matriculas_na_escala},
            )

            # 2. Insere os novos registros
            insert_query = text(
                """
                INSERT INTO escalas_geradas 
                (colaborador_matricula, data_turno, mes_referencia, ano_referencia) 
                VALUES (:matricula, :data_turno, :mes, :ano)
            """
            )

            registros_para_inserir = []
            for matricula, info in dados_escala.items():
                for dia in info.get("dias", []):
                    # O 'dia' aqui é um dicionário {'dia': X, 'turno': 'Y'}
                    data_do_turno = date(ano, mes, dia["dia"])
                    registros_para_inserir.append(
                        {
                            "matricula": matricula,
                            "data_turno": data_do_turno.strftime("%Y-%m-%d"),
                            "mes": mes,
                            "ano": ano,
                        }
                    )

            if registros_para_inserir:
                connection.execute(insert_query, registros_para_inserir)

            trans.commit()
            return True, f"Escala de {mes}/{ano} salva com sucesso no histórico."
        except Exception as e:
            trans.rollback()
            return False, f"Erro ao salvar histórico: {e}"


def get_distinct_escala_types():
    """Busca todos os tipos de escala únicos cadastrados para os colaboradores ativos."""
    if not engine:
        return []
    with engine.connect() as connection:
        query = text(
            """
            SELECT DISTINCT escala 
            FROM colaboradores 
            WHERE ativo = 1 AND escala IS NOT NULL AND escala != ''
            ORDER BY escala
        """
        )
        result = connection.execute(query).fetchall()
        return [row[0] for row in result]


def get_distinct_setores():
    """Busca todos os setores únicos cadastrados para os colaboradores ativos."""
    if not engine:
        return []
    with engine.connect() as connection:
        query = text(
            """
            SELECT DISTINCT setor 
            FROM colaboradores 
            WHERE ativo = 1 AND setor IS NOT NULL AND setor != ''
            ORDER BY setor
        """
        )
        result = connection.execute(query).fetchall()
        return [row[0] for row in result]
