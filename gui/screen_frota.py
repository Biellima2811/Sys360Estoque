import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from core import logic_frota
import os

class ScreenFrota(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Gestão de Expedição e Frota")
        self.geometry("1150x700")
        
        # Ícone
        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone):
                self.iconbitmap(caminho_icone)
        except: pass

        self._criar_interface()
        self.focus_force()

    def _criar_interface(self):
        # Topo
        frame_topo = ttk.Frame(self)
        frame_topo.pack(fill='x', padx=20, pady=10)
        ttk.Label(frame_topo, text="🚚 Gestão de Frota & Expedição", font=("Segoe UI", 18, "bold")).pack(side='left')
        
        # Container Dividido
        paned = ttk.PanedWindow(self, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=5)

        # --- ESQUERDA: Veículos ---
        frame_esq = ttk.Frame(paned)
        paned.add(frame_esq, weight=1)

        # Cadastro Rápido
        frame_cad = ttk.LabelFrame(frame_esq, text="Novo Veículo", padding=10)
        frame_cad.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(frame_cad, text="Modelo:").grid(row=0, column=0, sticky='w')
        self.entry_modelo = ttk.Entry(frame_cad, width=15)
        self.entry_modelo.grid(row=0, column=1, padx=5, sticky='ew')
        
        ttk.Label(frame_cad, text="Placa:").grid(row=1, column=0, sticky='w')
        self.entry_placa = ttk.Entry(frame_cad, width=15)
        self.entry_placa.grid(row=1, column=1, padx=5, sticky='ew')
        
        ttk.Button(frame_cad, text="Salvar", command=self.adicionar_veiculo).grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

        # Lista Veículos
        frame_lista_v = ttk.LabelFrame(frame_esq, text="Veículos Disponíveis")
        frame_lista_v.pack(fill='both', expand=True, padx=5, pady=5)
        
        cols_v = ('id', 'modelo', 'placa', 'status')
        self.tree_v = ttk.Treeview(frame_lista_v, columns=cols_v, show='headings')
        self.tree_v.heading('id', text='ID'); self.tree_v.column('id', width=30)
        self.tree_v.heading('modelo', text='Modelo'); self.tree_v.column('modelo', width=100)
        self.tree_v.heading('placa', text='Placa'); self.tree_v.column('placa', width=80)
        self.tree_v.heading('status', text='Status'); self.tree_v.column('status', width=80)
        self.tree_v.pack(fill='both', expand=True)

        # --- DIREITA: Entregas ---
        frame_dir = ttk.LabelFrame(paned, text="📦 Entregas Pendentes (Selecione Várias)")
        paned.add(frame_dir, weight=2)
        
        cols_e = ('id', 'cliente', 'endereco', 'data')
        self.tree_e = ttk.Treeview(frame_dir, columns=cols_e, show='headings')
        self.tree_e.heading('id', text='Venda'); self.tree_e.column('id', width=50)
        self.tree_e.heading('cliente', text='Cliente'); self.tree_e.column('cliente', width=150)
        self.tree_e.heading('endereco', text='Endereço'); self.tree_e.column('endereco', width=250)
        self.tree_e.heading('data', text='Data'); self.tree_e.column('data', width=100)
        self.tree_e.pack(fill='both', expand=True, padx=5, pady=5)

        # Ações
        frame_bot = ttk.Frame(self)
        frame_bot.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(frame_bot, text="🔄 Atualizar Listas", command=self.carregar_dados).pack(side='left')
        ttk.Button(frame_bot, text="🗺️ Gerar Rota (Google Maps)", command=self.gerar_rota).pack(side='right')

        self.carregar_dados()

    def carregar_dados(self):
        # Limpa tudo
        for i in self.tree_v.get_children(): self.tree_v.delete(i)
        for i in self.tree_e.get_children(): self.tree_e.delete(i)
        
        # Preenche Veículos
        for v in logic_frota.listar_veiculos_disponiveis():
            self.tree_v.insert('', 'end', values=v)
            
        # Preenche Entregas
        for e in logic_frota.listar_entregas_pendentes():
            # Trata endereço vazio
            end = e[2] if e[2] else "---"
            self.tree_e.insert('', 'end', values=(e[0], e[1], end, e[3]))

    def adicionar_veiculo(self):
        try:
            logic_frota.adicionar_veiculo(self.entry_modelo.get(), self.entry_placa.get())
            messagebox.showinfo("Sucesso", "Veículo adicionado!")
            self.entry_modelo.delete(0, 'end'); self.entry_placa.delete(0, 'end')
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def gerar_rota(self):
        # 1. Pega Veículo
        sel_v = self.tree_v.selection()
        if not sel_v:
            messagebox.showwarning("Ops", "Selecione um veículo na esquerda.")
            return
        v_id = self.tree_v.item(sel_v[0])['values'][0]

        # 2. Pega Entregas
        sel_e = self.tree_e.selection()
        if not sel_e:
            messagebox.showwarning("Ops", "Selecione as entregas na direita.")
            return
        
        vendas_ids = []
        enderecos = []
        for item in sel_e:
            vals = self.tree_e.item(item)['values']
            vendas_ids.append(vals[0])
            enderecos.append(vals[2])

        # 3. Executa
        if messagebox.askyesno("Confirmar", f"Despachar {len(vendas_ids)} entregas?"):
            try:
                logic_frota.criar_romaneio_entrega(v_id, vendas_ids)
                link = logic_frota.gerar_link_rota(enderecos)
                webbrowser.open(link)
                self.carregar_dados()
            except Exception as e:
                messagebox.showerror("Erro", str(e))