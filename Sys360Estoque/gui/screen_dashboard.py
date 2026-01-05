import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os

# Imports da Lógica para buscar os dados dos cards
from core import logic_produtos, logic_financeiro, logic_vendas

class Dashboard(ttk.Frame):
    """
    Frame principal que será exibido na janela da aplicação.
    Substitui a antiga tela direta de produtos.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller # Referência à App principal para chamar métodos
        self.pack(fill='both', expand=True)

        self._criar_cards_topo()
        self._criar_atalhos_centro()
        self._criar_lista_alertas()

    def _criar_cards_topo(self):
        # Frame para os cartões de informação
        frame_cards = ttk.Frame(self)
        frame_cards.pack(fill='x', padx=20, pady=20)

        # -- Card 1: Total Produtos --
        qtd_produtos = len(logic_produtos.listar_todos_produtos())
        self._criar_card(frame_cards, "Produtos Cadastrados", str(qtd_produtos), 0, 'blue')

        # -- Card 2: Saldo Atual --
        saldo = logic_financeiro.obter_saldo_atual()
        cor_saldo = 'green' if saldo >=0 else 'red'
        self._criar_card(frame_cards, 'Saldo em Caixa', f'R${saldo:.2f}', 1, cor_saldo)

        # -- Card 3: Vendas Hoje (Simulação - precisaria de query específica) --
        # Por enquanto vamos deixar estático ou criar uma função futura
        self._criar_card(frame_cards, "Status do Sistema", 'Online', 2, 'gray')
    
    def _criar_card(self, parent, titulo, valor, col, cor_texto):
        frame = ttk.LabelFrame(parent, text=titulo)
        frame.grid(row=0, column=col, padx=10, sticky='ew')

        lbl = ttk.Label(frame, text=valor, font=("Helvetica", 18, "bold"), foreground=cor_texto)
        lbl.pack(padx=20, pady=10)

        parent.grid_columnconfigure(col, weight=1)
    
    def _criar_atalhos_centro(self):
        frame_atalhos = ttk.LabelFrame(self, text='Acesso Rapido')
        frame_atalhos.pack(fill='x', padx=20, pady=10)

        # Botões Grandes
        btn_venda = ttk.Button(frame_atalhos, text='🛒 NOVA VENDA (PDV) - F9', command=self.controller.abrir_tela_vendas)
        btn_venda.grid(row=0, column=0, padx=20, pady=20, ipadx=10, ipady=10, sticky='ew')

        btn_estoque = ttk.Button(frame_atalhos, text="📦 Gerenciar Estoque", command=lambda: self.controller.mudar_tela("estoque"))
        btn_estoque.grid(row=0, column=2, padx=20, pady=20, ipadx=10, ipady=10, sticky='ew')

        btn_clientes = ttk.Button(frame_atalhos, text="👥 Clientes", command=self.controller.abrir_tela_gerenciar_clientes)
        btn_clientes.grid(row=0, column=3, padx=20, pady=20, ipadx=10, ipady=10, sticky='ew')

        frame_atalhos.grid_columnconfigure(0, weight=1)
        frame_atalhos.grid_columnconfigure(1, weight=1)
        frame_atalhos.grid_columnconfigure(2, weight=1)
    
    def _criar_lista_alertas(self):
        frame_alertas = ttk.LabelFrame(self, text="⚠️ Alerta de Estoque Baixo (Menos de 5 un.)")
        frame_alertas.pack(fill='both', expand=True, padx=20, pady=10)

        cols = ('id', 'nome', 'qtd')

        tree = ttk.Treeview(frame_alertas, columns=cols, show='headings', height=5)
        tree.heading('id', text='ID')
        tree.heading('nome', text='Produto')
        tree.heading('qtd', text='Qtd')

        tree.column('id', width=50)
        tree.column('nome', width=300)
        tree.column('qtd', width=50)

        tree.pack(side='left', fill='both', expand=True)

        # Lógica simples para pegar produtos com pouco estoque
        todos = logic_produtos.listar_todos_produtos()

        for produtos in todos:
            # produtos = (id, nome, qtd, ...)
            if produtos[2] < 5:
                tree.insert('', 'end', values=(produtos[0], produtos[1], produtos[2]))