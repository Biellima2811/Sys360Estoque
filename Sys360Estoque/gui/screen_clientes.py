# gui/screen_clientes.py
import tkinter as tk
from tkinter import messagebox, ttk
import os
from core import logic_clientes as lg_clientes

# ==========================================================
# --- CLASSE DA TELA DE GERENCIAMENTO DE CLIENTES ---
# ==========================================================
"""
Janela Toplevel para gerenciar clientes.
"""
class TelaGerenciarClientes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Gerenciar Clientes")
        self.geometry("800x550") # Um pouco maior para mais campos
        self.parent = parent

        # --- Ícone ---
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        # --- Widgets ---
        self._criar_widgets()
        
        # --- Popular a tabela ---
        self._popular_tabela_clientes()

        # --- Modal ---
        self.transient(parent)
        self.grab_set()
        self.wait_window()
    
    def _criar_widgets(self):
        frame_main = ttk.Frame(self, padding='10')
        frame_main.pack(expand=True, fill='both')

        # --- 1. Frame de Cadastro (Formulário) ---
        frame_formulario_cad_cliente = ttk.LabelFrame(frame_main, text='Adicionar Novo Cliente')
        frame_formulario_cad_cliente.pack(fill='x', padx=5, pady=5)

        # Labels e Entradas
        ttk.Label(frame_formulario_cad_cliente, text="Nome completo: ").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_nome_completo = ttk.Entry(frame_formulario_cad_cliente, width=40)
        self.entry_nome_completo.grid(row=0, column=1, padx=5, pady=2, sticky='we')

        ttk.Label(frame_formulario_cad_cliente, text="CPF/CNPJ :").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.entry_cpf_cnpj = ttk.Entry(frame_formulario_cad_cliente, width=40)
        self.entry_cpf_cnpj.grid(row=0, column=3, sticky='we', padx=5, pady=2)

        ttk.Label(frame_formulario_cad_cliente, text='Telefone: ').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_telefone = ttk.Entry(frame_formulario_cad_cliente, width=40)
        self.entry_telefone.grid(row=1, column=1, sticky='we', padx=5, pady=2)

        ttk.Label(frame_formulario_cad_cliente, text='E-mail: ').grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.entry_email = ttk.Entry(frame_formulario_cad_cliente, width=40)
        self.entry_email.grid(row=1, column=3, sticky='we', padx=5, pady=2)

        ttk.Label(frame_formulario_cad_cliente, text='Lagradouro :').grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.entry_endereco = ttk.Entry(frame_formulario_cad_cliente, width=50)
        self.entry_endereco.grid(row=2, column=1, padx=5, pady=2, sticky='ew')

        # Botão Salvar
        btn_salvar = ttk.Button(frame_formulario_cad_cliente, text='Salvar Novo Cliente', command=self._on_salvar_cliente_click, style="Accent.TButton")
        btn_salvar.grid(row=3, column=0, columnspan=4, pady=10)
        
        frame_formulario_cad_cliente.grid_columnconfigure(1, weight=1)
        frame_formulario_cad_cliente.grid_columnconfigure(3, weight=3)

        # --- 2. Frame da Tabela de Clientes ---
        frame_tabela = ttk.Labelframe(frame_main, text='Clientes Cadastrados')
        frame_tabela.pack(expand=True, fill='both', padx=5, pady=10)

        colunas = ('id', 'nome', 'telefone', 'email', 'cpf_cnpj')
        self.tabela_clientes = ttk.Treeview(frame_tabela, columns= colunas, show='headings')

        self.tabela_clientes.heading('id', text='ID')
        self.tabela_clientes.heading('nome', text='Nome Completo')
        self.tabela_clientes.heading('telefone', text='Telefone')
        self.tabela_clientes.heading('email', text='Email')
        self.tabela_clientes.heading('cpf_cnpj', text='CPF/CNPJ')

        self.tabela_clientes.column('id', width=40, stretch=False)
        self.tabela_clientes.column('nome', width=250, stretch=True)
        self.tabela_clientes.column('telefone', width=100, stretch=False)
        self.tabela_clientes.column('email', width=150, stretch=True)
        self.tabela_clientes.column('cpf_cnpj', width=120, stretch=False)

        barra_de_rolagem_y = ttk.Scrollbar(frame_tabela, orient='vertical', command=self.tabela_clientes.yview)
        self.tabela_clientes.configure(yscrollcommand=barra_de_rolagem_y.set)

        self.tabela_clientes.pack(side='left', expand=True, fill='both')
        barra_de_rolagem_y.pack(side='right', fill='y')

    def _popular_tabela_clientes(self):
        """Limpa e preenche a tabela com dados do logic.py."""
        for item in self.tabela_clientes.get_children():
            self.tabela_clientes.delete(item)
        
        lista_clientes = lg_clientes.listar_todos_clientes()
        for cliente in lista_clientes:
            self.tabela_clientes.insert('', 'end', values=cliente)
        
    def _on_salvar_cliente_click(self):
        """Pega dados do frame_formulario_cad_cliente, envia para logic.py e atualiza."""
        try:
            # 1. Coletar dados da UI
            nome = self.entry_nome_completo.get()
            telefone = self.entry_telefone.get()
            email = self.entry_email.get()
            cpf_cnpj = self.entry_cpf_cnpj.get()
            endereco = self.entry_endereco.get()

            # 2. Enviar para a lógica (que pode dar erro de validação ou de BD)
            lg_clientes.registrar_novo_cliente(nome, telefone, email, cpf_cnpj, endereco)

            # 3. Se tudo deu certo, sucesso!
            messagebox.showinfo("Sucesso", f"Cliente '{nome}' salvo com sucesso!", parent=self)
            self._limpar_campos_form()
            self._popular_tabela_clientes() # Atualiza a lista
        
        except ValueError as e:
            # 4. Falha (pega o erro do logic.py)
            messagebox.showerror('Erro de validação', str(e), parent=self)

    def _limpar_campos_form(self):
        """Limpa os campos de entrada do formulário."""
        self.entry_nome_completo.delete(0, 'end')
        self.entry_telefone.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_cpf_cnpj.delete(0, 'end')
        self.entry_endereco.delete(0, 'end')
        self.entry_nome_completo.focus_set()