# main.py
import tkinter as tk
from tkinter import ttk

# Importa as funções de inicialização
from database.db_manager import inicializar_db
from core.logic_usuarios import criar_primeiro_admin

# Importa as classes de Tela
from gui.app_main import App
from gui.screen_login import TelaLogin

if __name__ == "__main__":
    
    # --- 0. Inicializa o DB e cria o admin ---
    # (Movido do _backup_app.py para cá)
    inicializar_db()
    criar_primeiro_admin()

    # --- 1. Cria a App principal, mas a esconde ---
    app = App()
    app.withdraw()

    # --- 2. Aplica o estilo ---
    estilo = ttk.Style(app)
    estilo.configure("Accent.TButton", font=('Helvetica', 9, 'bold'))

    # --- 3. Mostra a Tela de Login ---
    login_window = TelaLogin(app)
    
    # --- 4. Verifica se o login foi bem-sucedido ---
    if login_window.usuario_logado:
        # SUCESSO!
        app.usuario_logado = login_window.usuario_logado
        app.title(f"Sys360 - (Usuário: {app.usuario_logado[2]})")
        
        # Constrói os widgets e popula a tabela AGORA
        app.criar_widgets()
        app.popular_tabela()
        
        app.deiconify()
        app.mainloop()
    else:
        # FALHA!
        print("Login cancelado. Encerrando aplicação.")
        app.destroy()