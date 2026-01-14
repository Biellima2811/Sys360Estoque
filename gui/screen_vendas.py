import tkinter as tk
from tkinter import messagebox, ttk
import os
from core import logic_vendas as lg_vendas
from core import logic_produtos as lg_produtos
from core import logic_clientes as lg_clientes
from core import gerador_pdf

class TelaPagamento(tk.Toplevel):
    """Janela popup para escolher forma de pagamento e calcular troco."""
    def __init__(self, parent, total_venda, on_confirmar):
        super().__init__(parent)
        self.title("Finalizar Pagamento")
        self.geometry("400x450")
        self.total_venda = total_venda
        self.on_confirmar = on_confirmar # Função callback para voltar dados
        self.transient(parent)
        self.grab_set()
        
        self._criar_widgets()
        
    def _criar_widgets(self):
        ttk.Label(self, text="Total a Pagar", font=("Arial", 10)).pack(pady=(20,5))
        lbl_total = ttk.Label(self, text=f"R$ {self.total_venda:.2f}", font=("Arial", 22, "bold"), foreground="blue")
        lbl_total.pack(pady=(0, 20))
        
        # Forma de Pagamento
        ttk.Label(self, text="Selecione o Método:").pack(anchor='w', padx=40)
        self.metodo_var = tk.StringVar(value="Dinheiro")
        
        frame_metodos = ttk.Frame(self)
        frame_metodos.pack(pady=5)
        
        rb1 = ttk.Radiobutton(frame_metodos, text="Dinheiro 💵", variable=self.metodo_var, value="Dinheiro", command=self._atualizar_troco)
        rb2 = ttk.Radiobutton(frame_metodos, text="Cartão 💳", variable=self.metodo_var, value="Cartão", command=self._atualizar_troco)
        rb3 = ttk.Radiobutton(frame_metodos, text="Pix ✨", variable=self.metodo_var, value="Pix", command=self._atualizar_troco)
        rb1.pack(side='left', padx=10); rb2.pack(side='left', padx=10); rb3.pack(side='left', padx=10)
        
        # Valor Pago
        ttk.Label(self, text="Valor Recebido (R$):").pack(anchor='w', padx=40, pady=(20,5))
        self.entry_pago = ttk.Entry(self, font=("Arial", 12))
        self.entry_pago.pack(ipadx=10, ipady=5)
        self.entry_pago.insert(0, f"{self.total_venda:.2f}") # Sugere o valor total
        self.entry_pago.bind('<KeyRelease>', lambda e: self._atualizar_troco())
        self.entry_pago.bind('<FocusOut>', lambda e: self._atualizar_troco())
        
        # Troco
        ttk.Label(self, text="Troco:", font=("Arial", 10)).pack(pady=(20,5))
        self.lbl_troco = ttk.Label(self, text="R$ 0.00", font=("Arial", 18, "bold"), foreground="green")
        self.lbl_troco.pack()
        
        # Botão
        ttk.Button(self, text="CONFIRMAR VENDA", command=self._confirmar).pack(fill='x', padx=40, pady=30, ipady=10)
        
        self.bind('<Return>', lambda e: self._confirmar())
        self._atualizar_troco()

    def _atualizar_troco(self):
        try:
            pago = float(self.entry_pago.get().replace(',', '.'))
        except:
            pago = 0.0
            
        # Se não for dinheiro, não tem troco (teoricamente)
        if self.metodo_var.get() != "Dinheiro":
            self.lbl_troco.config(text="---")
            return
            
        troco = pago - self.total_venda
        if troco < 0:
            self.lbl_troco.config(text="Falta R$", foreground="red")
        else:
            self.lbl_troco.config(text=f"R$ {troco:.2f}", foreground="green")

    def _confirmar(self):
        try:
            pago = float(self.entry_pago.get().replace(',', '.'))
        except:
            messagebox.showerror("Erro", "Valor pago inválido.")
            return

        metodo = self.metodo_var.get()
        
        if metodo == "Dinheiro" and pago < self.total_venda:
            messagebox.showwarning("Atenção", "Valor recebido menor que o total!")
            return
            
        troco = pago - self.total_venda if metodo == "Dinheiro" else 0.0
        
        # Retorna os dados para a tela principal
        self.on_confirmar(metodo, pago, troco)
        self.destroy()


