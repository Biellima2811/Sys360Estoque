import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core import logic_analytics
import os

class TelaAnalytics(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Dashboard Gerencial & Analytics")
        self.geometry("1200x800")
        
        # Ícone
        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone): self.iconbitmap(caminho_icone)
        except: pass

        self._criar_layout()
        self.focus_force()

    def _criar_layout(self):
        # Título
        ttk.Label(self, text="📊 Inteligência de Negócios (BI)", font=("Segoe UI", 18, "bold")).pack(pady=10)
        
        # Botão Atualizar
        ttk.Button(self, text="🔄 Atualizar Dados", command=self._plotar_graficos).pack(pady=5)

        # Container Principal dos Gráficos
        self.frame_graficos = ttk.Frame(self)
        self.frame_graficos.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configuração do Grid (2x2)
        self.frame_graficos.columnconfigure(0, weight=1)
        self.frame_graficos.columnconfigure(1, weight=1)
        self.frame_graficos.rowconfigure(0, weight=1)
        self.frame_graficos.rowconfigure(1, weight=1)

        self._plotar_graficos()

    def _plotar_graficos(self):
        # Limpa gráficos anteriores se houver (para atualizar)
        for widget in self.frame_graficos.winfo_children():
            widget.destroy()

        # --- GRÁFICO 1: VENDAS SEMANAIS (LINHA) ---
        dados_vendas = logic_analytics.obter_vendas_ultimos_7_dias()
        fig1 = Figure(figsize=(5, 4), dpi=100)
        ax1 = fig1.add_subplot(111)
        
        if dados_vendas:
            dias = [d[0] for d in dados_vendas]
            valores = [d[1] for d in dados_vendas]
            ax1.plot(dias, valores, marker='o', color='#2563eb', linewidth=2)
            ax1.set_title("Evolução de Vendas (7 Dias)")
            ax1.grid(True, linestyle='--', alpha=0.6)
            for i, v in enumerate(valores):
                ax1.text(i, v, f"R${v:.0f}", ha='center', va='bottom', fontsize=8)
        else:
            ax1.text(0.5, 0.5, "Sem dados recentes", ha='center')

        canvas1 = FigureCanvasTkAgg(fig1, master=self.frame_graficos)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # --- GRÁFICO 2: TOP 5 PRODUTOS (BARRAS HORIZONTAIS) ---
        top_prods = logic_analytics.obter_top_5_produtos()
        fig2 = Figure(figsize=(5, 4), dpi=100)
        ax2 = fig2.add_subplot(111)

        if top_prods:
            nomes = [p[0] for p in top_prods]
            qtds = [p[1] for p in top_prods]
            # Inverte para o mais vendido ficar em cima
            ax2.barh(nomes[::-1], qtds[::-1], color='#10b981') 
            ax2.set_title("Top 5 Produtos Mais Vendidos")
        else:
            ax2.text(0.5, 0.5, "Sem vendas registradas", ha='center')

        canvas2 = FigureCanvasTkAgg(fig2, master=self.frame_graficos)
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # --- GRÁFICO 3: FINANCEIRO (PIZZA) ---
        entradas, saidas = logic_analytics.obter_balanco_financeiro()
        fig3 = Figure(figsize=(5, 4), dpi=100)
        ax3 = fig3.add_subplot(111)

        if entradas > 0 or saidas > 0:
            labels = ['Receitas', 'Despesas']
            sizes = [entradas, saidas]
            colors = ['#4ade80', '#f87171'] # Verde e Vermelho
            ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax3.set_title(f"Balanço Financeiro (Saldo: R${entradas-saidas:.2f})")
        else:
            ax3.text(0.5, 0.5, "Sem movimentação", ha='center')

        canvas3 = FigureCanvasTkAgg(fig3, master=self.frame_graficos)
        canvas3.draw()
        canvas3.get_tk_widget().grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # --- CARD INFORMATIVO (Resumo Texto) ---
        frame_info = tk.Frame(self.frame_graficos, bg="white", relief="raised", bd=2)
        frame_info.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        tk.Label(frame_info, text="Resumo Geral", font=("Arial", 14, "bold"), bg="white").pack(pady=20)
        tk.Label(frame_info, text=f"Total Vendas (7d): R$ {sum([d[1] for d in dados_vendas]):.2f}", font=("Arial", 12), bg="white").pack(anchor='w', padx=20)
        tk.Label(frame_info, text=f"Produto Campeão: {top_prods[0][0] if top_prods else '---'}", font=("Arial", 12), bg="white").pack(anchor='w', padx=20)
        
        lucro = entradas - saidas
        cor_lucro = "green" if lucro >= 0 else "red"
        tk.Label(frame_info, text=f"Resultado Líquido: R$ {lucro:.2f}", font=("Arial", 16, "bold"), fg=cor_lucro, bg="white").pack(pady=30)