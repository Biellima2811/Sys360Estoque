from database import db_manager as db
import bcrypt
import re
from sqlite3 import Error
from core import logic_financeiro as lg_financeiro # <--- Import Novo
import logging # <--- Import Novo
# ==========================================================
# --- LÓGICA DE VENDAS (PDV) ---
# ==========================================================
def validar_produto_para_venda(id_produto_str, qtd_desejada_str):
    """
    Verifica se um produto pode ser vendido (valida ID, qtd e estoque).
    Lança ValueError se algo estiver errado.
    Retorna (produto_tupla, qtd_int) se for válido.
    """
    # 1. Validação de entrada
    if not id_produto_str or not qtd_desejada_str:
        raise ValueError("ID do produto e Quantidade são obrigatorios!")
    try:
        id_produto = int(id_produto_str)
        qtd_desejada = int(qtd_desejada_str)
    except ValueError:
        raise ValueError("ID e quantidade devem ser números inteiros.")

    if qtd_desejada <= 0:
        raise ValueError('A quantidade deve ser maior que zero.')
    
    # 2. Validação de Regra de Negócio (Estoque)
    # Usamos a nova função do database.py
    produto = db.buscar_produto_por_id(id_produto)

    if produto is None:
        raise ValueError(f'Produto com ID {id_produto} não encontrado!')
    
    # O produto é uma tupla: (id, nome, quantidade, preco)
    # Índice [2] é a quantidade em estoque
    qtd_estoque = produto[2]

    if qtd_desejada > qtd_estoque:
        raise ValueError(f"Estoque insuficiente para '{produto[1]}'. \n"
                         f"Diponivel: {qtd_estoque} | Desejado: {qtd_desejada}")
    
    # 3. Sucesso!
    # Retorna os dados do produto e a quantidade validada
    print(f"Produto validado para venda: {produto[1]}, Qtd: {qtd_desejada}")
    return produto, qtd_desejada

def processar_venda_completa(usuario_id, carrinho):
    """
    Processa o "carrinho" final e chama a transação do banco.
    'carrinho' é uma lista de tuplas: [(id_produto, nome, qtd, preco, subtotal), ...]
    """
    logging.info(f"Iniciando processamento de venda para usuário {usuario_id}")
    print('Re-validando estoque antes da transação, favor aguarde...')

    # 1. Validação final
    if not carrinho:
        raise ValueError('O carrinho está vazio. Adicione produtos para finalizar a venda.')
    
    if not usuario_id:
        raise ValueError('Usuário não identificado. Faça login novamente.')

    # 2. (Opcional, mas recomendado) Re-validar todo o estoque
    # Isso previne que duas pessoas vendam o mesmo item ao mesmo tempo. 
    # --- INÍCIO DO LOOP (ETAPA 2) ---
    for item in carrinho:
        produto_id = item[0]
        qtd_vendida = item[2]
        produto_db = db.buscar_produto_por_id(produto_id) # Use buscar_produto_por_id (do db_manager)
        
        if produto_db is None:
            raise ValueError(f"Erro critico: Produto '{item[1]}' (ID: {produto_id} não existe mais.)")
        
        if qtd_vendida > produto_db[2]: # produto_db[2] é a qtd
            raise ValueError(f"Estoque de '{produto_db[1]}' mudou durante a venda!\n"
                             f"Disponível: {produto_db[2]} | No carrinho: {qtd_vendida}")
    # --- FIM DO LOOP (ETAPA 2) ---

    # 3. Calcular o total final (CORRETO: FORA DO LOOP)
    total_venda = 0.0
    for item in carrinho:
        total_venda += item[4] # item[4] é o subtotal (qtd * preco)
    print(f"Total calculado: {total_venda}")

    # 4. Enviar para a camada de dados (CORRETO: FORA DO LOOP)
    try:
        # 1. Registrar a Venda e Baixar Estoque (DB Transaction)
        venda_id = db.registrar_venda_transacao(usuario_id, total_venda, carrinho)
        
        # 2. Registrar no Financeiro (AUTOMÁTICO)
        # Tenta pegar o ID da categoria "Venda de Produtos" (geralmente é 1 se rodou o script)
        # Por simplificação, vamos passar None no categoria_id por enquanto ou implementar busca
        lg_financeiro.registrar_movimentacao(
            descricao=f"Venda PDV #{venda_id}",
            valor=total_venda,
            tipo='entrada',
            usuario_id=usuario_id,
            venda_id=venda_id
        )
        
        logging.info(f"Venda {venda_id} concluída com sucesso. Total: {total_venda}")
        return venda_id
    
    except Exception as e:
        logging.error(f"Falha ao processar venda completa: {e}")
        raise ValueError(f"Erro ao processar venda: {e}")