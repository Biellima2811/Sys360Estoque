from database.db_manager import *
import bcrypt
import re
from sqlite3 import Error

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

    if not buscar_usuario_por_login("admin"):
        print("Nenhum admin encontrado!, Criando usuario 'admin' padrão...")
        senha_hash = _hash_senha("admin") # Senha padrão é 'admin'
        adicionar_usuario(
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
    usuario_db = buscar_usuario_por_login(login)

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
    return listar_usuarios()

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
    if buscar_usuario_por_login(login):
        raise ValueError(f"O login '{login}', já está em uso.")
    
    # 3. Se tudo estiver OK, hashear a senha e salvar
    try:
        senha_hash = _hash_senha(senha)
        adicionar_usuario(nome_completo, login, senha_hash, role) # <-- CORRETO! Salve o hash!
        print(f"Novo usuario: '{login}' registrado com sucesso pela tela de admin.")
    except Exception as e:
        raise ValueError(f'Erro ao salvar no banco de dados: {e}')