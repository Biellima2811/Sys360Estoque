# gui/screen_historico.py
import tkinter as tk
from tkinter import ttk
import os
from database import db_manager as db

class TelaHistoricoVendas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Histórico de Vendas e Auditoria")
        self.geometry("1000x700")
        
        # Ícone
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        self._criar_layout()
        self._carregar_vendas()

    def _criar_layout(self):
        # === PARTE SUPERIOR: LISTA DE VENDAS ===
        frame_vendas = ttk.LabelFrame(self, text="Registro de Vendas (Clique para ver detalhes)")
        frame_vendas.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ('id', 'data', 'vendedor', 'cliente', 'total')
        self.tree_vendas = ttk.Treeview(frame_vendas, columns=cols, show='headings', selectmode="browse")
        
        self.tree_vendas.heading('id', text="ID")
        self.tree_vendas.heading('data', text="Data/Hora")
        self.tree_vendas.heading('vendedor', text="Vendedor")
        self.tree_vendas.heading('cliente', text="Cliente")
        self.tree_vendas.heading('total', text="Total (R$)")

        self.tree_vendas.column('id', width=50, anchor='center')
        self.tree_vendas.column('data', width=150, anchor='center')
        self.tree_vendas.column('vendedor', width=200)
        self.tree_vendas.column('cliente', width=200)
        self.tree_vendas.column('total', width=100, anchor='e')

        self.tree_vendas.pack(side="left", fill="both", expand=True)
        
        sb_v = ttk.Scrollbar(frame_vendas, orient="vertical", command=self.tree_vendas.yview)
        sb_v.pack(side="right", fill="y")
        self.tree_vendas.configure(yscrollcommand=sb_v.set)

        # Evento de clique
        self.tree_vendas.bind("<<TreeviewSelect>>", self._carregar_itens)

        # === PARTE INFERIOR: ITENS DA VENDA ===
        frame_detalhes = ttk.LabelFrame(self, text="Itens da Venda Selecionada")
        frame_detalhes.pack(fill="both", expand=True, padx=10, pady=10)

        cols_itens = ('produto', 'qtd', 'unit', 'subtotal')
        self.tree_itens = ttk.Treeview(frame_detalhes, columns=cols_itens, show='headings', height=8)
        
        self.tree_itens.heading('produto', text="Produto")
        self.tree_itens.heading('qtd', text="Qtd")
        self.tree_itens.heading('unit', text="Valor Unit.")
        self.tree_itens.heading('subtotal', text="Subtotal")

        self.tree_itens.pack(fill="both", expand=True)

    def _carregar_vendas(self):
        # Limpa tabela
        for i in self.tree_vendas.get_children():
            self.tree_vendas.delete(i)
            
        vendas = db.listar_vendas_detalhadas()
        for v in vendas:
            # v = (id, data, vendedor, cliente, total)
            cliente_nome = v[3] if v[3] else "Consumidor Final"
            self.tree_vendas.insert('', 'end', values=(v[0], v[1], v[2], cliente_nome, f"R$ {v[4]:.2f}"), text=v[0])

    def _carregar_itens(self, event):
        selection = self.tree_vendas.selection()
        if not selection: return

        # Limpa itens antigos
        for i in self.tree_itens.get_children():
            self.tree_itens.delete(i)

        # Pega ID da venda (salvo na propriedade text ou values)
        item = self.tree_vendas.item(selection[0])
        venda_id = item['values'][0] # ID é a primeira coluna

        itens = db.listar_itens_da_venda(venda_id)
        for i in itens:
            # i = (nome, qtd, unit, subtotal)
            self.tree_itens.insert('', 'end', values=(i[0], i[1], f"R$ {i[2]:.2f}", f"R$ {i[3]:.2f}"))