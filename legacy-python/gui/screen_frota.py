import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import urllib.parse
import os
from core import logic_frota
from database import db_manager  # Importação correta do banco

class ScreenFrota(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Gestão de Expedição e Frota")
        self.geometry("1150x700")
        
        # Ícone (Corrigido 'Tente' para 'try')
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
        frame_dir = ttk.LabelFrame(paned, text="📦 Entregas Pendentes (Selecione para Rota)")
        paned.add(frame_dir, weight=2)
        
        # Colunas: 0=ID, 1=Cliente, 2=Endereço, 3=Data
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
        # O botão agora chama a nova função inteligente
        ttk.Button(frame_bot, text="🗺️ Gerar Rota (Google Maps)", command=self.gerar_rota_inteligente).pack(side='right')

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

    def gerar_rota_inteligente(self):
        """
        Função unificada que gera a rota considerando a Origem da Empresa
        e múltiplos destinos selecionados.
        """
        # 1. Verifica Seleção
        sel_e = self.tree_e.selection()
        if not sel_e:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma entrega na lista da direita.")
            return

        # 2. Pega endereço de Origem (Empresa)
        dados_empresa = db_manager.obter_dados_empresa()
        endereco_origem = ""
        if dados_empresa and dados_empresa[1]:
            endereco_origem = dados_empresa[1]

        # 3. Coleta os destinos selecionados
        enderecos_destino = []
        for item in sel_e:
            vals = self.tree_e.item(item)['values']
            # O endereço é o índice 2 (conforme definido nas colunas)
            end_cliente = vals[2]
            if end_cliente and end_cliente != "---":
                enderecos_destino.append(end_cliente)
        
        if not enderecos_destino:
            messagebox.showwarning("Erro", "As entregas selecionadas não possuem endereço válido.")
            return

        # 4. Monta a URL do Google Maps
        # Formato: https://www.google.com/maps/dir/Origem/Destino1/Destino2...
        
        base_url = "https://www.google.com/maps/dir"
        rota_parts = []
        
        # Se tiver origem cadastrada, ela é o primeiro ponto
        if endereco_origem:
            rota_parts.append(urllib.parse.quote(endereco_origem))
        
        # Adiciona os destinos
        for end in enderecos_destino:
            rota_parts.append(urllib.parse.quote(end))
            
        # Junta tudo com barras "/"
        url_final = f"{base_url}/{'/'.join(rota_parts)}"
        
        # 5. Abre no Navegador
        webbrowser.open(url_final)