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

    except Error as e:
        print(f"Erro ao criar a tabela: {e}")


# --- FUNÇÕES CRUD ---

def adicionar_produto(nome, quantidade, preco):
    """Adiciona um novo produto ao banco de dados."""
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
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


def atualizar_produto(id, nome, quantidade, preco):
    """Atualiza os dados de um produto com base no seu ID."""
    conn = conectar()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET nome = ?, quantidade = ?, preco = ? WHERE id = ?",
                       (nome, quantidade, preco, id))
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


def inicializar_db():
    """Conecta ao DB e garante que a tabela de produtos exista."""
    conn = conectar()
    if conn is not None:
        criar_tabela(conn)
        conn.close()
    else:
        print("Não foi possível estabelecer conexão com o banco de dados.")


# --- Bloco de teste ---
if __name__ == '__main__':
    # Apague o .db antigo para um teste limpo


    if os.path.exists("estoque.db"):
        os.remove("estoque.db")
        print("Banco de dados antigo removido para um teste limpo.")

    inicializar_db()

    print("\n--- Testando Funções do Banco de Dados ---")
    adicionar_produto("Notebook Gamer", 10, 5500.00);
    adicionar_produto("Mouse Sem Fio", 50, 89.90);
    adicionar_produto("Teclado Mecânico", 25, 350.50)
    print("\n1. Listando produtos após adição:")
    for produto in listar_produtos(): print(produto)

    atualizar_produto(2, "Mouse Sem Fio Logitech", 45, 120.00)
    print("\n2. Listando produtos após atualização do ID 2:")
    for produto in listar_produtos(): print(produto)

    print("\n3. Buscando por 'clado':")
    for produto in buscar_produto("clado"): print(produto)

    remover_produto(1)
    print("\n4. Listando produtos após remoção do ID 1:")
    for produto in listar_produtos(): print(produto)