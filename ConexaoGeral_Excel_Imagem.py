import psycopg2
import pandas as pd
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

def atualizar_excel_obras(conn):
    try:
        # Lê os dados da tabela obra no banco de dados
        query = "SELECT id, nm_obra, url_imagem FROM obra"
        df = pd.read_sql(query, conn)

        # Caminho onde o arquivo Excel está salvo no OneDrive
        caminho_excel = r"C:\Users\neifejunior-ieg\OneDrive - Instituto J&F\Segundo Ano\Interdisciplinar II\BI\Bases\ObrasParaRedis.xlsx"

        # Escreve os dados no Excel
        df.to_excel(caminho_excel, index=False)
        print("Excel de obras atualizado com sucesso.")
    except Exception as e:
        print(f"Erro ao atualizar o Excel de obras: {e}")

def sync_table(orig_conn, dest_conn, tabela, colunas_origem, colunas_destino, pk, operation):
    try:
        orig_cur = orig_conn.cursor()
        dest_cur = dest_conn.cursor()

        if operation == 'DELETE':
            dest_cur.execute(f"TRUNCATE TABLE {tabela} CASCADE")
            dest_conn.commit()
            print(f"Tabela {tabela} truncada devido à operação de exclusão.")
            # Inserindo novamente todos os dados, exceto o deletado
            orig_cur.execute(f"SELECT {', '.join(colunas_origem)} FROM {tabela}")
            registros = orig_cur.fetchall()
        elif operation == 'UPDATE':
            dest_cur.execute(f"TRUNCATE TABLE {tabela} CASCADE")
            dest_conn.commit()
            print(f"Tabela {tabela} truncada devido à operação de atualização.")
            # Inserindo novamente todos os dados, exceto o deletado
            orig_cur.execute(f"SELECT {', '.join(colunas_origem)} FROM {tabela}")
            registros = orig_cur.fetchall()
        elif operation == 'INSERT':
            query = f"""
            SELECT {', '.join(colunas_origem)} 
            FROM {tabela}
            WHERE id IN (SELECT id_registro FROM log_geral WHERE tabela = '{tabela}' AND data_operacao >= NOW() - INTERVAL '30 minutes')
            """
            orig_cur.execute(query)
            registros = orig_cur.fetchall()
        else:
            "Entrou no Else."
        if not registros:
            print(f"Nenhuma alteração encontrada na tabela {tabela}.")
            return

        for registro in registros:
            dest_cur.execute(f"SELECT 1 FROM {tabela} WHERE {pk} = %s", (registro[colunas_origem.index(pk)],))
            if dest_cur.fetchone():
                print(f"Registro {registro[colunas_origem.index(pk)]} já existe na tabela {tabela}, pulando...")
                continue

            valores = ', '.join([f"%s" for _ in registro])
            on_conflict = ', '.join([f"{col}=EXCLUDED.{col}" for col in colunas_destino])
            insert_query = f"""
            INSERT INTO {tabela} ({', '.join(colunas_destino)})
            VALUES ({valores})
            ON CONFLICT ({pk}) DO UPDATE 
            SET {on_conflict}
            """
            dest_cur.execute(insert_query, registro)
            dest_conn.commit()
            print(f"Registro {registro[colunas_origem.index(pk)]} da tabela {tabela} sincronizado com sucesso.")
            log_sync(dest_conn, tabela, registro[colunas_origem.index(pk)], 'UPSERT')

