import logging
import os
from datetime import datetime

def configurar_logger():
    """
    Configura o sistema de logs da aplicação.
    Cria uma pasta 'logs' se não existir e define o formato.
    """

    # Cria a pasta logs na raiz do projeto se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Nome do arquivo com data (ex: logs/sys360_2023-10-27.log)
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo = f'logs/sys360_{data_hoje}.log'

    logging.basicConfig(
        level=logging.INFO, # Captura tudo de INFO para cima (INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(nome_arquivo, encoding='utf-8'), # Salva em arquivo
            logging.StreamHandler() # Mostra no console (terminal)
        ]
    )
    
    logging.info("Sistema de logs inicializado.")