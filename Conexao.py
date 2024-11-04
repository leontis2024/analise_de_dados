import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta

# Função para verificar se houve atividades recentes na tabela de log
def verificar_atividades_recentes(cur2):
    agora = datetime.now()
    dois_minutos_atras = agora - timedelta(minutes=100000)
    
    cur2.execute("""
        SELECT DISTINCT tabela FROM log_geral
        WHERE data_operacao >= %s
    """, (dois_minutos_atras,))
    
    tabelas_afetadas = cur2.fetchall()
    print(f"Atividades recentes detectadas nas tabelas: {tabelas_afetadas}")  # Debug
    return [tabela[0] for tabela in tabelas_afetadas]

# Função de sincronização das tabelas
def sync_tabelas(cur1, cur2, tabelas):
    tabelas_a_sincronizar = {
        'artista': 'id, nm_artista, dt_nasc_artista, dt_falecimento, local_nasc, local_morte, desc_artista',
        'genero': 'id, nm_genero, introducao, desc_genero',
        'usuario': 'id, nm_usuario, sobrenome, email_usuario, nr_tel_usuario, dt_nasci_usuario, biografia, sexo, apelido, senha_usuario',
        'obra': 'id, nm_obra, desc_obra, ano_inicio, ano_final, id_genero, id_artista, id_museu',
        'guia': 'id, titulo_guia, desc_guia, id_museu',
        'dia_funcionamento': 'id, hr_inicio, hr_termino, pr_dia_funcionamento, dia_semana, id_museu',
        'museu': 'id, nm_museu, desc_museu, id_endereco, dt_inauguracao, nr_tel_museu',
        'endereco_museu': 'id, rua, cep, num_museu, cidade, estado, ponto_referencia',
        'usuario_museu': 'id, id_museu, id_usuario',
        'obra_guia': 'id, id_guia, id_obra, nr_ordem, desc_localizacao',
        'artista_genero': 'id, id_artista, id_genero',
        'usuario_genero': 'id, id_usuario, id_genero'
    }

    for tabela in tabelas:
        if tabela in tabelas_a_sincronizar:
            colunas = tabelas_a_sincronizar[tabela]
            cur2.execute(sql.SQL("SELECT {} FROM {}").format(sql.SQL(colunas), sql.Identifier(tabela)))
            dados = cur2.fetchall()

            for linha in dados:
                placeholders = ', '.join(['%s'] * len(linha))
                colunas_lista = colunas.split(', ')

                cur1.execute(sql.SQL("SELECT id FROM {} WHERE id = %s").format(sql.Identifier(tabela)), (linha[0],))
                result = cur1.fetchone()

                if result:
                    try:
                        update_query = sql.SQL("""
                            UPDATE {} SET {} WHERE id = %s
                        """).format(
                            sql.Identifier(tabela),
                            sql.SQL(', ').join([sql.SQL("{} = %s".format(colunas_lista[i])) for i in range(1, len(colunas_lista))])
                        )
                        cur1.execute(update_query, (*linha[1:], linha[0]))
                        print(f"Tabela {tabela}: Linha com id {linha[0]} atualizada com sucesso.")  # Debug
                    except Exception as e:
                        print(f"Erro ao atualizar {tabela}: {e}")
                        print(f"Linha: {linha}")
                        print(f"Colunas: {colunas_lista[1:]}")
                else:
                    insert_query = sql.SQL("""
                        INSERT INTO {} ({}) VALUES ({})
                    """).format(
                        sql.Identifier(tabela),
                        sql.SQL(', '.join(colunas_lista)),
                        sql.SQL(placeholders)
                    )
                    cur1.execute(insert_query, linha)
                    print(f"Tabela {tabela}: Nova linha com id {linha[0]} inserida com sucesso.")  # Debug

            conn1.commit()

# Conexão com o banco do segundo ano
try:
    conn2 = psycopg2.connect(
        host="pg-2aed5b20-leontis2024-c492.l.aivencloud.com",
        database="dbleontis",
        user="avnadmin",
        port="23599",
        password="AVNS_I9sw4r5PMHAOdaMY_Yz"
    )

    # Conexão com o banco do primeiro ano
    conn1 = psycopg2.connect(
        host="pg-2aed5b20-leontis2024-c492.l.aivencloud.com",
        database="dbLeontisPrimeiroAno",
        user="avnadmin",
        port="23599",
        password="AVNS_I9sw4r5PMHAOdaMY_Yz"
    )

    # Criando cursores para executar comandos SQL
    cur2 = conn2.cursor()
    cur1 = conn1.cursor()

    # Verificar atividades recentes na tabela de log (no banco do segundo ano)
    tabelas_afetadas = verificar_atividades_recentes(cur2)

    # Se houver tabelas afetadas, sincronizar
    if tabelas_afetadas:
        sync_tabelas(cur1, cur2, tabelas_afetadas)
    else:
        print("Nenhuma atividade recente encontrada.")

finally:
    # Fechar conexões
    cur2.close()
    conn2.close()
    cur1.close()
    conn1.close()

print("Processo de sincronização concluído.")