#        if tabela == 'obra':
#            atualizar_excel_obras(orig_conn) # Comentado para não dar erro no BI ao atualizar o Excel

    except Exception as e:
        print(f"Erro ao sincronizar a tabela {tabela}: {e}")
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

        tabelas_segundo_para_primeiro1 = {
            'usuario': (['id', 'nm_usuario', 'sobrenome', 'email_usuario', 'nr_tel_usuario', 'dt_nasci_usuario', 'biografia', 'sexo', 'apelido', 'senha_usuario', 'url_imagem'],
                        ['id', 'nm_usuario', 'sobrenome', 'email_usuario', 'nr_tel_usuario', 'dt_nasci_usuario', 'biografia', 'sexo', 'apelido', 'senha_usuario', 'url_imagem'], 'id'),
            'museu_adm': (['id', 'email_adm', 'senha_adm'], ['id', 'email_adm', 'senha_adm'], 'id')
        }


        tabelas_primeiro_para_segundo = {
            'artista': (['id', 'nm_artista', 'dt_nasc_artista', 'dt_falecimento', 'local_nasc', 'local_morte', 'desc_artista', 'url_imagem'], ['id', 'nm_artista', 'dt_nasc_artista', 'dt_falecimento', 'local_nasc', 'local_morte', 'desc_artista', 'url_imagem'], 'id'),
            'genero': (['id', 'nm_genero', 'desc_genero', 'intro', 'url_imagem'], ['id', 'nm_genero', 'desc_genero', 'introducao', 'url_imagem'], 'id'),
            'guia': (['id', 'titulo_guia', 'desc_guia', 'id_museu', 'url_imagem'], ['id', 'titulo_guia', 'desc_guia', 'id_museu', 'url_imagem'], 'id'),
            'obra': (['id', 'ano_inicio', 'ano_final', 'desc_obra', 'nm_obra', 'id_genero', 'id_artista', 'id_museu', 'url_imagem'], ['id', 'ano_inicio', 'ano_final', 'desc_obra', 'nm_obra', 'id_genero', 'id_artista', 'id_museu', 'url_imagem'], 'id'),
            'artista_genero': (['id', 'id_artista', 'id_genero'], ['id', 'id_artista', 'id_genero'], 'id'),
            'dia_funcionamento': (['id', 'dia_semana', 'pr_dia_funcionamento', 'hr_inicio', 'hr_termino', 'id_museu'], ['id', 'dia_semana', 'pr_dia_funcionamento', 'hr_inicio', 'hr_termino', 'id_museu'], 'id'),
            'obra_guia': (['id', 'nr_ordem', 'desc_localizacao', 'id_obra', 'id_guia'], ['id', 'nr_ordem', 'desc_localizacao', 'id_obra', 'id_guia'], 'id')
        }

        tabelas_segundo_para_primeiro2 = {
            'usuario_genero': (['id', 'id_usuario', 'id_genero'], ['id', 'id_usuario', 'id_genero'], 'id'),
            'usuario_museu': (['id', 'id_usuario', 'id_museu'], ['id', 'id_usuario', 'id_museu'], 'id')
        }

        for tabela, (colunas_origem, colunas_destino, pk) in tabelas_segundo_para_primeiro1.items():
            orig_cur = conn2.cursor()
            orig_cur.execute(f"SELECT operacao FROM log_geral WHERE tabela = '{tabela}' AND data_operacao >= NOW() - INTERVAL '30 minutes' ORDER BY data_operacao DESC LIMIT 1;")
            operacao = orig_cur.fetchone()[0] if orig_cur.rowcount > 0 else 'INSERT'
            print(f"Verificando tabela: {tabela}")
            sync_table(conn2, conn1, tabela, colunas_origem, colunas_destino, pk, operacao)
            orig_cur.close()
        

        for tabela, (colunas_origem, colunas_destino, pk) in tabelas_primeiro_para_segundo.items():
            orig_cur = conn1.cursor()
            orig_cur.execute(f"SELECT operacao FROM log_geral WHERE tabela = '{tabela}' AND data_operacao >= NOW() - INTERVAL '30 minutes' ORDER BY data_operacao DESC LIMIT 1;")
            operacao = orig_cur.fetchone()[0] if orig_cur.rowcount > 0 else 'INSERT'
            print(f"Verificando tabela: {tabela}")
            sync_table(conn1, conn2, tabela, colunas_origem, colunas_destino, pk, operacao)
            orig_cur.close()

        for tabela, (colunas_origem, colunas_destino, pk) in tabelas_segundo_para_primeiro2.items():
            orig_cur = conn2.cursor()
            orig_cur.execute(f"SELECT operacao FROM log_geral WHERE tabela = '{tabela}' AND data_operacao >= NOW() - INTERVAL '30 minutes' ORDER BY data_operacao DESC LIMIT 1;")
            operacao = orig_cur.fetchone()[0] if orig_cur.rowcount > 0 else 'INSERT'
            print(f"Verificando tabela: {tabela}")
            sync_table(conn2, conn1, tabela, colunas_origem, colunas_destino, pk, operacao)
            orig_cur.close()

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        conn1.close()
        conn2.close()

run_rpa()