class TelaVendas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Frente de Caixa (PDV)")
        self.geometry("950x650")
        self.parent = parent
        self.usuario_atual = parent.usuario_logado
        
        self.carrinho = []
        self.valor_total_venda = 0.0

        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone): self.iconbitmap(caminho_icone)
        except: pass

        self._criar_widgets()
        self.transient(parent)
        self.grab_set()

    def _criar_widgets(self):
        frame_main = ttk.Frame(self, padding="10")
        frame_main.pack(fill='both', expand=True)

        painel_esquerdo = ttk.Frame(frame_main)
        painel_esquerdo.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        painel_direito = ttk.Frame(frame_main, padding="15", relief="sunken")
        painel_direito.pack(side='right', fill='y')
        
        # Cliente
        ttk.Label(painel_direito, text="Selecione o Cliente:").pack(anchor="w")
        clientes_db = lg_clientes.listar_todos_clientes()
        lista_clientes = [f"{c[0]} - {c[1]}" for c in clientes_db]
        self.combo_cliente = ttk.Combobox(painel_direito, values=lista_clientes)
        self.combo_cliente.pack(fill='x', pady=(0, 20))

        # Frete
        frame_frete = ttk.LabelFrame(painel_direito, text="Entrega / Frete")
        frame_frete.pack(fill='x', pady=10)
        
        self.var_tem_entrega = tk.BooleanVar()
        self.chk_entrega = ttk.Checkbutton(frame_frete, text="Incluir Entrega?", variable=self.var_tem_entrega, command=self._toggle_frete)
        self.chk_entrega.pack(anchor='w', padx=5, pady=5)
        
        ttk.Label(frame_frete, text="Valor R$:").pack(anchor='w', padx=5)
        self.entry_frete = ttk.Entry(frame_frete)
        self.entry_frete.pack(fill='x', padx=5, pady=(0,10))
        self.entry_frete.insert(0, "0.00")
        self.entry_frete.config(state='disabled')
        self.entry_frete.bind('<FocusOut>', lambda e: self._atualizar_total())
        self.entry_frete.bind('<Return>', lambda e: self._atualizar_total())

        # Adicionar Produto
        frame_topo = ttk.LabelFrame(painel_esquerdo, text="Adicionar Produto")
        frame_topo.pack(fill='x', pady=(0, 10))

        ttk.Label(frame_topo, text='ID:').grid(row=0, column=0, padx=5, pady=10)
        self.entry_id_produto = ttk.Entry(frame_topo, width=15)
        self.entry_id_produto.grid(row=0, column=1, padx=5)
        self.entry_id_produto.bind('<Return>', lambda e: self.entry_qtd.focus())

        ttk.Button(frame_topo, text='?', width=3, command=self._mostrar_ajuda_ids).grid(row=0, column=2, padx=2)

        ttk.Label(frame_topo, text="Qtd:").grid(row=0, column=3, padx=5)
        self.entry_qtd = ttk.Entry(frame_topo, width=8)
        self.entry_qtd.insert(0, '1')
        self.entry_qtd.grid(row=0, column=4, padx=5)
        self.entry_qtd.bind('<Return>', lambda e: self._adicionar_item())

        ttk.Button(frame_topo, text="Incluir (+)", command=self._adicionar_item).grid(row=0, column=5, padx=15)

        # Carrinho
        frame_carrinho = ttk.LabelFrame(painel_esquerdo, text="Lista de Itens")
        frame_carrinho.pack(fill='both', expand=True)

        colunas = ('id', 'nome', 'qtd', 'unitario', 'subtotal')
        self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=colunas, show='headings', selectmode="browse")
        self.tree_carrinho.heading('id', text='Cód'); self.tree_carrinho.column('id', width=50)
        self.tree_carrinho.heading('nome', text='Produto'); self.tree_carrinho.column('nome', width=250)
        self.tree_carrinho.heading('qtd', text='Qtd'); self.tree_carrinho.column('qtd', width=50)
        self.tree_carrinho.heading('unitario', text='Unit.'); self.tree_carrinho.column('unitario', width=80)
        self.tree_carrinho.heading('subtotal', text='Total'); self.tree_carrinho.column('subtotal', width=80)
        
        self.tree_carrinho.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(frame_carrinho, orient='vertical', command=self.tree_carrinho.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_carrinho.configure(yscrollcommand=scrollbar.set)

        ttk.Button(painel_esquerdo, text="Remover Item", command=self._remover_item_carrinho).pack(side='bottom', anchor='e', pady=5)

        # Totais
        ttk.Label(painel_direito, text="Subtotal Produtos:", font=("Arial", 10)).pack(pady=(20, 0))
        self.lbl_total_grande = ttk.Label(painel_direito, text="R$ 0.00", font=("Arial", 26, "bold"), foreground="#2e8b57")
        self.lbl_total_grande.pack(pady=(5, 20))
        
        ttk.Separator(painel_direito, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Button(painel_direito, text="FINALIZAR (F5)", command=self._abrir_tela_pagamento).pack(fill='x', ipady=10, pady=10)
        ttk.Button(painel_direito, text="Cancelar", command=self.destroy).pack(fill='x', ipady=5)

        self.bind('<F5>', lambda e: self._abrir_tela_pagamento())

    def _toggle_frete(self):
        if self.var_tem_entrega.get():
            self.entry_frete.config(state='normal')
            self.entry_frete.focus()
            self.entry_frete.selection_range(0, 'end')
        else:
            self.entry_frete.delete(0, 'end')
            self.entry_frete.insert(0, "0.00")
            self.entry_frete.config(state='disabled')
            self._atualizar_total()

    def _adicionar_item(self):
        id_str = self.entry_id_produto.get()
        qtd_str = self.entry_qtd.get()
        try:
            prod_tupla, qtd_int = lg_vendas.validar_produto_para_venda(id_str, qtd_str)
            subtotal = prod_tupla[3] * qtd_int
            self.carrinho.append((prod_tupla[0], prod_tupla[1], qtd_int, prod_tupla[3], subtotal))
            self.tree_carrinho.insert('', 'end', values=(prod_tupla[0], prod_tupla[1], qtd_int, f"R${prod_tupla[3]:.2f}", f"R${subtotal:.2f}"))
            self._atualizar_total()
            self.entry_id_produto.delete(0, 'end'); self.entry_qtd.delete(0, 'end'); self.entry_qtd.insert(0, "1")
            self.entry_id_produto.focus()
        except ValueError as e:
            messagebox.showwarning("Atenção", str(e), parent=self)

    def _remover_item_carrinho(self):
        sel = self.tree_carrinho.selection()
        if not sel: return
        idx = self.tree_carrinho.index(sel[0])
        self.tree_carrinho.delete(sel[0])
        if idx < len(self.carrinho): del self.carrinho[idx]
        self._atualizar_total()

    def _atualizar_total(self):
        total_prods = sum(item[4] for item in self.carrinho)
        try: val_frete = float(self.entry_frete.get().replace(',', '.'))
        except: val_frete = 0.0
        self.valor_total_venda = total_prods + val_frete
        self.lbl_total_grande.config(text=f"TOTAL: R${self.valor_total_venda:.2f}")

    def _mostrar_ajuda_ids(self):
        prods = lg_produtos.listar_todos_produtos()
        msg = "\n".join([f"{p[0]} - {p[1]} (Est: {p[2]})" for p in prods[:15]])
        messagebox.showinfo("Produtos (Top 15)", msg)

    # --- NOVA LÓGICA DE PAGAMENTO ---
    def _abrir_tela_pagamento(self):
        if not self.carrinho:
            messagebox.showinfo("Vazio", "Carrinho vazio!", parent=self)
            return
        
        # Abre o popup e passa a função _processar_venda_final como callback
        TelaPagamento(self, self.valor_total_venda, self._processar_venda_final)

    def _processar_venda_final(self, metodo_pagto, valor_pago, troco):
        try:
            # Pega dados básicos
            usuario_id = self.usuario_atual[0]
            cli_sel = self.combo_cliente.get()
            cli_id = int(cli_sel.split(' - ')[0]) if cli_sel and ' - ' in cli_sel else None
            try: val_frete = float(self.entry_frete.get().replace(',', '.'))
            except: val_frete = 0.0

            # Chama Lógica (Agora com dados de Pagto)
            venda_id = lg_vendas.processar_venda_completa(
                usuario_id, self.carrinho, cli_id, val_frete,
                metodo_pagto, valor_pago, troco
            )
            
            # Gera PDF (Agora com dados de Pagto)
            nome_cli = cli_sel.split(' - ')[1] if cli_id else "Consumidor Final"
            nome_vend = self.usuario_atual[1]
            
            path_pdf = gerador_pdf.gerar_cupom_pdf(
                venda_id, self.carrinho, self.valor_total_venda, nome_cli, val_frete, 
                nome_vend, metodo_pagto, valor_pago, troco
            )

            messagebox.showinfo("Sucesso", f"Venda {venda_id} realizada!\nPDF: {path_pdf}")
            
            try:
                import webbrowser
                webbrowser.open(os.path.abspath(path_pdf))
            except: pass
            
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro ao Finalizar", str(e))