import sys
import os
import logging
from core import logger_config

# Configuração de Log
logger = logging.getLogger(__name__)

# Ajuste de caminho
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.app_main import App
from gui.screen_login import TelaLogin
from database import db_manager

def main():
    try:
        # 1. Inicializa Banco
        db_manager.inicializar_db()
        logger.info("Banco de dados inicializado.")

        # 2. Cria a App Principal (mas deixa invisível)
        app = App()
        app.withdraw() 

        # 3. Abre Login como janela modal (bloqueia o resto até fechar)
        # Passamos 'app' como pai para que o Toplevel saiba a quem pertence
        login_window = TelaLogin(app) 
        
        # O código para aqui e espera a janela de login fechar...
        # ...
        # ... Janela de login fechou.

        # 4. Verifica se logou
        if login_window.usuario_logado:
            logger.info(f"Usuário logado: {login_window.usuario_logado[1]}")
            
            # Configura o usuário na App Principal
            app.usuario_logado = login_window.usuario_logado
            
            # Atualiza o rodapé com o nome do usuário (se existir o label)
            if hasattr(app, 'lbl_usuario'):
                app.lbl_usuario.config(text=f"Usuário: {app.usuario_logado[1]}")

            # MÁGICA AQUI: Mostra a janela principal e maximiza
            app.deiconify() 
            app.state('zoomed') 
            
            # Inicia o sistema
            app.mainloop()
        else:
            # Se fechou o login sem entrar, mata tudo
            logger.info("Login cancelado. Encerrando.")
            app.destroy()

    except Exception as e:
        logger.critical(f"Erro fatal no main: {e}", exc_info=True)

if __name__ == "__main__":
    main()