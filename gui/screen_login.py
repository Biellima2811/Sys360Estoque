import tkinter as tk
from tkinter import messagebox, ttk
import os
from core import logic_usuarios as lg_usuarios

class TelaLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Login")
        self.geometry("600x400")
        
        # Remove a barra de título (Estilo Moderno)
        self.overrideredirect(True) 
        
        # Centraliza na tela
        largura = 600
        altura = 400
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        self.parent = parent
        self.usuario_logado = None

        # CORREÇÃO: Removemos transient para evitar conflito com app.withdraw()
        # self.transient(parent) 

        self._criar_layout_moderno()

        self.grab_set()
        self.wait_window()

    def _criar_layout_moderno(self):
        # Frame Principal com borda sutil
        main_container = tk.Frame(self, bg="white", relief="raised", bd=2)
        main_container.pack(fill="both", expand=True)

        # --- LADO ESQUERDO (Imagem) ---
        side_frame = tk.Frame(main_container, bg="#2c3e50", width=300)
        side_frame.pack(side="left", fill="y")
        side_frame.pack_propagate(False) # Impede que o frame encolha

        # Carregar Imagem
        try:
            img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "login_side.png"))
            if os.path.exists(img_path):
                self.img_lateral = tk.PhotoImage(file=img_path) # Guarda referência
                lbl_img = tk.Label(side_frame, image=self.img_lateral, bg="#2c3e50")
                lbl_img.pack(expand=True, fill="both")
            else:
                # Fallback se não achar a imagem
                tk.Label(side_frame, text="Sys360", bg="#2c3e50", fg="white", font=("Arial", 24, "bold")).pack(expand=True)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            tk.Label(side_frame, text="Sys360", bg="#2c3e50", fg="white", font=("Arial", 24)).pack(expand=True)

        # --- LADO DIREITO (Formulário) ---
        form_frame = tk.Frame(main_container, bg="white")
        form_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        # Botão fechar (X)
        btn_close = tk.Button(form_frame, text="✕", bg="white", fg="gray", 
                              bd=0, font=("Arial", 12), cursor="hand2",
                              command=self._fechar_sistema)
        btn_close.place(relx=1.0, rely=0.0, anchor="ne")

        # Cabeçalho
        tk.Label(form_frame, text="BEM-VINDO", font=("Helvetica", 18, "bold"), 
                 bg="white", fg="#333").pack(pady=(10, 30))

        # Inputs
        tk.Label(form_frame, text="Usuário", bg="white", fg="gray", anchor="w").pack(fill="x")
        self.entry_login = ttk.Entry(form_frame, font=("Arial", 11))
        self.entry_login.pack(fill="x", pady=(5, 15))

        tk.Label(form_frame, text="Senha", bg="white", fg="gray", anchor="w").pack(fill="x")
        self.entry_senha = ttk.Entry(form_frame, font=("Arial", 11), show="•")
        self.entry_senha.pack(fill="x", pady=(5, 20))

        # Botão Entrar
        btn_entrar = tk.Button(form_frame, text="ENTRAR", bg="#2980b9", fg="white", 
                               font=("Arial", 10, "bold"), bd=0, pady=8, cursor="hand2",
                               command=self._on_login_click)
        btn_entrar.pack(fill="x")
        
        self.entry_senha.bind('<Return>', lambda e: self._on_login_click())

    def _fechar_sistema(self):
        self.usuario_logado = None
        self.destroy()
        self.parent.destroy()

    def _on_login_click(self):
        login = self.entry_login.get()
        senha = self.entry_senha.get()

        try:
            usuario_db = lg_usuarios.verificar_login(login, senha)
            self.usuario_logado = usuario_db
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            self.entry_senha.delete(0, 'end')