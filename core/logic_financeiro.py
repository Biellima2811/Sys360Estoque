from database import db_manager as db
import logging
from datetime import datetime

def adicionar_categoria_padrao():
    """Cria categorias básicas se não existirem."""
    conn = db.conectar()
    if not conn: return

    try:
        cursor = conn.cursor()
        categorias = [
            ('Venda de Produtos', 'receita'),
            ('Pagamento de Fornecedor', 'despesa'),
            ('Conta de Energia', 'despesa'),
            ('Salário', 'despesa'),
            ('Frete/Transporte', 'despesa')
        ]

        for nome, tipo in categorias:
            # Tenta inserir, se já existir o nome (precisaria ser unique no banco, mas aqui validamos simples)
            cursor.execute("SELECT id FROM financeiro_categorias WHERE nome = ?", (nome,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO financeiro_categorias (nome, tipo) VALUES (?, ?)", (nome, tipo))
        conn.commit()
        logging.info("Categorias financeiras padrão verificadas.")
    except Exception as e:
        logging.error(f'Erro ao criar categorias padrão: {e}')
    finally:
        conn.close()

def registrar_movimentacao(descricao, valor, tipo, usuario_id, categoria_id=None, venda_id=None):
    """
    Registra uma entrada ou saída no caixa.
    """
    conn = db.conectar()
    if not conn: return

    try:
        if valor < 0:
            raise ValueError("O valor deve ser positivo. O tipo define se é entrada ou saída.")
        
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO financeiro_movimentacoes
                       (descricao, valor, tipo, usuario_id, categoria_id, venda_id)
                       VALUES (?, ?, ?, ?, ?, ?)""",(descricao, valor, tipo, usuario_id, categoria_id, venda_id))
        conn.commit()
        logging.info(f'Financeiro: {tipo.upper()} de R$ {valor} registrada. ({descricao})')
    except Exception as e:
        logging.error(f'Erro ao registrar movimentação financeira: {e}')
        raise e  # Repassa o erro para a tela exibir
    finally:
        conn.close()

def obter_saldo_atual():
    """Calcula Receitas - Despesas."""
    conn = db.conectar()
    if not conn: return 0.0

    try:
        cursor = conn.cursor()
        
        # Soma entradas
        cursor.execute("select sum(valor) from financeiro_movimentacoes where tipo = 'entrada'")
        entradas = cursor.fetchone()[0] or 0.0

        # Soma saídas
        cursor.execute("SELECT SUM(valor) FROM financeiro_movimentacoes WHERE tipo = 'saida'")
        saidas = cursor.fetchone()[0] or 0.0
        
        return entradas - saidas
    
    except Exception as e:
        logging.error(f'Erro ao calcular saldo: {e}')
        return 0.0
    finally:
        conn.close()

def listar_movimentacoes():
    """Lista todas as movimentações para exibir na tabela."""
    conn = db.conectar()
    if not conn: return[]

    try:
        cursor = conn.cursor()
        sql = """
            SELECT m.id, m.data_lancamento, m.descricao, m.tipo, m.valor, u.nome_completo
            FROM financeiro_movimentacoes m
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            ORDER BY m.data_lancamento DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        logging.error(f'Erro ao listar movimentações: {e}')
        return []
    finally:
        conn.close()