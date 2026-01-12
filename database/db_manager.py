import sqlite3
from sqlite3 import Error

def conectar():
    """
    Cria e retorna uma conexão com o banco de dados SQLite 'estoque.db'.

    Retorno:
        sqlite3.Connection | None: objeto de conexão se bem-sucedido, caso contrário None.
    Observações:
        - Usa sqlite3.connect que cria o arquivo de DB se não existir.
        - Em caso de erro, imprime a mensagem e retorna None.
    """
    try:
        conn = sqlite3.connect('estoque.db')
        return conn
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def criar_tabela(conn):
    """
    Garante que todas as tabelas necessárias existam no banco de dados e aplica
    migrações simples (ALTER TABLE) para atualizar esquemas antigos.

    Parâmetros:
        conn (sqlite3.Connection): conexão aberta com o banco de dados.

    Comportamento:
        - Cria tabelas: produtos, usuarios, vendas, venda_itens, clientes,
          financeiro_categorias, financeiro_movimentacoes, veiculos, manutencoes.
        - Executa blocos try/except para alterações de esquema (renomear/ adicionar colunas)
          sem falhar caso já tenham sido aplicadas anteriormente.
    """
    try:
        cursor = conn.cursor()

        # Tabela de produtos (estoque)
        comando = """CREATE TABLE IF NOT EXISTS produtos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco REAL NOT NULL );"""
        cursor.execute(comando)

        # Tabela de usuários do sistema (login/roles)
        cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome_completo TEXT NOT NULL,
                     login TEXT UNIQUE NOT NULL,
                     senha_hash TEXT NOT NULL,
                     role TEXT NOT NULL DEFAULT 'funcionario' 
                     );""")  # roles possíveis: 'admin', 'funcionario'
        
        # Tabela principal de vendas (recibo)
        cursor.execute("""CREATE TABLE IF NOT EXISTS vendas (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     usuario_id INTEGER NOT NULL,
                     total_venda REAL NOT NULL,
                     FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                     );""")
        
        # Itens de cada venda (relacionamento 1:N com vendas)
        cursor.execute("""CREATE TABLE IF NOT EXISTS venda_itens (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     venda_id INTEGER NOT NULL,
                     produto_id INTEGER NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco_unitario REAL NOT NULL,
                     FOREIGN KEY (venda_id) REFERENCES vendas(id),
                     FOREIGN KEY (produto_id) REFERENCES produtos(id)
                     );""")
        
        # Cadastro de clientes
        cursor.execute("""CREATE TABLE IF NOT EXISTS clientes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome_completo TEXT NOT NULL,
                     telefone TEXT,
                     email TEXT,
                     cpf_cnpj TEXT UNIQUE,
                     endereco TEXT
                     );""")

        # Categorias do financeiro (receita/despesa)
        cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro_categorias (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa'))
                     );""")

        # Movimentações financeiras (fluxo de caixa)
        cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro_movimentacoes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     descricao TEXT NOT NULL,
                     valor REAL NOT NULL,
                     tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                     categoria_id INTEGER,
                     venda_id INTEGER, -- Link opcional: se veio de uma venda do PDV
                     usuario_id INTEGER, -- quem lançou a movimentação
                     FOREIGN KEY (categoria_id) REFERENCES financeiro_categorias(id),
                     FOREIGN KEY (venda_id) REFERENCES vendas(id),
                     FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                     );""")

        # --- MÓDULO DE FROTA ---
        # Tabela de veículos
        cursor.execute("""CREATE TABLE IF NOT EXISTS veiculos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     placa TEXT UNIQUE NOT NULL,
                     modelo TEXT NOT NULL,
                     marca TEXT,
                     ano INTEGER,
                     capacidade_kg REAL,
                     status TEXT DEFAULT 'disponivel' CHECK(status IN ('disponivel', 'em_rota', 'manutencao'))
                     );""")

        # Histórico de manutenções dos veículos
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
        # As operações abaixo tentam atualizar o esquema sem quebrar se já aplicadas.

        # 1. Renomeia 'preco' para 'preco_venda' (caso tabela antiga tenha coluna preco)
        try:
            cursor.execute("ALTER TABLE produtos RENAME COLUMN preco TO preco_venda")
        except Error:
            # Ignora erro se a coluna já foi renomeada ou se não existe
            pass

        # 2. Adiciona colunas novas na tabela produtos (se ainda não existirem)
        try:
            cursor.execute("ALTER TABLE produtos ADD COLUMN preco_custo REAL DEFAULT 0.0")
        except Error:
            pass

        try:
            cursor.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT NOT NULL")
        except Error:
            pass

        try:
            cursor.execute("ALTER TABLE produtos ADD COLUMN fornecedor TEXT NOT NULL")
        except Error:
            pass

        # Adiciona colunas opcionais na tabela vendas
        try:
            cursor.execute("ALTER TABLE vendas ADD COLUMN cliente_id INTEGER REFERENCES clientes(id)")
        except Error:
            pass

        try:
            cursor.execute("ALTER TABLE vendas ADD COLUMN valor_frete REAL DEFAULT 0.0")
        except Error:
            pass
        
        try:
            cursor.execute("ALTER TABLE vendas ADD COLUMN endereco_entrega TEXT")
        except Error:
            pass

        try:
            cursor.execute("ALTER TABLE vendas ADD COLUMN status_entrega TEXT DEFAULT 'n/a'") 
            # status: 'n/a' (sem frete), 'pendente' (aguardando), 'em_rota', 'entregue'
        except Error:
            pass

        try:
            cursor.execute("ALTER TABLE vendas ADD COLUMN veiculo_id INTEGER")
        except Error:
            pass

        # Atualiza vendas antigas que tem frete para 'pendente'
        cursor.execute("UPDATE vendas SET status_entrega = 'pendente' WHERE valor_frete > 0 AND status_entrega = 'n/a'")

    except Error as e:
        # Erro geral ao criar tabelas ou aplicar migrações
        print(f"Erro ao criar a tabela: {e}")
        

# --- FUNÇÕES CRUD ---

def adicionar_produto(nome, quantidade, preco_venda, preco_custo, categoria, fornecedor):
    """
    Insere um novo produto na tabela produtos.

    Parâmetros:
        nome (str): nome do produto.
        quantidade (int): quantidade inicial em estoque.
        preco_venda (float): preço de venda do produto.
        preco_custo (float): preço de custo do produto.
        categoria (str): categoria do produto.
        fornecedor (str): nome do fornecedor.

    Observações:
        - Abre e fecha a conexão internamente.
        - Em caso de erro, imprime a mensagem.
    """
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO produtos (nome, 
                                                quantidade, 
                                                preco_venda, 
                                                preco_custo,
                                                categoria, 
                                                fornecedor) VALUES (?, ?, ?, ?, ?, ?)""",
                       (nome, quantidade, preco_venda, preco_custo, categoria, fornecedor))
        conn.commit()
    except Error as e:
        print(f"Erro ao adicionar produto: {e}")
    finally:
        if conn:
            conn.close()


