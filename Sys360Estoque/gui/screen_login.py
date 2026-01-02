# gui/screen_login.py
import tkinter as tk
from tkinter import messagebox, ttk
import os
from core import logic_usuarios as lg_usuarios
# ==========================================================
# --- CLASSE DA TELA DE LOGIN ---
# ==========================================================
class TelaLogin(tk.Toplevel):
    """
    Esta é uma janela 'Toplevel', o que significa que é uma
    janela pop-up que aparece sobre a janela principal.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Login")
        self.geometry("350x200+650+250")
        self.resizable(False, False)

        # --- Define o Ícone ---
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)
        self.parent = parent # Guarda a referência da janela principal

        # --- Atributo para guardar o resultado ---
        self.usuario_logado = None

        # --- Widgets da Tela de Login ---
        self.frame = ttk.Frame(self, padding="20 20 20 20")
        self.frame.pack(expand=True, fill='both')

        lbl_login = ttk.Label(self.frame, text="Usuario: ")
        lbl_login.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.entry_login = ttk.Entry(self.frame, width=30)
        self.entry_login.grid(row=0, column=1, padx=5, pady=5)

        lbl_senha = ttk.Label(self.frame, text="Senha: ")
        lbl_senha.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.entry_senha = ttk.Entry(self.frame, width=30, show='*')
        self.entry_senha.grid(row=1, column=1, padx=5, pady=5)

        btn_login = ttk.Button(self.frame, text="Entrar", command=self._on_login_click, style="Accent.TButton")
        btn_login.grid(row=2, column=0, columnspan=2, pady=20)

        # Foco inicial
        self.entry_login.focus_set()

        # --- Modal ---
        # Esses comandos tornam a janela "modal", ou seja,
        # o usuário NÃO consegue clicar na janela principal
        # enquanto esta não for fechada.
        self.transient(parent) # Mantém a janela no topo
        self.grab_set() # Bloqueia eventos para outras janelas

        # Bloqueia eventos para outras janelas
        self.wait_window()
    
    def _on_login_click(self):
        """Chamado quando o botão 'Entrar' é clicado."""
        login = self.entry_login.get()
        senha = self.entry_senha.get()

        try:
            # 1. TENTA verificar o login (chama o logic.py)
            # Isso pode disparar um 'ValueError'
            usuario_db = lg_usuarios.verificar_login(login, senha)

            # 2. SUCESSO!
            self.usuario_logado = usuario_db # Guarda os dados do usuário
            messagebox.showinfo("Autenticação Validada!", f"Bem-Vindo, {self.usuario_logado[1]}")
            self.destroy() # Fecha a janela de login
        except ValueError as e:
            # 3. FALHA! (O alarme 'ValueError' tocou)
            messagebox.showerror("Aviso!", f'Erro de login: {e}')
            self.entry_senha.delete(0, 'end')# Limpa a senha