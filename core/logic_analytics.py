import sqlite3
from database import db_manager
from datetime import datetime, timedelta

def obter_vendas_ultimos_7_dias():
    conn = db_manager.conectar()

    if not conn: return []

    try:
        cursor = conn.cursor()
        # SQLite query para agrupar vendas por dia

        sql = """
            SELECT strftime('%d/%m', data_hora) as dia, SUM(total_venda) 
            FROM vendas 
            WHERE data_hora >= date('now', '-6 days')
            GROUP BY dia
            ORDER BY data_hora ASC
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        # Garante que dias sem vendas não quebrem o gráfico (opcional, aqui retornamos o que tem)
        return dados
    except Exception as e:
        print(f'Erro Analiticos Vendas: {e}')
        return []
    finally:
        conn.close()

def obter_top_5_produtos():
    """Retorna os 5 produtos mais vendidos (nome, qtd_total)"""
    conn = db_manager.conectar()
    if not conn: return []

    try:
        cursor = conn.cursor()
        sql = """
            SELECT p.nome, SUM(vi.quantidade) as total
            FROM venda_itens vi
            JOIN produtos p ON vi.produto_id = p.id
            GROUP BY p.id
            ORDER BY total DESC
            LIMIT 5
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()

def obter_balanco_financeiro():
    """Retorna (total_entradas, total_saidas)"""
    conn = db_manager.conectar()
    
    if not conn: return (0,0)

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT tipo, SUM(valor) FROM financeiro_movimentacoes GROUP BY tipo')
        rows = cursor.fetchall()

        entradas = 0.0
        saidas = 0.0

        for tipo, valor in rows:
            if tipo == 'entrada': entradas = valor
            elif tipo == 'saida': saidas = valor

        return (entradas, saidas)
    finally:
        conn.close()
        