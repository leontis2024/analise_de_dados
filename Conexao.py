import psycopg2
from datetime import datetime, timedelta

# Configurações para o Banco do Primeiro Ano e Segundo Ano
config_primeiro_ano = {
    'dbname': 'banco_primeiro_ano',
    'user': 'usuario_primeiro_ano',
    'password': 'senha_primeiro_ano',
    'host': 'localhost',
    'port': '5432'
}

config_segundo_ano = {
    'dbname': 'banco_segundo_ano',
    'user': 'usuario_segundo_ano',
    'password': 'senha_segundo_ano',
    'host': 'localhost',
    'port': '5432'
}

# Função para conectar ao banco de dados
def connect_to_db(config):
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para obter as tabelas alteradas nos últimos 30 minutos
def get_modified_tables(conn):
    cur = conn.cursor()
    query = """
        SELECT DISTINCT tabela
        FROM log_geral
        WHERE data_operacao > NOW() - INTERVAL '30 minutes';
    """
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    return [row[0] for row in result]

# Função para sincronizar os dados das tabelas alteradas
def sync_tables(conn_source, conn_target, table_name):
    cur_source = conn_source.cursor()
    cur_target = conn_target.cursor()

    # Consultar os dados da tabela alterada no banco de origem
    query = f"SELECT * FROM {table_name};"
    cur_source.execute(query)
    rows = cur_source.fetchall()

    if table_name == 'museu':
        # Sincronização especial para museu, separando o endereço no banco do segundo ano
        for row in rows:
            museu_id, nm_museu, desc_museu, rua, estado, cidade, ponto_referencia, cep, dt_inauguracao, nr_tel_museu = row
            
            # Primeiro inserir o endereço na tabela endereco_museu do segundo ano
            endereco_query = """
                INSERT INTO endereco_museu (rua, cep, cidade, estado, ponto_referencia)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """
            cur_target.execute(endereco_query, (rua, cep, cidade, estado, ponto_referencia))
            endereco_id = cur_target.fetchone()[0]
            
            # Depois inserir o museu com o id do endereço
            museu_query = """
                INSERT INTO museu (id, nm_museu, desc_museu, id_endereco, nr_tel_museu, dt_inauguracao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur_target.execute(museu_query, (museu_id, nm_museu, desc_museu, endereco_id, nr_tel_museu, dt_inauguracao))
    
    else:
        # Para outras tabelas, simplesmente sincronize os dados
        for row in rows:
            columns = ', '.join([f"%s" for _ in row])
            insert_query = f"INSERT INTO {table_name} VALUES ({columns})"
            cur_target.execute(insert_query, row)
    
    conn_target.commit()
    cur_source.close()
    cur_target.close()

# Função principal do RPA
def run_rpa():
    # Conectar ao banco de dados do primeiro e segundo ano
    conn_primeiro_ano = connect_to_db(config_primeiro_ano)
    conn_segundo_ano = connect_to_db(config_segundo_ano)

    if conn_primeiro_ano is None or conn_segundo_ano is None:
        print("Erro ao conectar aos bancos de dados.")
        return

    # Buscar as tabelas que sofreram alterações nos últimos 30 minutos
    modified_tables = get_modified_tables(conn_primeiro_ano)

    # Sincronizar as tabelas modificadas
    for table in modified_tables:
        print(f"Sincronizando tabela: {table}")
        sync_tables(conn_primeiro_ano, conn_segundo_ano, table)

    # Fechar as conexões
    conn_primeiro_ano.close()
    conn_segundo_ano.close()

# Agendando o RPA para rodar de 30 em 30 minutos
if __name__ == "__main__":
    while True:
        run_rpa()
        print("Aguardando 30 minutos para próxima execução...")
        time.sleep(1800)  # Espera 30 minutos
