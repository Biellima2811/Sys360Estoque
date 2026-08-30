import sqlite3
from sqlite3 import Error
import json
import os

# Nome do arquivo de configuração
CONFIG_FILE = 'config.json'

def carregar_caminho_db():
    """Lê o caminho do banco do arquivo JSON ou retorna o padrão."""
    default_path = 'estoque.db'
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('db_path', default_path)
        except:
            pass
    return default_path

def salvar_caminho_db(novo_caminho):
    """Salva o novo caminho no arquivo JSON."""
    dados = {'db_path': novo_caminho}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(dados, f)

def conectar():
    """Conecta ao banco usando o caminho configurado."""
    db_path = carregar_caminho_db()
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(f"Erro ao conectar em {db_path}: {e}")
        return None

def inicializar_db():
    """
    Inicializa o banco de dados garantindo que as tabelas existam.
    """
    conn = conectar()
    if conn is not None:
        criar_tabela(conn)
        conn.close()
    else:
        print("Não foi possível estabelecer conexão com o banco de dados.")

def criar_tabela(conn):
    try:
        cursor = conn.cursor()

        # Tabelas Base
        cursor.execute("""CREATE TABLE IF NOT EXISTS produtos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     quantidade INTEGER NOT NULL,
                     preco REAL NOT NULL,
                     preco_venda REAL,
                     preco_custo REAL DEFAULT 0.0,
                     categoria TEXT,
                     fornecedor TEXT
                     );""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome_completo TEXT NOT NULL,
                     login TEXT UNIQUE NOT NULL,
                     senha_hash TEXT NOT NULL,
                     role TEXT NOT NULL DEFAULT 'funcionario' 
                     );""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS vendas (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     usuario_id INTEGER NOT NULL,
                     total_venda REAL NOT NULL,
                     cliente_id INTEGER,
                     valor_frete REAL DEFAULT 0.0,
                     status_entrega TEXT DEFAULT 'n/a',
                     veiculo_id INTEGER,
                     endereco_entrega TEXT,
                     metodo_pagamento TEXT DEFAULT 'Dinheiro',
                     valor_pago REAL DEFAULT 0.0,
                     troco REAL DEFAULT 0.0,
                     FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                     );""")
        
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

        cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro_categorias (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     nome TEXT NOT NULL,
                     tipo TEXT NOT NULL CHECK(tipo IN ('receita', 'despesa'))
                     );""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro_movimentacoes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     descricao TEXT NOT NULL,
                     valor REAL NOT NULL,
                     tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                     categoria_id INTEGER,
                     venda_id INTEGER,
                     usuario_id INTEGER,
                     FOREIGN KEY (categoria_id) REFERENCES financeiro_categorias(id),
                     FOREIGN KEY (venda_id) REFERENCES vendas(id),
                     FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                     );""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS veiculos (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     placa TEXT UNIQUE NOT NULL,
                     modelo TEXT NOT NULL,
                     marca TEXT,
                     ano INTEGER,
                     capacidade_kg REAL,
                     status TEXT DEFAULT 'disponivel' CHECK(status IN ('disponivel', 'em_rota', 'manutencao'))
                     );""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS manutencoes (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     veiculo_id INTEGER NOT NULL,
                     data_manutencao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     descricao TEXT NOT NULL,
                     custo REAL,
                     km_atual INTEGER,
                     FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
                     );""")
        
        # --- TABELA DE CONFIGURAÇÃO DA EMPRESA ---
        cursor.execute("""CREATE TABLE IF NOT EXISTS empresa_config (
                     id INTEGER PRIMARY KEY CHECK (id = 1),
                     nome_fantasia TEXT,
                     endereco_base TEXT,
                     telefone TEXT
                     );""")
        
        # Cria a linha padrão se não existir
        cursor.execute("INSERT OR IGNORE INTO empresa_config (id, nome_fantasia, endereco_base) VALUES (1, 'Minha Empresa', '')")

        # Migrações
        migracoes = [
            "ALTER TABLE produtos ADD COLUMN preco_custo REAL DEFAULT 0.0",
            "ALTER TABLE produtos ADD COLUMN categoria TEXT",
            "ALTER TABLE produtos ADD COLUMN fornecedor TEXT",
            "ALTER TABLE vendas ADD COLUMN cliente_id INTEGER",
            "ALTER TABLE vendas ADD COLUMN valor_frete REAL DEFAULT 0.0",
            "ALTER TABLE vendas ADD COLUMN status_entrega TEXT DEFAULT 'n/a'",
            "ALTER TABLE vendas ADD COLUMN veiculo_id INTEGER",
            "ALTER TABLE vendas ADD COLUMN metodo_pagamento TEXT DEFAULT 'Dinheiro'",
            "ALTER TABLE vendas ADD COLUMN valor_pago REAL DEFAULT 0.0",
            "ALTER TABLE vendas ADD COLUMN troco REAL DEFAULT 0.0"
        ]

        for sql in migracoes:
            try:
                cursor.execute(sql)
            except Error:
                pass 

        cursor.execute("UPDATE vendas SET status_entrega = 'pendente' WHERE valor_frete > 0 AND status_entrega = 'n/a'")

    except Error as e:
        print(f"Erro ao criar/atualizar tabelas: {e}")

# --- FUNÇÕES GERAIS ---

def obter_dados_empresa():
    conn = conectar()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome_fantasia, endereco_base, telefone FROM empresa_config WHERE id = 1")
        return cursor.fetchone()
    except Error as e:
        print(f"Erro ao obter empresa: {e}")
        return None
    finally:
        if conn: conn.close()

def salvar_dados_empresa(nome, endereco, telefone):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE empresa_config 
            SET nome_fantasia = ?, endereco_base = ?, telefone = ?
            WHERE id = 1
        """, (nome, endereco, telefone))
        conn.commit()
    except Error as e:
        print(f"Erro ao salvar empresa: {e}")
        raise e
    finally:
        if conn: conn.close()

