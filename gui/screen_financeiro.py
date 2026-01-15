import tkinter as tk
from tkinter import ttk, messagebox
from core import logic_financeiro
# Se você usa matplotlib para gráficos, mantenha os imports
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    pass

class TelaFinanceiro(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        
        self._criar_interface()
        self.carregar_dados()

    def _criar_interface(self):
        # Título
        ttk.Label(self, text="💰 Gestão Financeira", font=("Segoe UI", 16, "bold")).pack(anchor='w', padx=20, pady=10)

        # Container Principal (Dividido em Esquerda e Direita)
        paned = ttk.PanedWindow(self, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=5)

        # --- LADO ESQUERDO: Lançamentos ---
        frame_lan = ttk.Frame(paned)
        paned.add(frame_lan, weight=1)

        # Cards de Resumo (Topo Esquerda)
        frame_resumo = ttk.Frame(frame_lan)
        frame_resumo.pack(fill='x', pady=5)
        
        self.card_receita = self._criar_card(frame_resumo, "Receitas", "R$ 0,00", "#27ae60")
        self.card_receita.pack(side='left', fill='x', expand=True, padx=5)
        
        self.card_despesa = self._criar_card(frame_resumo, "Despesas", "R$ 0,00", "#c0392b")
        self.card_despesa.pack(side='left', fill='x', expand=True, padx=5)
        
        self.card_saldo = self._criar_card(frame_resumo, "Saldo", "R$ 0,00", "#2980b9")
        self.card_saldo.pack(side='left', fill='x', expand=True, padx=5)

        # Formulário de Lançamento
        frame_form = ttk.LabelFrame(frame_lan, text="Novo Lançamento", padding=10)
        frame_form.pack(fill='x', padx=5, pady=10)

        ttk.Label(frame_form, text="Descrição:").grid(row=0, column=0, sticky='w')
        self.entry_desc = ttk.Entry(frame_form, width=30)
        self.entry_desc.grid(row=0, column=1, padx=5, sticky='ew')

        ttk.Label(frame_form, text="Valor (R$):").grid(row=0, column=2, sticky='w')
        self.entry_valor = ttk.Entry(frame_form, width=15)
        self.entry_valor.grid(row=0, column=3, padx=5, sticky='ew')

        ttk.Label(frame_form, text="Tipo:").grid(row=1, column=0, sticky='w', pady=5)
        self.combo_tipo = ttk.Combobox(frame_form, values=["Receita", "Despesa"], state="readonly", width=10)
        self.combo_tipo.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.combo_tipo.current(0)

        ttk.Button(frame_form, text="💾 Registrar", command=self.registrar).grid(row=1, column=3, padx=5, pady=5, sticky='ew')

        # Tabela de Movimentações
        frame_tab = ttk.LabelFrame(frame_lan, text="Últimas Movimentações")
        frame_tab.pack(fill='both', expand=True, padx=5, pady=5)

        cols = ('id', 'data', 'desc', 'valor', 'tipo')
        self.tree = ttk.Treeview(frame_tab, columns=cols, show='headings')
        self.tree.heading('id', text='ID'); self.tree.column('id', width=30)
        self.tree.heading('data', text='Data'); self.tree.column('data', width=100)
        self.tree.heading('desc', text='Descrição'); self.tree.column('desc', width=200)
        self.tree.heading('valor', text='Valor'); self.tree.column('valor', width=80)
        self.tree.heading('tipo', text='Tipo'); self.tree.column('tipo', width=80)
        
        self.tree.pack(fill='both', expand=True)

        # --- LADO DIREITO: Gráficos (Analytics) ---
        # Se você tiver matplotlib, aqui entra o gráfico. Senão, deixamos um aviso.
        frame_graf = ttk.LabelFrame(paned, text="Análise Visual", padding=10)
        paned.add(frame_graf, weight=1)
        
        self.area_grafico = tk.Frame(frame_graf, bg="white")
        self.area_grafico.pack(fill='both', expand=True)
        
        # Botão Atualizar
        ttk.Button(frame_graf, text="🔄 Atualizar Dados", command=self.carregar_dados).pack(fill='x', pady=5)

    def _criar_card(self, parent, titulo, valor, cor_texto):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=10, relief="raised")
        ttk.Label(frame, text=titulo, font=("Arial", 10)).pack(anchor='w')
        lbl_valor = ttk.Label(frame, text=valor, font=("Arial", 14, "bold"), foreground=cor_texto)
        lbl_valor.pack(anchor='w')
        # Guarda referência para atualizar depois
        if titulo == "Receitas": self.lbl_receita = lbl_valor
        elif titulo == "Despesas": self.lbl_despesa = lbl_valor
        else: self.lbl_saldo = lbl_valor
        return frame

    def registrar(self):
        desc = self.entry_desc.get()
        valor = self.entry_valor.get()
        tipo = self.combo_tipo.get().lower() # 'receita' ou 'despesa'
        
        if not desc or not valor:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        try:
            # Chama a lógica (Adapte se sua função no logic for diferente)
            # Ex: logic_financeiro.adicionar_movimentacao(desc, valor, tipo)
            # Vou assumir uma função genérica aqui:
            logic_financeiro.registrar_movimento(desc, valor, tipo)
            
            messagebox.showinfo("Sucesso", "Lançamento registrado!")
            self.entry_desc.delete(0, 'end')
            self.entry_valor.delete(0, 'end')
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def carregar_dados(self):
        # Limpa tabela
        for i in self.tree.get_children(): self.tree.delete(i)
        
        try:
            # Carrega lista (Adapte conforme retorno do seu logic)
            movs = logic_financeiro.listar_movimentacoes()
            total_rec = 0
            total_desp = 0
            
            for m in movs:
                # m = (id, data, desc, valor, tipo, ...)
                valor = float(m[3])
                tipo = m[4] # 'entrada' ou 'saida' / 'receita' ou 'despesa'
                
                # Formata valor
                val_str = f"R$ {valor:.2f}"
                
                self.tree.insert('', 'end', values=(m[0], m[1], m[2], val_str, tipo))
                
                if tipo in ['receita', 'entrada']:
                    total_rec += valor
                else:
                    total_desp += valor
            
            # Atualiza Cards
            saldo = total_rec - total_desp
            self.lbl_receita.config(text=f"R$ {total_rec:.2f}")
            self.lbl_despesa.config(text=f"R$ {total_desp:.2f}")
            self.lbl_saldo.config(text=f"R$ {saldo:.2f}", foreground="#27ae60" if saldo >= 0 else "#c0392b")
            
            # Se quiser, chame a função de desenhar gráfico aqui
            self._desenhar_grafico(total_rec, total_desp)
            
        except Exception as e:
            print(f"Erro ao carregar financeiro: {e}")

    def _desenhar_grafico(self, rec, desp):
        # Verifica se matplotlib está disponível
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            tk.Label(self.area_grafico, text="Instale 'matplotlib' para ver gráficos", bg="white").place(relx=0.5, rely=0.5, anchor='center')
            return

        # Limpa gráfico anterior
        for widget in self.area_grafico.winfo_children():
            widget.destroy()

        # Cria Figura
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Dados
        labels = ['Receitas', 'Despesas']
        valores = [rec, desp]
        cores = ['#27ae60', '#c0392b']
        
        if rec == 0 and desp == 0:
            ax.text(0.5, 0.5, "Sem dados", ha='center')
        else:
            ax.pie(valores, labels=labels, autopct='%1.1f%%', colors=cores, startangle=90)
            ax.set_title("Balanço Financeiro")

        # Renderiza no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.area_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)