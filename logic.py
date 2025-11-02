# logic.py
# O "Cérebro" - Não sabe nada sobre interface gráfica.
# Apenas processa dados e fala com o banco.
import database as db
import bcrypt
import re
from sqlite3 import Error

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

def _hash_senha(senha):
    """Gera um hash seguro para a senha."""
    sal = bcrypt.gensalt()
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), sal)
    return hash_senha.decode('utf-8')

def verificar_senha(senha_fornecida, hash_armazenado):
    """Verifica se a senha fornecida bate com o hash salvo."""
    if isinstance(hash_armazenado, str):
        hash_armazenado = hash_armazenado.encode('utf-8')
    return bcrypt.checkpw(senha_fornecida.encode('utf-8'), hash_armazenado)

def criar_primeiro_admin():
    """
    Verifica se existe algum usuário. Se não, cria um admin padrão.
    Isso é crucial para a primeira execução do sistema.
    """

    if not db.buscar_usuario_por_login("admin"):
        print("Nenhum admin encontrado!, Criando usuario 'admin' padrão...")
        senha_hash = _hash_senha("admin") # Senha padrão é 'admin'
        db.adicionar_usuario(
            nome_completo="Administrador do Sistema",
            login="admin",
            senha_hash=senha_hash,
            role="admin"
        )
    else:
        print("Usuario admin já existente!")

def verificar_login(login, senha):
    """
    Verifica as credenciais do usuário.
    Retorna a tupla do usuário se for válido, senão lança um erro.
    """
    usuario_db = db.buscar_usuario_por_login(login)

    # Usuário não encontrado
    if not usuario_db:
        raise ValueError("Login ou senha invalidos")
    
    # usuário_db é uma tupla: (id, nome_completo, login, senha_hash, role)
    hash_armazenado = usuario_db[3]

    # Senha não bateu
    if not verificar_senha(senha, hash_armazenado):
        raise ValueError("Login ou senha inválidos.")
    
    # Sucesso! Retorna os dados do usuario
    print(f"Login bem-sucedido! -> User: {usuario_db[1]} | Função : {usuario_db[4]}")
    return usuario_db

def listar_todos_usuarios():
    """Apenas repassa a listagem de usuários do banco."""
    return db.listar_usuarios()

def registrar_novo_usuario(nome_completo, login, senha, role):
    """
    Valida e registra um novo usuário no sistema.
    Lança ValueError em caso de falha.
    """
    # 1. Validação de campos
    if not nome_completo or not login or not senha or not role:
        raise ValueError ("Atenção !, Todos os campos são de caráter obrigatorio. ")
    
    if role not in ['admin', 'funcionario']:
        raise ValueError ("A 'FUNÇÂO deve ser 'admin' ou 'funcionario'.")
    
    if len(senha) < 4:
        raise ValueError("A senha deve ter pelo menos 4 caracteres.")
    # 2. Verificar se o login já existe
    if db.buscar_usuario_por_login(login):
        raise ValueError(f"O login '{login}', já está em uso.")
    
    # 3. Se tudo estiver OK, hashear a senha e salvar
    try:
        senha_hash = _hash_senha(senha)
        db.adicionar_usuario(nome_completo, login, senha_hash, role) # <-- CORRETO! Salve o hash!
        print(f"Novo usuario: '{login}' registrado com sucesso pela tela de admin.")
    except Exception as e:
        raise ValueError(f'Erro ao salvar no banco de dados: {e}')

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
    # 1. Validação final
    if not carrinho:
        raise ValueError('O carrinho está vazio. Adicione produtos para finalizar a venda.')
    
    if not usuario_id:
        raise ValueError('Usuário não identificado. Faça login novamente.')

    # 2. (Opcional, mas recomendado) Re-validar todo o estoque
    # Isso previne que duas pessoas vendam o mesmo item ao mesmo tempo. 
    print('Re-validando estoque antes da transação, favor aguarde...')

    for item in carrinho:
        produto_id = item[0]
        qtd_vendida = item[2]

        produto_db = db.buscar_produto_por_id(produto_id)
        
        if produto_db is None:
            raise ValueError(f"Erro critico: Produto '{item[1]}' (ID: {produto_id} não existe mais.)")
        
        if qtd_vendida > produto_db[2]: # produto_db[2] é a qtd
            raise ValueError(f"Estoque de '{produto_db[1]}' mudou durante a venda!\n"
                             f"Disponível: {produto_db[2]} | No carrinho: {qtd_vendida}")
        
        # 3. Calcular o total final (confiamos no backend, não no frontend)
        total_venda = 0.0 # <-- MOVER PARA ANTES DO LOOP
        for item in carrinho:
            total_venda += item[4] # item[4] é o subtotal (qtd * preco)
        print(f"Total calculado: {total_venda}")

        # 4. Enviar para a camada de dados (A Transação)
        try:
            venda_id = db.registrar_venda_transacao(usuario_id, total_venda, carrinho)
            print(f'Logic.py: Venda {venda_id} procesada com sucesso.')
            return venda_id
        
        except Exception as e:
            # Se o db.registrar_venda_transacao deu rollback(), ele vai lançar um erro.
            # Nós o capturamos e repassamos para a interface.
            print(f"Logic.py: Falha na transação. {e}")
            raise ValueError(f"Erro ao salvar a venda no banco de dados. {e}")

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
        cliente_existente = db.buscar_cliente_por_cpf(cpf_cnpj)
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
        db.adicionar_cliente(*dados_validos)# O '*' desempacota a tupla
        print(f"Novo cliente '{nome}' registrado com sucesso.")
    except (ValueError, Error) as e:
        # Pega erros de validação (ValueError) e erros de banco (Error, ex: duplicado)
        print(f"Erro ao registrar cliente '{nome}' (CPF/CNPJ: {cpf_cnpj}): {e}")
        raise ValueError(f"Erro ao registrar cliente: {e}") # Repassa o erro para a interface

def listar_todos_clientes():
    """Apenas repassa a listagem de clientes do banco."""
    return db.listar_clientes()