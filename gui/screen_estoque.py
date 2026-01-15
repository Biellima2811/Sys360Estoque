import tkinter as tk
from tkinter import ttk, messagebox
from core import logic_produtos

class TelaEstoque(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        self._criar_interface()
        self.popular_tabela()

    def _criar_interface(self):
        # Título da Seção
        ttk.Label(self, text="📦 Gestão de Estoque", font=("Segoe UI", 16, "bold")).pack(anchor='w', padx=20, pady=10)

        # --- Formulário ---
        frame_dados = ttk.LabelFrame(self, text="Dados do Produto", padding=10)
        frame_dados.pack(fill='x', padx=20, pady=5)

        # Grid de Inputs
        grid_frame = ttk.Frame(frame_dados)
        grid_frame.pack(fill='x')

        # Linha 1
        ttk.Label(grid_frame, text="Nome do Produto:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nome = ttk.Entry(grid_frame, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(grid_frame, text="Categoria:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_cat = ttk.Entry(grid_frame, width=20)
        self.entry_cat.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Linha 2
        ttk.Label(grid_frame, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_qtd = ttk.Entry(grid_frame, width=15)
        self.entry_qtd.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(grid_frame, text="Fornecedor:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.entry_forn = ttk.Entry(grid_frame, width=20)
        self.entry_forn.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Linha 3
        ttk.Label(grid_frame, text="Preço Custo (R$):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_custo = ttk.Entry(grid_frame, width=15)
        self.entry_custo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(grid_frame, text="Preço Venda (R$):").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.entry_venda = ttk.Entry(grid_frame, width=15)
        self.entry_venda.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(3, weight=1)

        # --- Botões de Ação ---
        frame_acoes = ttk.Frame(self)
        frame_acoes.pack(fill='x', padx=20, pady=10)

        # Busca (Esquerda)
        frame_busca = ttk.Frame(frame_acoes)
        frame_busca.pack(side='left')
        self.entry_busca = ttk.Entry(frame_busca, width=25)
        self.entry_busca.pack(side='left', padx=5)
        ttk.Button(frame_busca, text="🔍 Buscar", command=self.buscar).pack(side='left')

        # CRUD (Direita)
        ttk.Button(frame_acoes, text="🗑️ Remover", command=self.remover).pack(side='right', padx=5)
        ttk.Button(frame_acoes, text="✏️ Atualizar", command=self.atualizar).pack(side='right', padx=5)
        ttk.Button(frame_acoes, text="➕ Adicionar", command=self.adicionar).pack(side='right', padx=5)
        ttk.Button(frame_acoes, text="🧹 Limpar", command=self.limpar_campos).pack(side='right', padx=5)

        # --- Tabela ---
        frame_tabela = ttk.Frame(self)
        frame_tabela.pack(fill='both', expand=True, padx=20, pady=10)

        cols = ("id", "nome", "qtd", "venda", "custo", "cat", "forn")
        self.tree = ttk.Treeview(frame_tabela, columns=cols, show='headings', selectmode='browse')
        
        # Cabeçalhos
        headers = {"id": "ID", "nome": "Produto", "qtd": "Qtd", "venda": "Venda (R$)", "custo": "Custo (R$)", "cat": "Categoria", "forn": "Fornecedor"}
        widths = {"id": 40, "nome": 250, "qtd": 50, "venda": 80, "custo": 80, "cat": 100, "forn": 100}

        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c])
            if c in ['qtd', 'id', 'venda', 'custo']:
                self.tree.column(c, anchor='center')

        # Scrollbar
        scrolly = ttk.Scrollbar(frame_tabela, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrolly.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrolly.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self.ao_selecionar)

    # --- Lógica ---
    def popular_tabela(self, lista=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        if lista is None:
            lista = logic_produtos.listar_todos_produtos()
            
        for p in lista:
            # p = (id, nome, qtd, preco(legacy), venda, custo, cat, forn)
            # Ajuste os índices conforme seu banco
            try:
                self.tree.insert('', 'end', text=p[0], values=(p[0], p[1], p[2], f"{p[4]:.2f}", f"{p[5]:.2f}", p[6], p[7]))
            except IndexError:
                pass

    def ao_selecionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        # item = [id, nome, qtd, venda, custo, cat, forn]
        
        self.limpar_campos()
        self.entry_nome.insert(0, item[1])
        self.entry_qtd.insert(0, item[2])
        self.entry_venda.insert(0, item[3])
        self.entry_custo.insert(0, item[4])
        self.entry_cat.insert(0, item[5])
        self.entry_forn.insert(0, item[6])

    def limpar_campos(self):
        for e in [self.entry_nome, self.entry_qtd, self.entry_venda, self.entry_custo, self.entry_cat, self.entry_forn]:
            e.delete(0, 'end')
        self.tree.selection_remove(self.tree.selection())

    def adicionar(self):
        try:
            logic_produtos.adicionar_produto(
                self.entry_nome.get(), self.entry_qtd.get(), self.entry_venda.get(),
                self.entry_custo.get(), self.entry_cat.get(), self.entry_forn.get()
            )
            messagebox.showinfo("Sucesso", "Produto adicionado!")
            self.limpar_campos()
            self.popular_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def atualizar(self):
        sel = self.tree.selection()
        if not sel: return
        id_prod = self.tree.item(sel[0])['values'][0]
        try:
            logic_produtos.atualizar_produto(
                id_prod, self.entry_nome.get(), self.entry_qtd.get(), self.entry_venda.get(),
                self.entry_custo.get(), self.entry_cat.get(), self.entry_forn.get()
            )
            messagebox.showinfo("Sucesso", "Produto atualizado!")
            self.limpar_campos()
            self.popular_tabela()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def remover(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "Excluir este produto?"):
            id_prod = self.tree.item(sel[0])['values'][0]
            try:
                logic_produtos.remover_produto(id_prod)
                self.limpar_campos()
                self.popular_tabela()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def buscar(self):
        termo = self.entry_busca.get()
        try:
            res = logic_produtos.buscar_produtos(termo)
            self.popular_tabela(res)
        except Exception as e:
            messagebox.showerror("Erro", str(e))