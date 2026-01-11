# gui/screen_frota.py
import tkinter as tk
from tkinter import messagebox, ttk
import os
import webbrowser # <--- Biblioteca nativa para abrir navegador
from core import logic_frota

class TelaFrota(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Gestão de Frota")
        self.geometry("900x700")

        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)
        
        self._criar_tabs()
        self._popular_tabela()

        self.transient(parent)

    def _criar_tabs(self):
        # Cria o sistema de Abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Aba 1: Veículos
        self.frame_veiculos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_veiculos, text="🚚 Gerenciar Veículos")

        # Aba 2: Calculadora de Frete
        self.frame_calc = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_calc, text="🧮 Calculadora de Frete")

        # Aba 3: Rastreamento (Google Maps)
        self.frame_mapa = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_mapa, text="🗺️ Rastreamento / Rotas")

        self._montar_aba_veiculos()
        self._montar_aba_calculadora()
        self._montar_aba_mapa_navegador() # <--- Nova função

    # ... (Os métodos _montar_aba_veiculos, _salvar_veiculo, _popular_tabela mantêm-se IGUAIS) ...
    # Vou reescrever para garantir que você tenha o arquivo completo sem erros de indentação

    def _montar_aba_veiculos(self):
        frame_form = ttk.LabelFrame(self.frame_veiculos, text="Cadastro")
        frame_form.pack(fill='x', padx=15, pady=15)

        ttk.Label(frame_form, text='Placa:').grid(row=0, column=0, padx=5)
        self.ent_placa = ttk.Entry(frame_form, width=15)
        self.ent_placa.grid(row=0, column=1, padx=5)

        ttk.Label(frame_form, text='Modelo:').grid(row=0, column=2, padx=5)
        self.ent_modelo = ttk.Entry(frame_form, width=20)
        self.ent_modelo.grid(row=0, column=3, padx=5)

        ttk.Label(frame_form, text="Capacidade (Kg):").grid(row=0, column=4, padx=5)
        self.ent_cap = ttk.Entry(frame_form, width=10)
        self.ent_cap.grid(row=0,column=5, padx=5)

        btn_add = ttk.Button(frame_form, text="Salvar Veículo", command=self._salvar_veiculo, style="Accent.TButton")
        btn_add.grid(row=0, column=6, padx=10)

        cols = ('id', 'placa', 'modelo', 'status')
        self.tree_veiculos = ttk.Treeview(self.frame_veiculos, columns=cols, show='headings')
        self.tree_veiculos.heading('id', text='ID')
        self.tree_veiculos.heading('placa', text='Placa')
        self.tree_veiculos.heading('modelo', text='Modelo')
        self.tree_veiculos.heading('status', text='Status')

        self.tree_veiculos.column('id', width=50)
        self.tree_veiculos.column('placa', width=100)
        self.tree_veiculos.column('modelo', width=150)
        self.tree_veiculos.column('status', width=100)

        self.tree_veiculos.pack(fill='both', expand=True, padx=10, pady=10)

    def _montar_aba_calculadora(self):
        frame_calc = ttk.LabelFrame(self.frame_calc, text='Simulação de Frete')
        frame_calc.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(frame_calc, text="Distancia (KM):", font=('Arial',12)).pack(pady=5)
        self.ent_dist = ttk.Entry(frame_calc, font=('Arial', 12))
        self.ent_dist.pack(pady=5)

        ttk.Label(frame_calc, text="Peso da Carga (Kg):", font=('Arial', 12)).pack(pady=5)
        self.ent_peso = ttk.Entry(frame_calc, font=('Arial', 12))
        self.ent_peso.pack(pady=5)

        ttk.Button(frame_calc, text='Calcular Custo', command=self._calcular).pack(pady=15, ipadx=10, ipady=5)
        
        self.lbl_resultado = ttk.Label(frame_calc, text="R$ 0.00", font=('Arial', 24, 'bold'), foreground='green')
        self.lbl_resultado.pack(pady=10)

        ttk.Label(frame_calc, text="*Cálculo base: (Distância x2 / 10km/L * R$6.00) + Taxas", font=('Arial', 8)).pack(side='bottom', pady=10)

    # --- AQUI ESTÁ A CORREÇÃO DO MAPA ---
    def _montar_aba_mapa_navegador(self):
        """Cria uma interface limpa que abre o Google Maps no navegador."""
        frame_conteudo = ttk.Frame(self.frame_mapa, padding=40)
        frame_conteudo.pack(fill='both', expand=True)

        # Ícone ou Título Grande
        ttk.Label(frame_conteudo, text="🌍 Rastreamento e Rotas", font=("Helvetica", 20, "bold")).pack(pady=(0, 20))

        # Explicação
        msg = ("Para garantir a melhor precisão de GPS e dados de trânsito em tempo real,\n"
               "o Sys360 utiliza a integração direta com o Google Maps.")
        ttk.Label(frame_conteudo, text=msg, font=("Arial", 11), justify="center").pack(pady=10)

        # Entrada de Endereço
        ttk.Label(frame_conteudo, text="Digite o endereço, CEP ou Coordenadas:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        
        self.ent_endereco_mapa = ttk.Entry(frame_conteudo, width=50, font=("Arial", 12))
        self.ent_endereco_mapa.pack(pady=5, ipady=3)
        self.ent_endereco_mapa.insert(0, "São Paulo, SP") # Exemplo padrão

        # Botão Ação
        btn_abrir = ttk.Button(frame_conteudo, text="Abrir no Google Maps ↗", command=self._abrir_google_maps, style="Accent.TButton")
        btn_abrir.pack(pady=20, ipadx=10, ipady=5)

    def _abrir_google_maps(self):
        endereco = self.ent_endereco_mapa.get()
        if not endereco:
            messagebox.showwarning("Aviso", "Digite um endereço para buscar.")
            return
        
        # Codifica o endereço para URL e abre
        # Ex: https://www.google.com/maps/search/Av+Paulista
        base_url = "https://www.google.com/maps/search/?api=1&query="
        webbrowser.open(base_url + endereco)

    def _salvar_veiculo(self):
        try:
            logic_frota.cadastrar_veiculo(
                self.ent_placa.get(),
                self.ent_modelo.get(),
                "Generico", 
                2024, 
                self.ent_cap.get()
            )
            messagebox.showinfo("Sucesso", "Veículo salvo")
            self._popular_tabela()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
    
    def _popular_tabela(self):
        for i in self.tree_veiculos.get_children():
            self.tree_veiculos.delete(i)
        
        veiculos = logic_frota.listar_veiculos()
        for v in veiculos:
            self.tree_veiculos.insert('', 'end', values=(v[0], v[1], v[2], v[6]))
    
    def _calcular(self):
        try:
            total = logic_frota.calcular_frete_estimado(
                self.ent_dist.get(),
                self.ent_peso.get()
            )
            self.lbl_resultado.config(text=f'R$ {total:.2f}')
        except ValueError:
            messagebox.showerror("Erro", 'Digite números validos')