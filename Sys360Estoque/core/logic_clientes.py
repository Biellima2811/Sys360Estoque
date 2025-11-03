from database.db_manager import *
import bcrypt
import re
from sqlite3 import Error

def validar_e_processar_cliente(nome, telefone, email, cpf_cnpj, endereco):
    """
    Valida os dados de entrada para um novo cliente.
    Lança um 'ValueError' se houver um erro de validação.
    """
    
    # 1. Validação de campos
    if not nome:
        raise ValueError("O campo 'Nome Completo' é obrigatório!")

    # 2. Validação de Regra de Negócio (CPF/CNPJ duplicado)
    if cpf_cnpj:
        cliente_existente = buscar_cliente_por_cpf(cpf_cnpj)
        if cliente_existente:
            raise ValueError(f"O CPF/CNPJ '{cpf_cnpj}' já está cadastrado para: {cliente_existente[1]}")

    if not email:
        raise ValueError("O campo 'Email' é obrigatório!")

    if not endereco:
        raise ValueError("O campo 'Endereço' é obrigatório!")
    
    # Validação simples de e-mail
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("O e-mail informado não é válido.")

    # Validação básica de CPF (apenas tamanho e dígitos)
    if cpf_cnpj and not re.match(r"^\d{11}$", cpf_cnpj):
        raise ValueError("O CPF deve conter 11 dígitos numéricos.")
    # 3. Se tudo deu certo, retorna os dados limpos
    return nome, telefone, email, cpf_cnpj, endereco

def registrar_novo_cliente(nome, telefone, email, cpf_cnpj, endereco):
    """Processa e adiciona um novo cliente."""
    try:
        # 1. Valida os dados
        dados_validos = validar_e_processar_cliente(nome, telefone, email, cpf_cnpj, endereco)
        # 2. Envia para o banco de dados
        adicionar_cliente(*dados_validos)# O '*' desempacota a tupla
        print(f"Novo cliente '{nome}' registrado com sucesso.")
    except (ValueError, Error) as e:
        # Pega erros de validação (ValueError) e erros de banco (Error, ex: duplicado)
        print(f"Erro ao registrar cliente '{nome}' (CPF/CNPJ: {cpf_cnpj}): {e}")
        raise ValueError(f"Erro ao registrar cliente: {e}") # Repassa o erro para a interface

def listar_todos_clientes():
    """Apenas repassa a listagem de clientes do banco."""
    return listar_clientes()