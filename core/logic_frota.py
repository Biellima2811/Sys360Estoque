from database import db_manager
import urllib.parse

# --- CADASTRO DE VEÍCULOS ---
def adicionar_veiculo(modelo, placa, capacidade=0):
    if not modelo or not placa:
        raise ValueError("Modelo e Placa são obrigatórios")
    
    conn = db_manager.conectar()
    if not conn: return
    try:
        cursor = conn.cursor()
        # Status padrão ao criar é 'disponivel'
        cursor.execute("INSERT INTO veiculos (modelo, placa, capacidade_kg, status) VALUES (?, ?, ?, 'disponivel')", 
                       (modelo, placa, capacidade))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        conn.close()

def remover_veiculo(veiculo_id):
    conn = db_manager.conectar()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
        conn.commit()
    except Exception as e:
        raise e
    finally:
        conn.close()

def listar_veiculos_disponiveis():
    """Retorna lista de veículos (id, modelo, placa, status)."""
    conn = db_manager.conectar()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, modelo, placa, status FROM veiculos")
        return cursor.fetchall()
    finally:
        conn.close()

# --- GESTÃO DE ENTREGAS ---
def listar_entregas_pendentes():
    """
    Lista vendas com frete que estão 'pendente'.
    DICA: Se você fez vendas antes da correção, elas podem não aparecer.
    """
    conn = db_manager.conectar()
    if not conn: return []
    try:
        cursor = conn.cursor()
        # Garante que pega status 'pendente' E frete > 0
        sql = """
            SELECT v.id, c.nome_completo, c.endereco, v.data_hora
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            WHERE v.status_entrega = 'pendente' AND v.valor_frete > 0
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()

def criar_romaneio_entrega(veiculo_id, lista_venda_ids):
    """Vincula as vendas ao veículo e muda status para 'em_rota'."""
    conn = db_manager.conectar()
    if not conn: return
    try:
        cursor = conn.cursor()
        for vid in lista_venda_ids:
            cursor.execute("""
                UPDATE vendas 
                SET status_entrega = 'em_rota', veiculo_id = ? 
                WHERE id = ?
            """, (veiculo_id, vid))
        
        # Opcional: Atualizar status do veículo
        cursor.execute("UPDATE veiculos SET status = 'em_rota' WHERE id = ?", (veiculo_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def gerar_link_rota(enderecos):
    """Gera link do Google Maps otimizado."""
    base_url = "https://www.google.com/maps/dir/"
    
    rota_parts = []
    # Dica: Você pode descomentar a linha abaixo para fixar a saída da sua loja
    # rota_parts.append(urllib.parse.quote("Av. Paulista, 1000, Sao Paulo")) 
    
    for end in enderecos:
        if end and len(end.strip()) > 3:
            rota_parts.append(urllib.parse.quote(end))
    
    if not rota_parts:
        return "https://www.google.com/maps"
        
    full_url = base_url + "/".join(rota_parts)
    return full_url