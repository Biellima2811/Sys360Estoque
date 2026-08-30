from database import db_manager as db

def adicionar_cliente(nome, telefone, email, cpf_cnpj, endereco):
    """Valida e envia o novo cliente para o banco."""
    # Validação simples
    if not nome or not cpf_cnpj:
        raise ValueError("Os campos 'Nome' e 'CPF/CNPJ' são obrigatórios.")
    
    # Limpeza básica (converter para string para evitar erro se vier número)
    nome = str(nome).strip()
    cpf_cnpj = str(cpf_cnpj).strip()
    
    # Chama o banco de dados
    db.adicionar_cliente(nome, telefone, email, cpf_cnpj, endereco)

def listar_todos_clientes():
    """Retorna a lista de clientes do banco."""
    return db.listar_clientes()

def buscar_cliente_por_cpf(cpf_cnpj):
    """Busca cliente para preencher a tela de edição."""
    if not cpf_cnpj:
        return None
    return db.buscar_cliente_por_cpf(str(cpf_cnpj))

def atualizar_cliente(id_cliente, nome, telefone, email, cpf_cnpj, endereco):
    """Atualiza o cliente existente."""
    if not id_cliente:
        raise ValueError("Erro: ID do cliente não encontrado.")
    
    if not nome or not cpf_cnpj:
        raise ValueError("Nome e CPF/CNPJ são obrigatórios.")

    db.atualizar_cliente(id_cliente, nome, telefone, email, cpf_cnpj, endereco)

def remover_cliente(id_cliente):
    pass