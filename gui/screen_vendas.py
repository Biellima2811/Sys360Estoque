import tkinter as tk
from tkinter import messagebox, ttk
import os

# Imports da Lógica
from core import logic_vendas as lg_vendas
from core import logic_produtos as lg_produtos

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
        # --- Frame Principal ---
        frame_main = ttk.Frame(self, padding="10")
        frame_main.pack(fill='both', expand=True)

        # ======================================================
        # 1. ÁREA DE INSERÇÃO DE PRODUTOS (TOPO)
        # ======================================================
        frame_topo = ttk.LabelFrame(frame_main, text="Adicionar Produto ao Carrinho")
        frame_topo.pack(fill='x', padx=5, pady=5)

        # ID do Produto
        ttk.Label(frame_topo, text='ID do Produto:').grid(row=0, column=0, padx=5, pady=5)
        self.entry_id_produto = ttk.Entry(frame_topo, width=15)
        self.entry_id_produto.grid(row=0, column=1, padx=5, pady=5)
        self.entry_id_produto.bind('<Return>', lambda e: self.entry_qtd.focus())# Enter pula para qtd

        # Botão de Busca Rápida (Opcional, mas útil)
        btn_buscar = ttk.Button(frame_topo, text='?', width=3, command=self._mostrar_ajuda_ids)
        btn_buscar.grid(row=0, column=2, padx=2)

        # Quantidade
        ttk.Label(frame_topo, text="Quantidade").grid(row=0, column=3, padx=5, pady=5)
        self.entry_qtd = ttk.Entry(frame_topo, width=10)
        self.entry_qtd.insert(0, '1') # Valor padrão
        self.entry_qtd.grid(row=0, column=4, padx=5, pady=5)
        self.entry_qtd.bind('<Return>', lambda e: self_adicionar_item()) # Enter adiciona

        # Botão Adicionar
        btn_add = ttk.Button(frame_topo, text="Adicionar item (+)", command=self._adicionar_item)
        btn_add.grid(row=0, column=6, padx=10, pady=5)


        # ======================================================
        # 2. CARRINHO DE COMPRAS (CENTRO)
        # ======================================================

        frame_carrinho = ttk.Label(frame_main, text="Carrinho de Compras")
        frame_carrinho.pack(fill='both', expand=True, padx=5, pady=5)

        colunas = ('id', 'nome', 'qtd', 'unitario', 'subtotal')
        self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=colunas, show='headings')

        self.tree_carrinho.heading('id', text='COD')
        self.tree_carrinho.heading('id', text='Cód')
        self.tree_carrinho.heading('nome', text='Produto')
        self.tree_carrinho.heading('qtd', text='Qtd')
        self.tree_carrinho.heading('unitario', text='Preço Unit.')
        self.tree_carrinho.heading('subtotal', text='Subtotal')

        self.tree_carrinho.column('id', width=50, anchor='center')
        self.tree_carrinho.column('nome', width=300)
        self.tree_carrinho.column('qtd', width=50, anchor='center')
        self.tree_carrinho.column('unitario', width=100, anchor='e')
        self.tree_carrinho.column('subtotal', width=100, anchor='e')

        self.tree_carrinho.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame_carrinho, orient='vertical', command=self.tree_carrinho.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_carrinho.configure(yscrollcommand=scrollbar.set)

        # ======================================================
        # 3. RODAPÉ (TOTAL E FINALIZAR)
        # ======================================================
        frame_footer = ttk.Frame(frame_main)
        frame_footer.pack(fill='x', padx=5, pady=10)

        # Label Total Gigante
        self.lbl_total= ttk.Label(frame_footer, text="TOTAL: R$ 0.00", font=("Helvetica", 16, "bold"), foreground="blue")
        self.lbl_total.pack(side='left', padx=10)

        # Botão Finalizar
        btn_finalizar = ttk.Button(frame_footer, text="FINALIZAR VENDA (F5)", command=self._finalizar_venda, style="Accent.TButton")
        btn_finalizar.pack(side='right', padx=10, ipadx=10, ipady=5)

        # Bind de tecla de atalho
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
        self.lbl_total.config(text=f"TOTAL: R${total:.2f}")
    
    def _finalizar_venda(self):
        if not self.carrinho:
            messagebox.showinfo("Atenção!!", "O carrinho está vazio!", parent=self)
            return
        
        if not messagebox.askyesno("Confirmação!", f'Finalizar venda no valor de R$ {self.valor_total_venda:.2f}?'):
            return
        
        try:
            # Pega o ID do usuário (índice 0 da tupla de usuário)
            usurio_id = self.usuario_atual[0]

            # Chama a lógica poderosa que faz a transação no BD
            venda_id = lg_vendas.processar_venda_completa(usurio_id, self.carrinho)
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