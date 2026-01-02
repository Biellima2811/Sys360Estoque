import sqlite3
from sqlite3 import Error


def conectar():
    """Cria uma conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect('estoque.db')
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def criar_tabela(conn):
    """Cria a tabela de produtos se ela não existir."""
    try:
        cursor = conn.cursor()
        comando = """CREATE TABLE IF NOT EXISTS produtos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco REAL NOT NULL );"""
        cursor.execute(comando)

        cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome_completo TEXT NOT NULL,
                     login TEXT UNIQUE NOT NULL,
                     senha_hash TEXT NOT NULL,
                     role TEXT NOT NULL DEFAULT 'funcionario' 
                     );""") # roles: 'admin', 'funcionario'
        
        # Tabela 1: O "Recibo" principal da venda
        cursor.execute("""CREATE TABLE IF NOT EXISTS vendas (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     usuario_id INTEGER NOT NULL,
                     total_venda REAL NOT NULL,
                     FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                     );""")
        
        # Tabela 2: Os itens de cada venda
        cursor.execute("""CREATE TABLE IF NOT EXISTS venda_itens (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     venda_id INTEGER NOT NULL,
                     produto_id INTEGER NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco_unitario REAL NOT NULL,
                     FOREIGN KEY (venda_id) REFERENCES vendas(id),
                     FOREIGN KEY (produto_id) REFERENCES produtos(id)
                     );""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS clientes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome_completo TEXT NOT NULL,
                     telefone TEXT,
                     email TEXT,
                     cpf_cnpj TEXT UNIQUE,
                     endereco TEXT
                     );""")
        # Categoria das contas (Ex: 'Venda de Produto', 'Conta de Luz', 'Salário')
        cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro_categorias (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa'))
                     );""")

        # Tabela principal de movimentações (Fluxo de Caixa)
        cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro_movimentacoes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     descricao TEXT NOT NULL,
                     valor REAL NOT NULL,
                     tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                     categoria_id INTEGER,
                     venda_id INTEGER, -- Link opcional: Se veio de uma venda do PDV
                     usuario_id INTEGER, -- Quem lançou
                     FOREIGN KEY (categoria_id) REFERENCES financeiro_categorias(id),
                     FOREIGN KEY (venda_id) REFERENCES vendas(id),
                     FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                     );""")
        
        # --- LÓGICA DE MIGRAÇÃO (ALTER TABLE) ---
        # Isso atualiza o banco de dados se ele já existir
        
        # 1. Renomeia 'preco' para 'preco_venda'
        try: # apenas renomeia a coluna preco para preco_custo
            cursor.execute("ALTER TABLE produtos RENAME COLUMN preco TO preco_venda")
        except Error as e:
            pass # Ignora o erro se a coluna já foi renomeada

        # 2. Adiciona as colunas novas
        try: # Adiciona a coluna preço de custo
            cursor.execute("ALTER TABLE produtos ADD COLUMN preco_custo REAL DEFAULT 0.0")
        except Error as e:
            pass

        try: # Adiciona a coluna categoria
            cursor.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT NOT NULL")
        except Error as e:
            pass

        try: # Adiciona a coluna Fornecedor
            cursor.execute("ALTER TABLE produtos ADD COLUMN fornecedor TEXT NOT NULL")
        except Error as e:
            pass

        
    except Error as e:
        print(f"Erro ao criar a tabela: {e}")
        

# --- FUNÇÕES CRUD ---

