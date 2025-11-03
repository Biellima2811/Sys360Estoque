from database import db_manager as db
import bcrypt
import re
from sqlite3 import Error

def validar_e_processar_produto(nome, quantidade_str, preco_venda_str, preco_custo_str, categoria, fornecedor):
    """
    Valida os dados de entrada para um produto.
    Lança um 'ValueError' se houver um erro de validação.
    Retorna os dados convertidos (int, float) se for válido.
    """

    # 1. Validação de campos obrigatórios
    if not nome:
        raise ValueError('O campo "Nome" é obrigatório!')
    
    if not quantidade_str:
        raise ValueError('O campo "Quantidade" é obrigatório!')
    
    if not preco_venda_str or not preco_custo_str:
        raise ValueError("O campo 'Preço de Venda' e 'Preço Custo' é obrigatório!")
    
    if not categoria or not fornecedor:
        raise ValueError("O campo 'Categoria' e 'Fornecedor' é obrigatório!")
    
    if not nome or not quantidade_str or not preco_venda_str or not preco_custo_str or not categoria or not fornecedor:
        raise ValueError("Atenção - Todos os campos são obrigatório.")
    
    # 2. Conversão e Validação de Tipo
    try:
        qtd_int = int(quantidade_str)
    except ValueError:
        raise ValueError("O campo 'Quantidade' deve ser um número inteiro.")
    
    try:
        preco_venda_float = float(preco_venda_str.replace(',', '.'))
    except ValueError:
        raise ValueError("O 'Preço de Venda' deve ser um número válido (ex: 120.50).")
        
    # Preço de custo é opcional, mas se digitado, deve ser um número
    preco_custo_float = 0.0
    if preco_custo_str: # Se o campo não estiver vazio
        try:
            preco_custo_float = float(preco_custo_str.replace(',', '.'))
        except ValueError:
            raise ValueError("O 'Preço de Custo' deve ser um número válido (ex: 80.20).")
    
    # 3. Validação de Regra de Negócio
    if qtd_int < 0:
        raise ValueError('A quantidade não pode ser negativa!')
    if preco_venda_float < 0:
        raise ValueError('O preço de venda não pode ser negativo!')
    if preco_custo_float < 0:
        raise ValueError('O preço de custo não pode ser negativo!')
    
    # Campos de texto (podem ficar vazios, então só limpamos)
    categoria_limpa = categoria.strip()
    fornecedor_limpo = fornecedor.strip()

    # Se tudo deu certo, retorna os dados limpos
    return nome, qtd_int, preco_venda_float, preco_custo_float, categoria_limpa, fornecedor_limpo

def adicionar_produto(nome, quantidade_str, preco_venda_str, preco_custo_str, categoria, fornecedor):
    """Processa e adiciona um novo produto (v2)."""
    # 1. Valida os dados
    dados_validos = validar_e_processar_produto(
        nome, quantidade_str, preco_venda_str, preco_custo_str, categoria, fornecedor
    )
    # 2. Envia para o banco de dados
    # O '*' desempacota a tupla na ordem correta
    db.adicionar_produto(*dados_validos)

def atualizar_produto(id, nome, quantidade_str, preco_venda_str, preco_custo_str, categoria, fornecedor):
    """Processa e atualiza um produto existente (v2)."""
    # 1. Valida os dados
    dados_validos = validar_e_processar_produto(
        nome, quantidade_str, preco_venda_str, preco_custo_str, categoria, fornecedor
    )
    # 2. Envia para o banco de dados (adicionando o ID no início)
    db.atualizar_produto(id, *dados_validos)

def remover_produto(id):
    """Remove um produto por ID."""
    if not id:
        raise ValueError("Nenhum produto selecionado para remover.")
    db.remover_produto(id)

def buscar_produtos(nome_busca):
    """Busca produtos por nome"""
    if not nome_busca:
        # Se a busca for vazia, retorna todos
        return db.listar_produtos()
    
    resultados = db.buscar_produto(nome_busca)
    if not resultados:
        # lança um erro se a busca não retorna nada
        raise ValueError(f"Nenhum produto encontrado com o nome '{nome_busca}'.")
    
    return resultados

def listar_todos_produtos():
    """Apenas repassa a listagem do banco."""
    return db.listar_produtos()
