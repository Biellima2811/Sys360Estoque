from database import db_manager as db
from core import logic_financeiro as lg_financeiro
import logging

def validar_produto_para_venda(id_str, qtd_str):
    if not id_str or not qtd_str: 
        raise ValueError("Preencha ID e Quantidade")
    try:
        id_prod = int(id_str)
        qtd = int(qtd_str)
    except: 
        raise ValueError("ID e Qtd devem ser números.")
    
    if qtd <= 0: 
        raise ValueError("Quantidade deve ser maior que zero.")
    
    prod = db.buscar_produto_por_id(id_prod) # (id, nome, qtd, preco...)
    if not prod: 
        raise ValueError("Produto não encontrado.")
    
    # prod[2] é a quantidade no banco
    if qtd > prod[2]: 
        raise ValueError(f"Estoque insuficiente! Disp: {prod[2]}")
        
    return prod, qtd

def processar_venda_completa(usuario_id, carrinho, cliente_id=None, valor_frete=0.0, metodo_pagto="Dinheiro", valor_pago=0.0, troco=0.0):
    """
    Processa venda recebendo dados de pagamento e troco.
    """
    if not carrinho: raise ValueError("Carrinho vazio.")
    if not usuario_id: raise ValueError("Erro de sessão.")
    
    # 1. Validação de Estoque
    total_produtos = 0.0
    for item in carrinho:
        p_id, _, qtd, _, sub = item
        produto_db = db.buscar_produto_por_id(p_id)
        if not produto_db:
             raise ValueError(f"Produto ID {p_id} não encontrado.")
        if qtd > produto_db[2]:
            raise ValueError(f"Estoque de '{item[1]}' acabou!")
        total_produtos += sub

    # 2. Calcula Total
    total_final = total_produtos + valor_frete

    try:
        # 3. Persiste no Banco (Com dados de pagto)
        venda_id = db.registrar_venda_transacao(
            usuario_id, total_final, carrinho, cliente_id, valor_frete,
            metodo_pagto, valor_pago, troco
        )
        
        # 4. Financeiro
        desc_fin = f"Venda #{venda_id} ({metodo_pagto})"
        if cliente_id: desc_fin += f" - Cli ID:{cliente_id}"
        if valor_frete > 0: desc_fin += " (+Frete)"
            
        lg_financeiro.registrar_movimentacao(
            descricao=desc_fin,
            valor=total_final,
            tipo='entrada',
            usuario_id=usuario_id,
            venda_id=venda_id
        )
        
        return venda_id
        
    except Exception as e:
        logging.error(f"Erro venda lógica: {e}")
        raise e