def adicionar_produto(nome, quantidade, preco_venda, preco_custo, categoria, fornecedor):
    """Adiciona um novo produto ao banco de dados."""
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO produtos (nome, 
                                                quantidade, 
                                                preco_venda, 
                                                preco_custo,
                                                categoria, 
                                                fornecedor) VALUES (?, ?, ?, ?, ?, ?)""", (nome, quantidade, preco_venda, preco_custo, categoria, fornecedor))
        conn.commit()
    except Error as e:
        print(f"Erro ao adicionar produto: {e}")
    finally:
        if conn:
            conn.close()


def listar_produtos():
    """Retorna uma lista de todos os produtos do banco de dados."""
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        # CORREÇÃO AQUI: Adicionado o '*' para selecionar todas as colunas.
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
        produtos = cursor.fetchall()
        return produtos
    except Error as e:
        print(f"Erro ao listar produtos: {e}")
        return []
    finally:
        if conn:
            conn.close()


def atualizar_produto(id, nome, quantidade, preco_venda, preco_custo, categoria, fornecedor):
    """Atualiza os dados de um produto com base no seu ID."""
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""UPDATE produtos SET 
                       nome = ?, 
                       quantidade = ?, 
                       preco_venda = ?,
                       preco_custo = ?,
                       categoria = ?,
                       fornecedor = ? 
               WHERE id = ?""",
                       (nome, quantidade, preco_venda, preco_custo, categoria, fornecedor, id))
        conn.commit()
    except Error as e:
        print(f"Erro ao atualizar produto: {e}")
    finally:
        if conn:
            conn.close()


def remover_produto(id):
    """Remove um produto do banco de dados com base no seu ID."""
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        # CORREÇÃO AQUI: O parâmetro 'id' deve ser passado como uma tupla (id,).
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
        conn.commit()
    except Error as e:
        print(f"Erro ao remover produto: {e}")
    finally:
        if conn:
            conn.close()


def buscar_produto(nome):
    """Busca produtos cujo nome contenha o texto pesquisado."""
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        # CORREÇÃO AQUI: O parâmetro de busca também deve ser uma tupla.
        cursor.execute("SELECT * FROM produtos WHERE nome LIKE ? ORDER BY nome", ('%' + nome + '%',))
        produtos = cursor.fetchall()
        return produtos
    except Error as e:
        print(f"Erro ao buscar produto: {e}")
        return []
    finally:
        if conn:
            conn.close()

def buscar_produto_por_id(id_produto):
    """Busca um produto específico pelo seu ID."""
    conn = conectar()
    if conn is None: return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos where id = ?", (id_produto,))
        produto = cursor.fetchone() # Retorna uma tupla (id, nome, qtd, preco) ou None
        return produto
    except Error as e:
        print(f'Erro ao buscar produto pro ID: {e}')
        return None
    finally:
        if conn:
            conn.close()
            print('Conexão com a base de dados encerrada!')
    
def adicionar_usuario(nome_completo, login, senha_hash, role='funcionario'):
    """Adiciona um novo usuário ao banco de dados."""
    conn = conectar()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome_completo, login, senha_hash, role) VALUES (?, ?, ?, ?)", (nome_completo, login, senha_hash, role)
        )
        conn.commit()
        print(f'Usuario {login} criado com sucesso!')
    except Error as e:
        print(f'Erro ao adicionar usuario: {e}, verifique comando SQL')
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_login(login):
    """Busca um usuário pelo seu login."""
    conn = conectar()
    if conn is None: return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
        usuario = cursor.fetchone() # Retorna uma tupla ou None
        return usuario
    except Error as e:
        print(f'Erro ao buscar usuario: {e}')
        return None
    finally:
        if conn:
            print('Conexão encerrada com a base de dados')
            conn.close()

def listar_usuarios():
    """Retorna uma lista de todos os usuários (sem o hash da senha)."""
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_completo, login, role FROM usuarios ORDER BY nome_completo")
        usuarios = cursor.fetchall()
        return usuarios
    except Error as e:
        print(f'Erro ao listar usuarios cadastrados na base: {e}')
        return []
    finally:
        if conn:
            conn.close()
            print("Conexão encerrada com a base...")