# --- FUNÇÕES PRODUTOS ---
def adicionar_produto(nome, quantidade, preco_venda, preco_custo, categoria, fornecedor):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO produtos (nome, quantidade, preco, preco_venda, preco_custo, categoria, fornecedor) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (nome, quantidade, preco_venda, preco_venda, preco_custo, categoria, fornecedor))
        conn.commit()
    except Error as e:
        print(f"Erro ao adicionar produto: {e}")
    finally:
        if conn: conn.close()

def listar_produtos():
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
        return cursor.fetchall()
    except Error as e:
        print(f"Erro ao listar produtos: {e}")
        return []
    finally:
        if conn: conn.close()

def atualizar_produto(id, nome, quantidade, preco_venda, preco_custo, categoria, fornecedor):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""UPDATE produtos SET 
                       nome = ?, quantidade = ?, preco = ?, preco_venda = ?, preco_custo = ?, categoria = ?, fornecedor = ? 
                       WHERE id = ?""",
                       (nome, quantidade, preco_venda, preco_venda, preco_custo, categoria, fornecedor, id))
        conn.commit()
    except Error as e:
        print(f"Erro ao atualizar produto: {e}")
    finally:
        if conn: conn.close()

def remover_produto(id):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
        conn.commit()
    except Error as e:
        print(f"Erro ao remover produto: {e}")
    finally:
        if conn: conn.close()

def buscar_produto(nome):
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE nome LIKE ? ORDER BY nome", ('%' + nome + '%',))
        return cursor.fetchall()
    except Error as e:
        print(f"Erro ao buscar produto: {e}")
        return []
    finally:
        if conn: conn.close()

def buscar_produto_por_id(id_produto):
    conn = conectar()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos where id = ?", (id_produto,))
        return cursor.fetchone()
    except Error as e:
        print(f'Erro ao buscar produto pro ID: {e}')
        return None
    finally:
        if conn: conn.close()

# --- FUNÇÕES USUÁRIOS ---
def adicionar_usuario(nome_completo, login, senha_hash, role='funcionario'):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome_completo, login, senha_hash, role) VALUES (?, ?, ?, ?)",
            (nome_completo, login, senha_hash, role)
        )
        conn.commit()
    except Error as e:
        print(f'Erro ao adicionar usuario: {e}')
    finally:
        if conn: conn.close()

def buscar_usuario_por_login(login):
    conn = conectar()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
        return cursor.fetchone()
    except Error as e:
        print(f'Erro ao buscar usuario: {e}')
        return None
    finally:
        if conn: conn.close()

def listar_usuarios():
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_completo, login, role FROM usuarios ORDER BY nome_completo")
        return cursor.fetchall()
    except Error as e:
        print(f'Erro ao listar usuarios: {e}')
        return []
    finally:
        if conn: conn.close()

# --- FUNÇÕES VENDAS ---
def registrar_venda_transacao(usuario_id, total_venda, carrinho, cliente_id=None, valor_frete=0.0, metodo_pagto="Dinheiro", valor_pago=0.0, troco=0.0):
    conn = conectar()
    if conn is None: raise Error("Sem conexão")
    try:
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")
        status_inicial = 'pendente' if valor_frete > 0 else 'n/a'
        cursor.execute(
            """INSERT INTO vendas 
               (usuario_id, total_venda, cliente_id, valor_frete, status_entrega, metodo_pagamento, valor_pago, troco) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
            (usuario_id, total_venda, cliente_id, valor_frete, status_inicial, metodo_pagto, valor_pago, troco)
        )
        venda_id = cursor.lastrowid
        for item in carrinho:
            cursor.execute("""
                INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_unitario)
                VALUES (?,?,?,?)""", (venda_id, item[0], item[2], item[3]))
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (item[2], item[0]))
        conn.commit()
        return venda_id
    except Error as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

