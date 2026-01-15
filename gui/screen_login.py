import tkinter as tk
from tkinter import messagebox, ttk
from database import db_manager
import bcrypt
import os

class TelaLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login - Sys360")
        self.geometry("850x550") # Janela mais larga para o visual moderno
        self.resizable(False, False)
        
        # Variável de retorno
        self.usuario_logado = None
        self.parent = parent

        # Carregar Ícone da Janela
        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone): self.iconbitmap(caminho_icone)
        except: pass

        self._criar_interface_moderna()
        self._centralizar_janela()

        # Torna Modal
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _centralizar_janela(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _criar_interface_moderna(self):
        # --- DIVISÃO DA TELA (Esquerda / Direita) ---
        
        # 1. Lado Esquerdo (Imagem/Banner)
        self.frame_side = tk.Frame(self, bg="#2c3e50", width=400)
        self.frame_side.pack(side='left', fill='both')
        self.frame_side.pack_propagate(False) # Impede que o frame encolha

        # Tentar carregar a imagem 'login_side.png'
        try:
            caminho_img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "login_side.png"))
            if os.path.exists(caminho_img):
                # O PhotoImage nativo do TKinter suporta PNG
                self.img_side = tk.PhotoImage(file=caminho_img)
                lbl_img = tk.Label(self.frame_side, image=self.img_side, bg="#2c3e50")
                lbl_img.place(x=0, y=0, relwidth=1, relheight=1) # Estica ou centraliza
            else:
                # Se não tiver imagem, mostra texto elegante
                tk.Label(self.frame_side, text="Sys360", font=("Segoe UI", 40, "bold"), fg="white", bg="#2c3e50").pack(expand=True)
                tk.Label(self.frame_side, text="Gestão Inteligente", font=("Segoe UI", 14), fg="#bdc3c7", bg="#2c3e50").place(relx=0.5, rely=0.6, anchor='center')
        except Exception as e:
            # Fallback seguro
            tk.Label(self.frame_side, text="Sys360", font=("Arial", 30), fg="white", bg="#2c3e50").pack(expand=True)

        # 2. Lado Direito (Formulário)
        self.frame_form = tk.Frame(self, bg="white")
        self.frame_form.pack(side='right', fill='both', expand=True)

        # Container centralizado no lado direito
        frame_center = tk.Frame(self.frame_form, bg="white")
        frame_center.place(relx=0.5, rely=0.5, anchor='center', width=300)

        # Título
        tk.Label(frame_center, text="Bem-vindo", font=("Segoe UI", 24, "bold"), bg="white", fg="#333").pack(pady=(0, 5))
        tk.Label(frame_center, text="Faça login para continuar", font=("Segoe UI", 10), bg="white", fg="#7f8c8d").pack(pady=(0, 30))

        # Campo Usuário
        tk.Label(frame_center, text="USUÁRIO", font=("Segoe UI", 8, "bold"), bg="white", fg="#95a5a6").pack(anchor='w')
        self.entry_user = ttk.Entry(frame_center, font=("Segoe UI", 11))
        self.entry_user.pack(fill='x', pady=(5, 20), ipady=3)
        self.entry_user.focus()

        # Campo Senha
        tk.Label(frame_center, text="SENHA", font=("Segoe UI", 8, "bold"), bg="white", fg="#95a5a6").pack(anchor='w')
        self.entry_pass = ttk.Entry(frame_center, show="•", font=("Segoe UI", 11))
        self.entry_pass.pack(fill='x', pady=(5, 30), ipady=3)
        
        self.entry_pass.bind('<Return>', lambda e: self.verificar_login())

        # Botão com visual moderno (Flat)
        self.btn_entrar = tk.Button(frame_center, text="ACESSAR SISTEMA", command=self.verificar_login,
                                    bg="#2980b9", fg="white", font=("Segoe UI", 10, "bold"), 
                                    bd=0, cursor="hand2", activebackground="#3498db", activeforeground="white")
        self.btn_entrar.pack(fill='x', ipady=10)

        # Rodapé
        tk.Label(frame_center, text="Sys360 v1.0", font=("Arial", 8), bg="white", fg="#bdc3c7").pack(pady=(40, 0))

        # Efeito Hover no botão
        self.btn_entrar.bind("<Enter>", lambda e: self.btn_entrar.config(bg="#3498db"))
        self.btn_entrar.bind("<Leave>", lambda e: self.btn_entrar.config(bg="#2980b9"))

    def verificar_login(self):
        login = self.entry_user.get()
        senha = self.entry_pass.get()

        if not login or not senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        # Backdoor (Mantenha ou remova em produção)
        if login == "admin" and senha == "admin":
            self.usuario_logado = (1, "Administrador Master", "admin", "hash", "admin")
            self.destroy()
            return

        try:
            usuario_banco = db_manager.buscar_usuario_por_login(login)
            if usuario_banco:
                senha_hash = usuario_banco[3]
                # Verifica hash ou senha simples (para compatibilidade com admin antigo)
                if senha_hash == "admin" and senha == "admin": # Caso o hash no banco seja texto plano
                     self.usuario_logado = usuario_banco
                     self.destroy()
                elif bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                    self.usuario_logado = usuario_banco
                    self.destroy()
                else:
                    messagebox.showerror("Erro", "Senha incorreta.")
            else:
                messagebox.showerror("Erro", "Usuário não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha no login: {e}")