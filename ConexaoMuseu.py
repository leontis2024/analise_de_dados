import psycopg2
import random
from datetime import datetime, timedelta

def log_sync(conn, tabela, id_registro, operacao):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO log_geral (tabela, id_registro, operacao)
            VALUES (%s, %s, %s)
        """, (tabela, id_registro, operacao))
        conn.commit()
    except Exception as e:
        print(f"Erro ao logar a operação: {e}")
    finally:
        cur.close()

def generate_unique_id_endereco(conn):
    while True:
        id_endereco = random.randint(100, 999)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM endereco_museu WHERE id = %s", (id_endereco,))
        if not cur.fetchone():
            cur.close()
            return id_endereco
        cur.close()

def sync_museu_with_address(orig_conn, dest_conn, operation):
    try:
        orig_cur = orig_conn.cursor()
        dest_cur = dest_conn.cursor()

        if operation == 'DELETE':
            dest_cur.execute("TRUNCATE TABLE museu CASCADE")
            dest_cur.execute("TRUNCATE TABLE endereco_museu CASCADE")
            dest_conn.commit()
            print("Tabelas museu e endereco_museu truncadas devido à operação de exclusão.")

            # Repopulando todos os registros da tabela museu após a exclusão
            query_repopulate = """
            SELECT id, nm_museu, rua, cidade, estado, ponto_referencia, cep, nr_tel_museu, dt_inauguracao, cnpj, id_museu_adm, url_imagem
            FROM museu
            """
            orig_cur.execute(query_repopulate)
            registros = orig_cur.fetchall()
        else:
            query = """
            SELECT id, nm_museu, rua, cidade, estado, ponto_referencia, cep, nr_tel_museu, dt_inauguracao, cnpj, id_museu_adm, url_imagem
            FROM museu
            WHERE id IN (SELECT id_registro FROM log_geral WHERE tabela = 'museu' AND data_operacao >= NOW() - INTERVAL '30 minutes')
            """
            orig_cur.execute(query)
            registros = orig_cur.fetchall()

        for registro in registros:
            rua_completa = registro[2].split(',')
            rua = rua_completa[0].strip()
            num_museu = rua_completa[1].strip() if len(rua_completa) > 1 else 'S/N'

            dest_cur.execute("""
            SELECT id FROM endereco_museu
            WHERE rua = %s AND num_museu = %s AND cidade = %s AND estado = %s AND cep = %s
            """, (rua, num_museu, registro[3], registro[4], registro[6]))
            endereco_existe = dest_cur.fetchone()

            if endereco_existe:
                id_endereco = endereco_existe[0]
            else:
                id_endereco = generate_unique_id_endereco(dest_conn)
                endereco_query = """
                INSERT INTO endereco_museu (id, rua, num_museu, cidade, estado, ponto_referencia, cep)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                dest_cur.execute(endereco_query, (id_endereco, rua, num_museu, registro[3], registro[4], registro[5], registro[6]))
                dest_conn.commit()

            museu_query = """
            INSERT INTO museu (id, nm_museu, id_endereco, nr_tel_museu, dt_inauguracao, cnpj, id_museu_adm, url_imagem)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE 
            SET nm_museu = EXCLUDED.nm_museu, id_endereco = EXCLUDED.id_endereco, nr_tel_museu = EXCLUDED.nr_tel_museu,
                dt_inauguracao = EXCLUDED.dt_inauguracao, cnpj = EXCLUDED.cnpj, id_museu_adm = EXCLUDED.id_museu_adm, url_imagem = EXCLUDED.url_imagem;
            """
            dest_cur.execute(museu_query, (registro[0], registro[1], id_endereco, registro[7], registro[8], registro[9], registro[10], registro[11]))
            dest_conn.commit()
            print(f"Museu {registro[1]} sincronizado com sucesso.")

    except Exception as e:
        print(f"Erro ao sincronizar museu: {e}")
        dest_conn.rollback()
    finally:
        orig_cur.close()
        dest_cur.close()

def run_rpa():
    try:
        conn1 = psycopg2.connect(
            host="pg-2aed5b20-leontis2024-c492.l.aivencloud.com",
            database="dbLeontisPrimeiroAno",  
            user="avnadmin",
            port="23599",
            password="AVNS_I9sw4r5PMHAOdaMY_Yz"
        )

        conn2 = psycopg2.connect(
            host="pg-2aed5b20-leontis2024-c492.l.aivencloud.com",
            database="dbleontis",
            user="avnadmin",
            port="23599",
            password="AVNS_I9sw4r5PMHAOdaMY_Yz"
        )

        tabelas_primeiro_para_segundo = {
            'museu': (['id', 'nm_museu', 'rua', 'cidade', 'estado', 'ponto_referencia', 'cep', 'nr_tel_museu', 'dt_inauguracao', 'cnpj', 'id_museu_adm', 'url_imagem'], 
                      ['id', 'nm_museu', 'rua', 'cidade', 'estado', 'ponto_referencia', 'cep', 'nr_tel_museu', 'dt_inauguracao', 'cnpj', 'id_museu_adm', 'url_imagem'], 'id'),
        }

        for tabela, (colunas_origem, colunas_destino, pk) in tabelas_primeiro_para_segundo.items():
            orig_cur = conn1.cursor()
            orig_cur.execute(f"SELECT operacao FROM log_geral WHERE tabela = '{tabela}' AND data_operacao >= NOW() - INTERVAL '30 minutes' ORDER BY data_operacao DESC LIMIT 1;")
            operacao = orig_cur.fetchone()[0] if orig_cur.rowcount > 0 else 'INSERT'
            if tabela == 'museu':
                sync_museu_with_address(conn1, conn2, operacao)
            orig_cur.close()

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        conn1.close()
        conn2.close()

run_rpa()
