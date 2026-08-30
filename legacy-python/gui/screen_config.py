import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from database import db_manager

class TelaConfiguracao(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Administração & Configurações")
        self.geometry("700x550")
        
        # Tenta carregar ícone
        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone): self.iconbitmap(caminho_icone)
        except: pass
        
        self._criar_interface()
        self._carregar_dados()
        
    def _criar_interface(self):
        # Notebook (Abas)
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # --- ABA 1: Dados da Empresa (Origem das Rotas) ---
        tab_empresa = ttk.Frame(notebook)
        notebook.add(tab_empresa, text="🏢 Dados da Empresa")
        
        frame_emp = ttk.LabelFrame(tab_empresa, text="Cadastro da Matriz / Base", padding=15)
        frame_emp.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_emp, text="Nome Fantasia:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_emp_nome = ttk.Entry(frame_emp, width=50)
        self.entry_emp_nome.grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Label(frame_emp, text="Endereço Base (Origem):").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_emp_end = ttk.Entry(frame_emp, width=70)
        self.entry_emp_end.grid(row=1, column=1, sticky='w', pady=5)
        
        # CORREÇÃO: O estilo (font, foreground) deve ficar dentro do Label(), não do grid()
        ttk.Label(frame_emp, text="(Usado como Ponto A no Google Maps)", 
                  font=("Arial", 8), foreground="gray").grid(row=2, column=1, sticky='w')
        
        ttk.Label(frame_emp, text="Telefone Contato:").grid(row=3, column=0, sticky='w', pady=5)
        self.entry_emp_tel = ttk.Entry(frame_emp, width=30)
        self.entry_emp_tel.grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Button(tab_empresa, text="💾 Salvar Dados da Empresa", command=self.salvar_empresa).pack(pady=10)

        # --- ABA 2: Banco de Dados (Rede) ---
        tab_rede = ttk.Frame(notebook)
        notebook.add(tab_rede, text="🌐 Rede & Banco")
        
        frame_db = ttk.LabelFrame(tab_rede, text="Conexão com Banco de Dados", padding=15)
        frame_db.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_db, text="Caminho do Arquivo (.db):").pack(anchor='w')
        
        frame_busca = ttk.Frame(frame_db)
        frame_busca.pack(fill='x', pady=5)
        
        self.entry_path = ttk.Entry(frame_busca)
        self.entry_path.pack(side='left', fill='x', expand=True)
        
        ttk.Button(frame_busca, text="📂 Buscar", command=self.buscar_arquivo).pack(side='right', padx=5)
        
        # Aqui também corrigi, só por garantia
        ttk.Label(frame_db, text="Dica: Para usar em rede, selecione um arquivo em uma pasta compartilhada (ex: Z:\\Sistema\\estoque.db)", 
                  font=("Arial", 8), foreground="gray").pack(anchor='w', pady=5)

        ttk.Button(tab_rede, text="💾 Salvar Configuração de Rede", command=self.salvar_rede).pack(pady=10)

    def _carregar_dados(self):
        # Carrega Rede
        caminho_atual = db_manager.carregar_caminho_db()
        self.entry_path.insert(0, caminho_atual)
        
        # Carrega Empresa
        dados = db_manager.obter_dados_empresa()
        if dados:
            # dados = (nome, endereco, telefone)
            if dados[0]: self.entry_emp_nome.insert(0, dados[0])
            if dados[1]: self.entry_emp_end.insert(0, dados[1])
            if dados[2]: self.entry_emp_tel.insert(0, dados[2])

    def buscar_arquivo(self):
        filename = filedialog.askopenfilename(title="Selecione o Banco", filetypes=[("SQLite DB", "*.db"), ("Todos", "*.*")])
        if filename:
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, filename)

    def salvar_rede(self):
        novo = self.entry_path.get()
        if novo:
            db_manager.salvar_caminho_db(novo)
            messagebox.showinfo("Sucesso", "Caminho de rede salvo!")

    def salvar_empresa(self):
        try:
            db_manager.salvar_dados_empresa(
                self.entry_emp_nome.get(),
                self.entry_emp_end.get(),
                self.entry_emp_tel.get()
            )
            messagebox.showinfo("Sucesso", "Dados da empresa atualizados!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))