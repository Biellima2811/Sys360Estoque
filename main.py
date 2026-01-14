# main.py
import tkinter as tk
from tkinter import ttk
import logging

# Importa as funções de inicialização
from database.db_manager import inicializar_db
from core.logic_usuarios import criar_primeiro_admin
from core.logger_config import configurar_logger
from core.logic_financeiro import adicionar_categoria_padrao
# Importa as classes de Tela
from gui.app_main import App
from gui.screen_login import TelaLogin



if __name__ == "__main__":
    
    # --- 0. Inicializa Logs, DB e Admin ---
    configurar_logger() # <--- INICIA O LOG AQUI
    try:   
        
        inicializar_db()
        criar_primeiro_admin()
        adicionar_categoria_padrao()
        # --- 1. Cria a App principal, mas a esconde ---
        app = App()
        
        app.withdraw()

        # --- 2. Aplica o estilo ---
        estilo = ttk.Style(app)
        estilo.configure("Accent.TButton", font=('Helvetica', 10, 'bold'))

        # --- 3. Mostra a Tela de Login ---
        login_window = TelaLogin(app)
    
        # --- 4. Verifica se o login foi bem-sucedido ---
        if login_window.usuario_logado:
            app.usuario_logado = login_window.usuario_logado
            # SUCESSO!
            app.title(f"Sys360 - (Usuário: {app.usuario_logado[1]})")

            # --- CORREÇÃO AQUI: Carrega o Dashboard e Permissões ---
            app._atualizar_permissoes_interface() # Habilita/Desabilita menus
            app.mostrar_dashboard()               # <--- ESSA LINHA CARREGA A TELA
            
            # --- Lógica de Maximizar ---
            try:
                app.state('zoomed') 
            except:
                app.attributes('-zoomed', True)
            
            app.deiconify()
            app.mainloop()
        else:
            # FALHA!
            print("Login cancelado. Encerrando aplicação.")
            app.destroy()
    except Exception as e:
        # Se o sistema quebrar totalmente, o log vai pegar
        logging.critical(f"Erro crítico no sistema: {e}", exc_info=True)