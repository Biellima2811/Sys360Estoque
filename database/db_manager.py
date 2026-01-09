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
        # --- MÓDULO DE FROTA ---
        # Tabela de Veículos
        cursor.execute("""CREATE TABLE IF NOT EXISTS veiculos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     placa TEXT UNIQUE NOT NULL,
                     modelo TEXT NOT NULL,
                     marca TEXT,
                     ano INTEGER,
                     capacidade_kg REAL,
                     status TEXT DEFAULT 'disponivel' CHECK(status IN ('disponivel', 'em_rota', 'manutencao'))
                     );""")

        # Tabela de Histórico de Manutenções
        cursor.execute("""CREATE TABLE IF NOT EXISTS manutencoes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     veiculo_id INTEGER NOT NULL,
                     data_manutencao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     descricao TEXT NOT NULL,
                     custo REAL,
                     km_atual INTEGER,
                     FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
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

        try: # Adiciona cliente_id na tabela vendas
            cursor.execute("ALTER TABLE vendas ADD COLUMN cliente_id INTEGER REFERENCES clientes(id)")
        except Error:
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

def registrar_venda_transacao(usuario_id, total_venda, carrinho, cliente_id=None):
    """
    Registra venda com transação e suporte a Cliente.
    """
    conn = conectar()
    if conn is None: raise Error("Sem conexão")
    
    try:
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")

        # Insere venda com CLIENTE_ID
        cursor.execute(
            "INSERT INTO vendas (usuario_id, total_venda, cliente_id) VALUES (?,?,?)", 
            (usuario_id, total_venda, cliente_id)
        )
        venda_id = cursor.lastrowid
        
        for item in carrinho:
            # item = (id, nome, qtd, preco, subtotal)
            produto_id = item[0]
            qtd_venda = item[2]
            preco_unit = item[3]

            cursor.execute("""
                INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario)
                VALUES (?,?,?,?)""", (venda_id, produto_id, qtd_venda, preco_unit))
            
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", 
                           (qtd_venda, produto_id))
            
        conn.commit()
        return venda_id
    except Error as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

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

def listar_vendas_detalhadas():
    """
    Lista todas as vendas com nomes de Cliente e Usuário.
    """
    conn = conectar()
    if conn is None: return[]

    try:
        cursor = conn.cursor()
        sql = """
            SELECT 
                v.id, 
                v.data_hora, 
                u.nome_completo as vendedor, 
                c.nome_completo as cliente, 
                v.total_venda
            FROM vendas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.data_hora DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f'Erro ao listar historico: {e}')
    finally:
        print('Encerramento de conexão com base')
        conn.close()

def listar_itens_da_venda(venda_id):
    """
    Retorna os produtos de uma venda específica.
    """
    conn = conectar()
    if conn is None: return []

    try:
        cursor = conn.cursor()
        sql = """
            SELECT 
                p.nome,
                vi.quantidade,
                vi.preco_unitario,
                (vi.quantidade * vi.preco_unitario) as subtotal
            FROM venda_itens vi
            JOIN produtos p ON vi.produto_id = p.id
            WHERE vi.venda_id = ?
        """
        cursor.execute(sql, (venda_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"Erro ao listar itens: {e}")
        return []
    finally:
        conn.close()