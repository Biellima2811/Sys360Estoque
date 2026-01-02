import tkinter as tk
from tkinter import messagebox, ttk
import os
from datetime import datetime

# Imports da Lógica
from core import logic_financeiro as lg_financeiro

class TelaFinanceiro(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Gestão Financeira")
        self.geometry("900x600")
        self.parent = parent
        self.usuario_atual = parent.usuario_logado

        # Ícone
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        self._criar_widgets()
        self._atualizar_dados() # Carrega dados ao abrir

        # Modal
        self.transient(parent)
        # self.grab_set() # Opcional: Se quiser bloquear a janela principal
        # self.wait_window()
    
    def _criar_widgets(self):
        # --- Layout Principal ---
        # Topo: Cards de Saldo
        # Centro: Tabela de Movimentações
        # Base: Botões de Ação

        # 1. CARDS DE RESUMO (TOPO)
        frame_resumo = ttk.LabelFrame(self, text='Resumo do Caixa')
        frame_resumo.pack(fill='x', padx=10, pady=5)

        # Usando Frame interno para alinhar os cards
        self.lbl_saldo = ttk.Label(frame_resumo, text="Saldo: R$ 0.00",font=("Helvetica", 16, "bold"), foreground="blue")
        self.lbl_saldo.pack(side='right', padx=20, pady=10)

        btn_atualizar = ttk.Button(frame_resumo, text="🔄 Atualizar", command=self._atualizar_dados)
        btn_atualizar.pack(side='right', padx=10,pady=10)

        # 2. TABELA DE MOVIMENTAÇÕES (CENTRO)
        frame_tabela = ttk.Frame(self)
        frame_tabela.pack(fill='both', expand=True, padx=10, pady=5)

        colunas = ('id', 'data', 'desc', 'tipo', 'valor', 'usuario')
        self.tree = ttk.Treeview(frame_tabela, columns=colunas, show='headings')

        self.tree.heading('id', text='ID')
        self.tree.heading('data', text='Data/Hora')
        self.tree.heading('desc', text='Descrição')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('valor', text='Valor (R$)')
        self.tree.heading('usuario', text='Responsável')

        self.tree.column('id', width=40, anchor='center')
        self.tree.column('data', width=120, anchor='center')
        self.tree.column('desc', width=250)
        self.tree.column('tipo', width=80, anchor='center')
        self.tree.column('valor', width=100, anchor='e')
        self.tree.column('usuario', width=150)

        scrollbar = ttk.Scrollbar(frame_tabela, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 3. LANÇAMENTOS MANUAIS (BASE)
        frame_lancamento = ttk.LabelFrame(self, text="Novo Lançamento Manual (Despesas/Aportes)")
        frame_lancamento.pack(fill='x', padx=10, pady=10)

        ttk.Label(frame_lancamento, text="Descrição:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_desc = ttk.Entry(frame_lancamento, width=40)
        self.entry_desc.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_lancamento, text='Valor R$:').grid(row=0, column=2, padx=5, pady=5)
        self.entry_valor = ttk.Entry(frame_lancamento, width=15)
        self.entry_valor.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_lancamento, text='Tipo').grid(row=0, column=4, padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(frame_lancamento, values=['saida', 'entrada'], state='readony', width=10)
        self.combo_tipo.set('saida') # Padrão saída (já que entrada vem de vendas)
        self.combo_tipo.grid(row=0, column=5, padx=5, pady=5)

        btn_lancar = ttk.Button(frame_lancamento, text='Registrar 💾', command=self._registrar_manual, style="Accent.TButton")
        btn_lancar.grid(row=0, column=6, padx=10, pady=5)

    def _atualizar_dados(self):
        """Busca saldo e histórico no banco."""
        # 1. Atualizar Saldo
        saldo = lg_financeiro.obter_saldo_atual()
        cor = 'green' if saldo >= 0 else 'red'
        self.lbl_saldo.config(text=f'Saldo Atual: R${saldo:.2f}', foreground=cor)

        # 2. Atualizar Tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        movimentacoes = lg_financeiro.listar_movimentacoes()
        for mov in movimentacoes:
            # mov = (id, data, desc, tipo, valor, nome_usuario)
            
            # Formatar a cor da linha dependendo se é entrada ou saída
            # (No Treeview padrão é difícil colorir linhas individuais sem tags, vamos manter simples por enquanto)
            
            # Formatar valor e data se necessário
            valor_fmt = f'R$ {mov[4]:.2f}'
            tipo_fmt = mov[3].upper()

            self.tree.insert('', 'end', values=(mov[0], mov[1], mov[2], tipo_fmt, valor_fmt, mov[5]))
    
    def _registrar_manual(self):
        desc = self.entry_desc.get()
        valor_str = self.entry_valor.get()
        tipo = self.combo_tipo.get()

        if not desc or not valor_str:
            messagebox.showwarning("Aviso", 'Preencha desscição e valor!')
            return
        
        try:
            valor = float(valor_str.replace(',', '.'))
            usuario_id = self.usuario_atual[0]

            lg_financeiro.registrar_movimentacao(
                descricao=desc,
                valor=valor,
                tipo=tipo,
                usuario_id=usuario_id
            )

            messagebox.showinfo("Sucesso", 'Lançamento realizado!')
            self.entry_desc.delete(0, 'end')
            self.entry_valor.delete(0, 'end')
            self._atualizar_dados()
        except ValueError:
            messagebox.showerror("Erro", 'Valor invalido. Digite aenas números.')
        except Exception as e:
            messagebox.showerror("Erro", f'Erro ao salvar {e}')
            