def listar_produtos():
    """
    Retorna todos os produtos ordenados por nome.

    Retorno:
        list[tuple]: lista de tuplas representando as linhas da tabela produtos.
    """
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        # Seleciona todas as colunas para exibir informações completas do produto
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
    """
    Atualiza os dados de um produto existente identificado pelo ID.

    Parâmetros:
        id (int): identificador do produto a ser atualizado.
        nome (str), quantidade (int), preco_venda (float), preco_custo (float),
        categoria (str), fornecedor (str): novos valores para o produto.
    """
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
    """
    Remove um produto pelo seu ID.

    Parâmetros:
        id (int): identificador do produto a ser removido.
    Observações:
        - O parâmetro deve ser passado como tupla para evitar erros de binding.
    """
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
        conn.commit()
    except Error as e:
        print(f"Erro ao remover produto: {e}")
    finally:
        if conn:
            conn.close()


def buscar_produto(nome):
    """
    Busca produtos cujo nome contenha o texto informado (LIKE %nome%).

    Parâmetros:
        nome (str): texto de busca parcial.
    Retorno:
        list[tuple]: produtos encontrados.
    """
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
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
    """
    Retorna um produto específico pelo seu ID.

    Parâmetros:
        id_produto (int): ID do produto.
    Retorno:
        tuple | None: tupla com os campos do produto ou None se não encontrado.
    """
    conn = conectar()
    if conn is None: return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos where id = ?", (id_produto,))
        produto = cursor.fetchone()  # Retorna uma tupla (id, nome, qtd, preco, ...) ou None
        return produto
    except Error as e:
        print(f'Erro ao buscar produto pro ID: {e}')
        return None
    finally:
        if conn:
            conn.close()
            print('Conexão com a base de dados encerrada!')
    
