import tkinter as tk
from tkinter import messagebox, ttk
import os
import ssl
import certifi
import tkintermapview
from core import logic_frota
import logging

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

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

        # Aba 3: Mapa
        self.frame_mapa = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_mapa, text="🗺️ Mapa")

        self._montar_aba_veiculos()
        self._montar_aba_calculadora()

    def _montar_aba_veiculos(self):
        # --- Formulário ---
        frame_form = ttk.Label(self.frame_veiculos)
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

        # --- Tabela ---
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

    def _montar_aba_mapa(self):
        # Cria o widget de mapa
        self.mapa = tkintermapview.TkinterMapView(self.frame_mapa, width=800, height=600, corner_radius=0)
        self.mapa.pack(fill="both", expand=True)
        
        # Define local padrão (Ex: Brasil)
        self.mapa.set_position(-14.2350, -51.9253) 
        self.mapa.set_zoom(4)
        
        # Campo para buscar endereço
        frame_busca = ttk.Frame(self.frame_mapa)
        frame_busca.place(relx=0.02, rely=0.02)
        
        self.ent_end = ttk.Entry(frame_busca, width=30)
        self.ent_end.pack(side="left", padx=5)
        ttk.Button(frame_busca, text="Ir", command=self._buscar_endereco).pack(side="left")
    
    def _buscar_endereco(self):
        end = self.ent_end.get()
        if end:
            self.mapa.set_address(end)

    def _salvar_veiculo(self):
        try:
            logic_frota.cadastrar_veiculo(
                self.ent_placa.get(),
                self.ent_modelo.get(),
                "Generico", # Marca (pode adicionar campo depois)
                2024, # Ano (pode adicionar campo depois)
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
            # v = (id, placa, modelo, marca, ano, cap, status)
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