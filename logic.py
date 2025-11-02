# logic.py
# O "Cérebro" - Não sabe nada sobre interface gráfica.
# Apenas processa dados e fala com o banco.
import database as db
import bcrypt

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