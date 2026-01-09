from database import db_manager as db
import logging

def cadastrar_veiculo(placa, modelo, marca ,ano, capacidade):
    """Registra um novo veículo."""
    if not placa or not modelo:
        raise ValueError('Placa e Modelo são obrigatorios')
    
    conn = db.conectar()
    
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO veiculos (placa, modelo, marca, ano, capacidade_kg)
                       VALUES (?, ?, ?, ?, ?)""", (placa.upper(), modelo, marca, ano, capacidade))
        conn.commit()
        logging.info(f'Veículo {placa}, foi cadastrado com sucesso!')

    except Exception as e:
        logging.error(f'Erro ao cadastrar veiculo: {e}')
        raise ValueError(f'Erro ao salvar (Verifique se a placa já existe na base): {e}')

def listar_veiculos():
    """Retorna todos os veículos."""
    conn = db.conectar()
    if not conn: return [] # Caso não tendo conexão retorne um lista
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM veiculos ORDER BY modelo')
        return cursor.fetchall()
    except Exception as e:
        logging.error(f'Erro ao listar veículos: {e}')
        return []
    finally:
        conn.close()


def calcular_frete_estimado(distancia_km, peso_kg, custo_litro = 6.0, consumo_medio=10.0):
    """
    Calcula um frete base.
    Fórmula simples: (Combustível gasto) + (Taxa por Kg) + Lucro/Margem
    """
    try:
        distancia = float(distancia_km)
        peso = float(peso_kg)

        # Custo de Combustível (Ida e Volta)
        litros_necessarios = (distancia * 2) / consumo_medio
        custo_combustivel = litros_necessarios * custo_litro

        # Adicional por peso (ex: R$ 0.10 por kg) e Taxa Fixa
        taxa_peso = peso * 0.10
        taxa_manuseio = 50.00

        total = custo_combustivel + taxa_peso + taxa_manuseio
        
        return total
    except ValueError as e:
        logging.error(f"Valores de distancia ou peso invalidos!: {e}")
        raise ValueError (f"Valores de distancia ou peso invalidos!: {e}")
        