# ==========================================================
# IMPORTAÇÕES E BIBLIOTECAS
# ==========================================================

from database import db_manager as db  
# Módulo responsável por interagir com o banco de dados.
# Funções como buscar produto, registrar venda, etc.
# Aqui é apelidado como "db" para facilitar o uso.

import bcrypt  
# Biblioteca para criptografia de senhas.
# Permite gerar hashes seguros e verificar senhas.

import re  
# Biblioteca padrão para expressões regulares.
# Usada para validar/manipular strings (ex.: emails, CPFs).

from sqlite3 import Error  
# Classe de erro específica do SQLite.
# Usada para capturar/tratar falhas em operações de banco.

from core import logic_financeiro as lg_financeiro  # <--- Import Novo
# Módulo de lógica financeira.
# Responsável por registrar movimentações financeiras (entradas/saídas).
# Apelidado como "lg_financeiro".

import logging  # <--- Import Novo
# Biblioteca padrão para logs.
# Permite registrar erros, avisos e informações em arquivos ou console.


# ==========================================================
# --- LÓGICA DE VENDAS (PDV) ---
# ==========================================================

def validar_produto_para_venda(id_str, qtd_str):
    """
    Função que valida se um produto pode ser vendido.
    - Verifica se ID e quantidade foram preenchidos.
    - Converte ambos para inteiros.
    - Garante que a quantidade seja maior que zero.
    - Busca produto no banco de dados.
    - Confere se há estoque suficiente.
    Retorna: (produto, quantidade)
    """
    if not id_str or not qtd_str: 
        raise ValueError("Preencha ID e Quantidade")
    try:
        id_prod = int(id_str)
        qtd = int(qtd_str)
    except: 
        raise ValueError("ID e Qtd devem ser números.")
    
    if qtd <= 0: 
        raise ValueError("Quantidade deve ser maior que zero.")
    
    prod = db.buscar_produto_por_id(id_prod)
    if not prod: 
        raise ValueError("Produto não encontrado.")
    
    if qtd > prod[2]:  # prod[2] = estoque
        raise ValueError(f"Estoque insuficiente! Disp: {prod[2]}")
        
    return prod, qtd


def processar_venda_completa(usuario_id, carrinho, cliente_id=None, valor_frete=0.0):
    """
    Função que processa uma venda completa no PDV.
    Etapas:
    1. Valida carrinho e sessão do usuário.
    2. Confere estoque de cada produto no carrinho.
    3. Calcula total final (produtos + frete).
    4. Registra venda no banco (db.registrar_venda_transacao).
    5. Registra movimentação financeira (lg_financeiro.registrar_movimentacao).
    6. Retorna o ID da venda.
    Em caso de erro, registra no log e repassa a exceção.
    """
    if not carrinho: 
        raise ValueError("Carrinho vazio.")
    if not usuario_id: 
        raise ValueError("Erro de sessão.")
    
    # 1. Validação de Estoque (Regra de Negócio)
    total_produtos = 0.0
    for item in carrinho:
        p_id, _, qtd, preco, sub = item
        produto_db = db.buscar_produto_por_id(p_id)
        
        if not produto_db:
             raise ValueError(f"Produto ID {p_id} não encontrado no banco.")
             
        # produto_db = (id, nome, qtd_estoque, preco...)
        qtd_estoque = produto_db[2] 
        
        if qtd > qtd_estoque:
            raise ValueError(f"Estoque de '{item[1]}' insuficiente! Restam: {qtd_estoque}")
        
        total_produtos += sub

    # 2. Calcula Total Final (Produtos + Frete)
    total_final = total_produtos + valor_frete

    try:
        # 3. Chama o DB Manager para persistir os dados (Sem SQL aqui)
        venda_id = db.registrar_venda_transacao(
            usuario_id=usuario_id, 
            total_venda=total_final, 
            carrinho=carrinho, 
            cliente_id=cliente_id,
            valor_frete=valor_frete
        )
        
        # 4. Lança no Financeiro (Regra de Negócio)
        desc_fin = f"Venda PDV #{venda_id}"
        if cliente_id:
            desc_fin += f" (Cli ID: {cliente_id})"
        
        # Se houve frete, adiciona na descrição para facilitar controle
        if valor_frete > 0:
            desc_fin += f" [+Frete R${valor_frete:.2f}]"
            
        lg_financeiro.registrar_movimentacao(
            descricao=desc_fin,
            valor=total_final,
            tipo='entrada',
            usuario_id=usuario_id,
            venda_id=venda_id
        )
        
        return venda_id
        
    except Exception as e:
        logging.error(f"Erro ao processar venda na lógica: {e}")
        # Repassa o erro para a tela exibir o alerta
        raise e