def listar_vendas_detalhadas():
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        sql = """SELECT v.id, v.data_hora, u.nome_completo, c.nome_completo, v.total_venda
            FROM vendas v
            LEFT JOIN usuarios u ON v.usuario_id = u.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.data_hora DESC"""
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f'Erro ao listar historico: {e}')
        return []
    finally:
        if conn: conn.close()

def listar_itens_da_venda(venda_id):
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        sql = """SELECT p.nome, vi.quantidade, vi.preco_unitario, (vi.quantidade * vi.preco_unitario) as subtotal
            FROM venda_itens vi
            JOIN produtos p ON vi.produto_id = p.id
            WHERE vi.venda_id = ?"""
        cursor.execute(sql, (venda_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"Erro ao listar itens: {e}")
        return []
    finally:
        if conn: conn.close()

# --- FUNÇÕES CLIENTES ---
def adicionar_cliente(nome, telefone, email, cpf_cnpj, endereco):
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
        raise e
    finally:
        if conn: conn.close()

def buscar_cliente_por_cpf(cpf_cnpj):
    conn = conectar()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE cpf_cnpj = ?", (cpf_cnpj,))
        return cursor.fetchone()
    except Error as e:
        print(f"Erro ao buscar cliente: {e}")
        return None
    finally:
        if conn: conn.close()

def listar_clientes():
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_completo, telefone, email, cpf_cnpj, endereco FROM clientes ORDER BY nome_completo")
        return cursor.fetchall()
    except Error as e:
        print(f'Erro ao listar clientes: {e}')
        return []
    finally:
        if conn: conn.close()

def atualizar_cliente(id_cliente, nome, telefone, email, cpf_cnpj, endereco):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes 
            SET nome_completo = ?, telefone = ?, email = ?, cpf_cnpj = ?, endereco = ?
            WHERE id = ?
        """, (nome, telefone, email, cpf_cnpj, endereco, id_cliente))
        conn.commit()
    except Error as e:
        print(f"Erro ao atualizar cliente: {e}")
        raise e
    finally:
        if conn: conn.close()

# --- FUNÇÕES FINANCEIRAS ---

def adicionar_movimentacao_manual(descricao, valor, tipo):
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        # categoria_id 1 = Geral (Pode criar lógica de categorias depois)
        cursor.execute("""
            INSERT INTO financeiro_movimentacoes (descricao, valor, tipo, categoria_id)
            VALUES (?, ?, ?, 1)
        """, (descricao, valor, tipo))
        conn.commit()
    except Error as e:
        print(f"Erro financeiro: {e}")
        raise e
    finally:
        if conn: conn.close()

def listar_movimentacoes():
    conn = conectar()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, data_lancamento, descricao, valor, tipo 
            FROM financeiro_movimentacoes 
            ORDER BY data_lancamento DESC
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Erro listar financeiro: {e}")
        return []
    finally:
        if conn: conn.close()