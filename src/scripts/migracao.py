# migracao.py (VERSÃO QUE IGNORA DUPLICATAS)

import pandas as pd
from sqlalchemy import create_engine, text
import sys

# --- CONFIGURAÇÕES ---
DB_USER = "root"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "gerador_escala_db"
EXCEL_FILE_PATH = r"C:\Users\Alissongc\Downloads\Teste\ESCALABANCODEDADOS.xlsx"

print("--- INICIANDO SCRIPT DE MIGRAÇÃO ---")

# --- 1. CONEXÃO COM O BANCO DE DADOS ---
try:
    connection_string = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    print("Conexão com o MySQL estabelecida com sucesso.")
except Exception as e:
    print(f"ERRO: Não foi possível conectar ao banco de dados: {e}")
    sys.exit()

# --- 2. LEITURA DO ARQUIVO EXCEL ---
try:
    print(f"Lendo dados do arquivo Excel: {EXCEL_FILE_PATH}")
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="Cadastro_Colaboradores")
    print(f"Encontrados {len(df)} registros na planilha.")
except Exception as e:
    print(f"ERRO: Falha ao ler o arquivo Excel: {e}")
    sys.exit()

# --- 3. PREPARAÇÃO DOS DADOS ---
print("Preparando os dados para a migração...")
df_ativos = df[df["Ativo?"].str.strip().str.upper() == "SIM"].copy()
print(f"Filtrados {len(df_ativos)} colaboradores ativos.")

mapeamento_colunas = {
    "Nome": "nome", "Matrícula": "matricula", "Cargo": "cargo", "Setor": "setor",
    "Escala": "escala", "Tipo de Turno": "tipo_turno", "Resultado Esperado": "resultado_esperado",
    "Horário Padrão": "horario_padrao", "Conselho (opcional)": "coren",
    "Período de Afastamento": "periodo_afastamento"
}
df_ativos.rename(columns=mapeamento_colunas, inplace=True)
df_ativos['ativo'] = True
df_ativos['matricula'] = df_ativos['matricula'].astype(str)

# --- 3A. OPÇÃO: REMOVER DUPLICATAS AUTOMATICAMENTE ---
# Esta seção agora remove as duplicatas, mantendo apenas a primeira ocorrência de cada matrícula.
num_registros_antes = len(df_ativos)
df_ativos.drop_duplicates(subset=['matricula'], keep='first', inplace=True)
num_registros_depois = len(df_ativos)

if num_registros_antes > num_registros_depois:
    removidos = num_registros_antes - num_registros_depois
    print(f"AVISO: {removidos} matrícula(s) duplicada(s) foi(ram) encontrada(s) e ignorada(s). Apenas o primeiro registro de cada foi mantido.")

# --- 4. INSERÇÃO DOS DADOS NO MYSQL ---
try:
    with engine.connect() as connection:
        print("Limpando a tabela 'colaboradores' antes de inserir novos dados...")
        connection.execute(text("TRUNCATE TABLE colaboradores"))
        if hasattr(connection, 'commit'):
            connection.commit()

    colunas_para_db = [col for col in mapeamento_colunas.values() if col in df_ativos.columns]
    if 'ativo' not in colunas_para_db:
        colunas_para_db.append('ativo')
    df_final = df_ativos[colunas_para_db]

    print(f"Inserindo {len(df_final)} registros únicos na tabela 'colaboradores'...")
    df_final.to_sql('colaboradores', con=engine, if_exists='append', index=False)
    print("\nDADOS MIGRADOS COM SUCESSO!")

except Exception as e:
    print(f"ERRO: Falha ao inserir dados no MySQL: {e}")

print("--- SCRIPT DE MIGRAÇÃO CONCLUÍDO ---")