def registrar_venda_transacao(usuario_id, total_venda, carrinho):
    """
    Registra uma venda completa usando uma transação.
    'carrinho' é uma lista de tuplas: [(id_produto, nome, qtd, preco_unit, subtotal), ...]
    """
    conn = conectar()
    if conn is None:
        raise Error('Não foi possivel estabelecer conexão com base de dados. \n',
        'Verifue o caminho do banco ou se esta realmente dentro a pasta da aplicação')
    try:
        cursor = conn.cursor()
        # Inicia a transação
        conn.execute("BEGIN TRANSACTION;")

        # --- Passo 1: Insere o "recibo" na tabela 'vendas' ---
        cursor.execute(
            "INSERT INTO vendas (usuario_id, total_venda) VALUES (?,?)", (usuario_id, total_venda)
        )
        # Pega o ID da venda que acabamos de criar
        venda_id = cursor.lastrowid
        
        # --- Passo 2: Itera sobre o carrinho e insere os itens ---
        for item in carrinho:
            produto_id = item[0]
            quantidade_venda = item[2]
            preco_unitario = item[3]

            # Insere o item na tabela 'venda_itens'
            cursor.execute("""
                            INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario)
                            VALUES (?,?,?,?)""", 
                            (venda_id, produto_id, quantidade_venda, preco_unitario))
            # --- Passo 3: Atualiza (dá baixa) no estoque ---
            # Este é o comando mais crítico.
            cursor.execute("""UPDATE produtos 
                           SET quantidade = quantidade - ? 
                           where id = ?""", 
                           (quantidade_venda, produto_id))
            
        # --- Passo 4: Se tudo deu certo, "salva" a transação ---
        conn.commit()
        print(f'Venda {venda_id} foi registrada com sucesso!')
        return venda_id
    except Error as e:
        # --- FALHA: Se qualquer passo acima deu erro, desfaz tudo ---
        if conn:
            conn.rollback() # Desfaz todas as mudanças da transação
        print(f'Ocorreu um erro ao registrar a venda. Transação sendo desfeita: {e}')
        # Propaga o erro para a camada de lógica saber que falhou
        raise e
    
    finally:
        if conn:
            conn.close()
            print('Conexão encerrada com a base de dados...')

# ==========================================================
# --- FUNÇÕES CRUD DE CLIENTES ---
# ==========================================================

def adicionar_cliente(nome, telefone, email, cpf_cnpj, endereco):
    """Adiciona um novo cliente ao banco de dados."""
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        
        cursor.execute(
        """INSERT INTO clientes (nome_completo, telefone, email, cpf_cnpj, endereco)
           VALUES (?, ?, ?, ?, ?)""", (nome, telefone, email, cpf_cnpj, endereco))
        
        conn.commit()
    except Error as e:
        print(f"Erro ao adicionar cliente: {e}")
        # Propaga o erro para o logic.py saber que falhou (ex: CPF/CNPJ duplicado)
        raise e
    finally:
        if conn:
            conn.close()
            print('Conexão com a base de dados, foi encerrada!')

def buscar_cliente_por_cpf(cpf_cnpj):
    """Busca um cliente específico pelo seu CPF/CNPJ (que é UNIQUE)."""
    conn = conectar()

    if conn is None: return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE cpf_cnpj = ?", (cpf_cnpj,))
        cliente = cursor.fetchone()
        return cliente
    
    except Error as e:
        print(f"Erro ao buscar cliente por CPF/CNPJ: {e}")
        return None
    finally:
        if conn:
            conn.close()
            print('Conexão com a base de dados foi encerrada!')

def listar_clientes():
    """Retorna uma lista de todos os clientes (campos principais)."""
    conn = conectar()
    if conn is None: return [] # Retorna uma lista
    try:
        cursor = conn.cursor()
        # Retorna apenas os campos que queremos na tabela principal
        cursor.execute("SELECT id, nome_completo, telefone, email, cpf_cnpj FROM clientes ORDER BY nome_completo")
        clientes = cursor.fetchall()
        return clientes
    except Error as e:
        print(f'Erro ao listar clientes: {e}')
    finally:
        if conn:
            conn.close()
            print('Conexão com a base de dados foi encerrada!')

def inicializar_db():
    """Conecta ao DB e garante que a tabela de produtos exista."""
    conn = conectar()
    if conn is not None:
        criar_tabela(conn)
        conn.close()
    else:
        print("Não foi possível estabelecer conexão com o banco de dados.")