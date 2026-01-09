from database import db_manager as db
import bcrypt
import re
from sqlite3 import Error
from core import logic_financeiro as lg_financeiro # <--- Import Novo
import logging # <--- Import Novo
# ==========================================================
# --- LÓGICA DE VENDAS (PDV) ---
# ==========================================================
def validar_produto_para_venda(id_str, qtd_str):
    if not id_str or not qtd_str: raise ValueError("Preencha ID e Quantidade")
    try:
        id_prod = int(id_str)
        qtd = int(qtd_str)
    except: raise ValueError("ID e Qtd devem ser números.")
    
    if qtd <= 0: raise ValueError("Quantidade deve ser maior que zero.")
    
    prod = db.buscar_produto_por_id(id_prod)
    if not prod: raise ValueError("Produto não encontrado.")
    
    if qtd > prod[2]: # prod[2] = estoque
        raise ValueError(f"Estoque insuficiente! Disp: {prod[2]}")
        
    return prod, qtd

def processar_venda_completa(usuario_id, carrinho, cliente_id=None):
    """
    Processa venda e envia para o DB.
    """
    if not carrinho: raise ValueError("Carrinho vazio.")
    if not usuario_id: raise ValueError("Erro de sessão.")
    
    # Valida estoque de novo (segurança)
    total_venda = 0.0
    for item in carrinho:
        p_id, _, qtd, preco, sub = item
        produto_db = db.buscar_produto_por_id(p_id)
        if not produto_db or qtd > produto_db[2]:
            raise ValueError(f"Estoque de '{item[1]}' acabou!")
        total_venda += sub

    try:
        # 1. Grava no Banco (Vendas + Estoque)
        venda_id = db.registrar_venda_transacao(usuario_id, total_venda, carrinho, cliente_id)
        
        # 2. Lança no Financeiro
        desc_fin = f"Venda PDV #{venda_id}"
        if cliente_id:
            desc_fin += f" (Cliente ID: {cliente_id})"
            
        lg_financeiro.registrar_movimentacao(
            descricao=desc_fin,
            valor=total_venda,
            tipo='entrada',
            usuario_id=usuario_id,
            venda_id=venda_id
        )
        return venda_id
    except Exception as e:
        logging.error(f"Erro venda: {e}")
        raise ValueError(f"Falha ao gravar venda: {e}")