def adicionar_usuario(nome_completo, login, senha_hash, role='funcionario'):
    """
    Cria um novo usuário no sistema.

    Parâmetros:
        nome_completo (str): nome do usuário.
        login (str): identificador único para login.
        senha_hash (str): hash da senha (não armazenar senhas em texto puro).
        role (str): papel do usuário no sistema ('admin' ou 'funcionario').
    Observações:
        - Em caso de violação de UNIQUE no campo login, o sqlite lançará um erro.
    """
    conn = conectar()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome_completo, login, senha_hash, role) VALUES (?, ?, ?, ?)",
            (nome_completo, login, senha_hash, role)
        )
        conn.commit()
        print(f'Usuario {login} criado com sucesso!')
    except Error as e:
        print(f'Erro ao adicionar usuario: {e}, verifique comando SQL')
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_login(login):
    """
    Busca um usuário pelo login.

    Parâmetros:
        login (str): login do usuário.
    Retorno:
        tuple | None: tupla com os campos do usuário ou None se não encontrado.
    """
    conn = conectar()
    if conn is None: return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
        usuario = cursor.fetchone()  # Retorna uma tupla ou None
        return usuario
    except Error as e:
        print(f'Erro ao buscar usuario: {e}')
        return None
    finally:
        if conn:
            print('Conexão encerrada com a base de dados')
            conn.close()

def listar_usuarios():
    """
    Lista todos os usuários sem expor o hash da senha.

    Retorno:
        list[tuple]: cada tupla contém (id, nome_completo, login, role).
    """
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

def registrar_venda_transacao(usuario_id, total_venda, carrinho, cliente_id=None, valor_frete=0.0):
    """
    Registra a venda e define o status de entrega automaticamente.
    """
    conn = conectar()
    if conn is None: raise Error("Sem conexão com a base de dados")
    
    try:
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")

        # LÓGICA DE STATUS: Se tem frete, fica 'pendente'. Se não, 'n/a' ou 'concluido'
        status_inicial = 'pendente' if valor_frete > 0 else 'n/a'

        # Insere venda com todos os campos corretos
        cursor.execute(
            """INSERT INTO vendas 
               (usuario_id, total_venda, cliente_id, valor_frete, status_entrega) 
               VALUES (?, ?, ?, ?, ?)""", 
            (usuario_id, total_venda, cliente_id, valor_frete, status_inicial)
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
    """
    Insere um novo cliente na tabela clientes.

    Parâmetros:
        nome (str): nome completo do cliente.
        telefone (str): telefone de contato.
        email (str): e-mail do cliente.
        cpf_cnpj (str): CPF ou CNPJ (campo UNIQUE).
        endereco (str): endereço completo.

    Observações:
        - Em caso de CPF/CNPJ duplicado, o sqlite lançará um erro que é repassado (raise)
          para que a camada de lógica saiba que houve falha (ex: duplicidade).
    """
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
        # Propaga o erro para o chamador tratar (ex: CPF/CNPJ duplicado)
        raise e
    finally:
        if conn:
            conn.close()
            print('Conexão com a base de dados, foi encerrada!')

def buscar_cliente_por_cpf(cpf_cnpj):
    """
    Busca um cliente pelo CPF ou CNPJ (campo UNIQUE).

    Parâmetros:
        cpf_cnpj (str): CPF ou CNPJ a ser pesquisado.
    Retorno:
        tuple | None: dados do cliente ou None se não encontrado.
    """
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
    """
    Retorna uma lista de clientes com os campos principais para exibição.

    Retorno:
        list[tuple]: cada tupla contém (id, nome_completo, telefone, email, cpf_cnpj).
    """
    conn = conectar()
    if conn is None: return []  # Retorna lista vazia se sem conexão
    try:
        cursor = conn.cursor()
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
    """
    Inicializa o banco de dados garantindo que as tabelas existam.

    Uso:
        - Deve ser chamada na inicialização da aplicação para criar o esquema
          caso o arquivo de banco ainda não exista.
    """
    conn = conectar()
    if conn is not None:
        criar_tabela(conn)
        conn.close()
    else:
        print("Não foi possível estabelecer conexão com o banco de dados.")

def listar_vendas_detalhadas():
    """
    Lista vendas com informações do vendedor e do cliente (quando houver).

    Retorno:
        list[tuple]: cada tupla contém (v.id, v.data_hora, vendedor, cliente, v.total_venda).
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
    Retorna os itens (produtos) de uma venda específica com subtotal calculado.

    Parâmetros:
        venda_id (int): id da venda cujos itens serão listados.

    Retorno:
        list[tuple]: cada tupla contém (nome_produto, quantidade, preco_unitario, subtotal).
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
