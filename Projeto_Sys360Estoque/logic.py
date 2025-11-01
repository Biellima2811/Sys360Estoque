# logic.py
# O "Cérebro" - Não sabe nada sobre interface gráfica.
# Apenas processa dados e fala com o banco.
import database as db

def validar_e_processar_produto(nome, quantidade_str, preco_str):
    """
    Valida os dados de entrada para um produto.
    Lança um 'ValueError' se houver um erro de validação.
    Retorna os dados convertidos (int, float) se for válido.
    """

    # 1. Validação de campos vazios
    if not nome or not quantidade_str or not preco_str:
        raise ValueError('Todos os campos são de carater obrigadorio !')
    
    # 2. Conversão e Validação de Tipo
    try:
        qtd_int = int(quantidade_str)
    except ValueError:
        raise ValueError("O campo 'Quantidade' deve ser um número inteiro")
    
    try:
        preco_float = float(preco_str.replace(',', '.'))
    except ValueError:
        raise ValueError("O campo 'Preço', dever ser um número válido (ex: 120.50).")
    
    # 3. Validação de Regra de Negócio
    if qtd_int < 0:
        raise ValueError('A quantidade não pode ser negativa!')
    if preco_float < 0:
        raise ValueError('O preço não pode ser negativo!')
    
    # Se tudo deu certo, retorna os dados limpos
    return nome, qtd_int, preco_float

def adicionar_produto(nome, quantidade_str, preco_str):
    """Processa e adiciona um novo produto."""
    nome_val, qtd_val, preco_val = validar_e_processar_produto(nome, quantidade_str, preco_str)
    db.adicionar_produto(nome_val, qtd_val, preco_val)

def atualizar_produto(id, nome, quantidade_str, preco_str):
    """Processa e atualiza um produto existente."""
    nome_val, qtd_val, preco_val = validar_e_processar_produto(nome, quantidade_str, preco_str)
    db.atualizar_produto(id, nome_val, qtd_val, preco_val)

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