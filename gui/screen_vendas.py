import tkinter as tk
from tkinter import messagebox, ttk
import os

# Imports da Lógica
from core import logic_vendas as lg_vendas
from core import logic_produtos as lg_produtos
from core import logic_clientes as lg_clientes

class TelaVendas(tk.Toplevel):
    def __init__(self, parent): # <--- Corrigido com 't' no final
        super().__init__(parent)
        self.title("Sys360 - Frente de Caixa (PDV)")
        self.geometry("900x600")
        self.parent = parent

        # Garante que temos o usuário logado (id, nome, login, hash, role)
        self.usuario_atual = parent.usuario_logado

        # Lista para armazenar itens do carrinho temporariamente
        # Estrutura: [(id, nome, qtd, preco_unit, subtotal), ...]
        self.carrinho = []
        self.valor_total_venda = 0.0

        # --- Ícone ---
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        self._criar_widgets()

        # Configuração Modal
        self.transient(parent) # transitório (pai)
        self.grab_set() # conjunto de captura
        self.wait_window() # janela de espera

    def _criar_widgets(self):
        # --- Frame Principal (Fundo) ---
        frame_main = ttk.Frame(self, padding="10")
        frame_main.pack(fill='both', expand=True)

        # === DIVISÃO EM DOIS PAINÉIS ===
        
        # Painel Esquerdo (Lista e Busca) - Pega todo o espaço disponível
        painel_esquerdo = ttk.Frame(frame_main)
        painel_esquerdo.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Painel Direito (Totais) - Fica fixo na direita
        painel_direito = ttk.Frame(frame_main, padding="15", relief="sunken")
        painel_direito.pack(side='right', fill='y')
        
        clintes_db = lg_clientes.listar_todos_clientes()
        # Cria lista de strings: "ID - Nome"]
        lista_clientes = [f"{c[0]} - {c[1]}" for c in clintes_db]
        
        self.combo_cliente = ttk.Combobox(painel_direito, values=lista_clientes)
        self.combo_cliente.pack(fill='x', pady=(0, 20))

        # ======================================================
        # [ESQUERDA] 1. ÁREA DE INSERÇÃO (TOPO)
        # ======================================================
        frame_topo = ttk.LabelFrame(painel_esquerdo, text="Adicionar Produto")
        frame_topo.pack(fill='x', pady=(0, 10))

        # ID do Produto
        ttk.Label(frame_topo, text='ID:').grid(row=0, column=0, padx=5, pady=10)
        self.entry_id_produto = ttk.Entry(frame_topo, width=15, font=('Arial', 11))
        self.entry_id_produto.grid(row=0, column=1, padx=5, pady=10)
        # Ao dar Enter no ID, pula para Quantidade
        self.entry_id_produto.bind('<Return>', lambda e: self.entry_qtd.focus())

        # Botão Ajuda
        btn_buscar = ttk.Button(frame_topo, text='?', width=3, command=self._mostrar_ajuda_ids)
        btn_buscar.grid(row=0, column=2, padx=2)

        # Quantidade
        ttk.Label(frame_topo, text="Qtd:").grid(row=0, column=3, padx=5, pady=10)
        self.entry_qtd = ttk.Entry(frame_topo, width=8, font=('Arial', 11))
        self.entry_qtd.insert(0, '1')
        self.entry_qtd.grid(row=0, column=4, padx=5, pady=10)
        # Ao dar Enter na Qtd, Adiciona o item
        self.entry_qtd.bind('<Return>', lambda e: self._adicionar_item())

        # Botão Adicionar
        btn_add = ttk.Button(frame_topo, text="Incluir (+)", command=self._adicionar_item)
        btn_add.grid(row=0, column=5, padx=15, pady=10)

        # ======================================================
        # [ESQUERDA] 2. CARRINHO DE COMPRAS (CENTRO)
        # ======================================================
        frame_carrinho = ttk.LabelFrame(painel_esquerdo, text="Lista de Itens")
        frame_carrinho.pack(fill='both', expand=True)

        colunas = ('id', 'nome', 'qtd', 'unitario', 'subtotal')
        self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=colunas, show='headings', selectmode="browse")

        self.tree_carrinho.heading('id', text='Cód')
        self.tree_carrinho.heading('nome', text='Produto')
        self.tree_carrinho.heading('qtd', text='Qtd')
        self.tree_carrinho.heading('unitario', text='Unit.')
        self.tree_carrinho.heading('subtotal', text='Total')

        self.tree_carrinho.column('id', width=50, anchor='center')
        self.tree_carrinho.column('nome', width=250)
        self.tree_carrinho.column('qtd', width=50, anchor='center')
        self.tree_carrinho.column('unitario', width=80, anchor='e')
        self.tree_carrinho.column('subtotal', width=80, anchor='e')

        self.tree_carrinho.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame_carrinho, orient='vertical', command=self.tree_carrinho.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_carrinho.configure(yscrollcommand=scrollbar.set)

        # Botão remover abaixo da lista
        btn_rem = ttk.Button(painel_esquerdo, text="Remover Item Selecionado", command=self._remover_item_carrinho)
        btn_rem.pack(side='bottom', anchor='e', pady=5)

        # ======================================================
        # [DIREITA] 3. TOTAIS E AÇÕES
        # ======================================================
        
        ttk.Label(painel_direito, text="Subtotal", font=("Arial", 10)).pack(pady=(10, 0))
        ttk.Label(painel_direito, text="Cliente:").pack(anchor="w", pady=(15, 5))
        
        # Total Gigante
        self.lbl_total_grande = ttk.Label(painel_direito, text="R$ 0.00", font=("Arial", 30, "bold"), foreground="#2e8b57")
        self.lbl_total_grande.pack(pady=(0, 20))
        
        ttk.Separator(painel_direito, orient='horizontal').pack(fill='x', pady=10)
        
        # Botões Grandes
        btn_finalizar = ttk.Button(painel_direito, text="FINALIZAR (F5)", command=self._finalizar_venda, style="Accent.TButton")
        btn_finalizar.pack(fill='x', ipady=10, pady=10)
        
        btn_cancelar = ttk.Button(painel_direito, text="Cancelar Venda", command=self.destroy)
        btn_cancelar.pack(fill='x', ipady=5, pady=5)

        # Atalho de teclado
        self.bind('<F5>', lambda e: self._finalizar_venda())

    def _adicionar_item(self):
        id_str = self.entry_id_produto.get()
        qtd_str = self.entry_qtd.get()

        try:
            # 1. Chama a lógica para validar (verifica se existe e se tem estoque)
            # Retorna: ( (id, nome, qtd_estoque, preco), qtd_validada_int )
            produto_tupla, qtd_int = lg_vendas.validar_produto_para_venda(id_str, qtd_str)

            # 2. Cálculos locais
            id_prod = produto_tupla[0]
            nome_prod = produto_tupla[1]
            preco_unit = produto_tupla[3]
            subtotal = preco_unit * qtd_int

            # 3. Adiciona na lista 'backend' (self.carrinho)
            # Item: (id, nome, qtd, preco, subtotal)
            item_carrinho = (id_prod, nome_prod, qtd_int, preco_unit, subtotal)
            self.carrinho.append(item_carrinho)

            # 4. Adiciona na visualização (Treeview)
            self.tree_carrinho.insert('', 'end', values=(
                id_prod, 
                nome_prod, 
                qtd_int, f"R${preco_unit:.2f}", 
                f'R${subtotal:.2f}'
            ))

            # 5. Atualiza Total e Limpa campos
            self._atualizar_total()
            self.entry_id_produto.delete(0, 'end')
            self.entry_qtd.delete(0, 'end')
            self.entry_qtd.insert(0, "1")
            self.entry_id_produto.focus()
        except ValueError as e:
            messagebox.showwarning("Atenção", str(e), parent=self)
    
    def _remover_item_carrinho(self):
        """Remove o item selecionado na treeview e na lista lógica."""
        selecionado = self.tree_carrinho.selection()
        if not selecionado:
            return
        
        # Pega o índice do item na Treeview
        index = self.tree_carrinho.index(selecionado[0])

        # Remove da Treeview
        self.tree_carrinho.delete(selecionado[0])
        
        # Remove da lista self.carrinho usando o índice
        if index < len(self.carrinho):
            del self.carrinho[index]
        
        self._atualizar_total()
    
    def _atualizar_total(self):
        total = sum(item[4] for item in self.carrinho)
        self.valor_total_venda = total
        self.lbl_total_grande.config(text=f"TOTAL: R${total:.2f}")
    
    def _finalizar_venda(self):
        cliente_selecionado = self.combo_cliente.get()
        cliente_id = None

        if cliente_selecionado:
            cliente_id = int(cliente_selecionado.split(' - ')[0])
        else:
            pass

        if not self.carrinho:
            messagebox.showinfo("Atenção!!", "O carrinho está vazio!", parent=self)
            return
        
        if not messagebox.askyesno("Confirmação!", f'Finalizar venda no valor de R$ {self.valor_total_venda:.2f}?'):
            return
        
        try:
            # Pega o ID do usuário (índice 0 da tupla de usuário)
            usurio_id = self.usuario_atual[0]

            # Chama a lógica poderosa que faz a transação no BD
            venda_id = lg_vendas.processar_venda_completa(usurio_id, self.carrinho, cliente_id)
            messagebox.showinfo("Sucesso!!", f'Venda {venda_id} registrada com sucesso!')

            self.destroy() # Fecha a tela de vendas
        
        except ValueError as e:
            messagebox.showerror("Erro ao processar venda", str(e), parent=self)
    
    def _mostrar_ajuda_ids(self):
        """Mostra uma lista simples de produtos e IDs para ajudar."""
        # Simplificação: apenas mostra uma mensagem. 
        # Idealmente abriria uma janelinha de busca.
        prods = lg_produtos.listar_todos_produtos()
        msg = "IDs Disponiveis: \n\n"
        for p in prods[:10]: # Mostrar só os 10 primeiros
            msg += f'{p[0]} - {p[1]} (Qtd: {p[2]})\n'
        messagebox.showinfo("Ajuda - Produtos", msg, parent=self)