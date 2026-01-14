import tkinter as tk
from tkinter import ttk, messagebox
from core import logic_clientes
import os

class TelaGerenciarClientes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerenciar Clientes")
        self.geometry("900x600")
        
        # Tenta carregar ícone
        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone): self.iconbitmap(caminho_icone)
        except: pass

        self._criar_interface()
        self.carregar_lista()

    def _criar_interface(self):
        # CORREÇÃO LAYOUT: padding reduzido e removido o 'expand=True'
        # Isso impede que o formulário tente ocupar metade da tela verticalmente
        frame_main = ttk.Frame(self, padding='5')
        frame_main.pack(fill='x', anchor='n') 

        # --- 1. Frame de Cadastro (Formulário) ---
        frame_formulario_cad_cliente = ttk.LabelFrame(frame_main, text='Adicionar / Editar Cliente')
        frame_formulario_cad_cliente.pack(fill='x', padx=10, pady=5)
        
        # Linha 1: Nome e CPF
        ttk.Label(frame_formulario_cad_cliente, text="Nome completo: ").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_nome = ttk.Entry(frame_formulario_cad_cliente, width=40)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(frame_formulario_cad_cliente, text="CPF/CNPJ :").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.entry_cpf = ttk.Entry(frame_formulario_cad_cliente, width=20)
        self.entry_cpf.grid(row=0, column=3, sticky='we', padx=5, pady=5)

        # Linha 2: Telefone e Email
        ttk.Label(frame_formulario_cad_cliente, text='Telefone: ').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_tel = ttk.Entry(frame_formulario_cad_cliente, width=20)
        self.entry_tel.grid(row=1, column=1, sticky='we', padx=5, pady=5)

        ttk.Label(frame_formulario_cad_cliente, text='E-mail: ').grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_email = ttk.Entry(frame_formulario_cad_cliente, width=30)
        self.entry_email.grid(row=1, column=3, sticky='we', padx=5, pady=5)

        # Linha 3: Endereço
        ttk.Label(frame_formulario_cad_cliente, text='Logradouro:').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_end = ttk.Entry(frame_formulario_cad_cliente, width=65)
        self.entry_end.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='ew')

        ttk.Label(frame_formulario_cad_cliente, text="(Rua, Número, Bairro, Cidade)", font=("Arial", 8), foreground="gray").grid(row=3, column=1, columnspan=3, sticky='w', padx=5)

        # --- Botões ---
        frame_btns = ttk.Frame(self)
        frame_btns.pack(fill='x', padx=10, pady=5)

        ttk.Button(frame_btns, text="Salvar Novo", command=self.salvar).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="💾 Atualizar Selecionado", command=self.atualizar).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="Limpar Campos", command=self.limpar_campos).pack(side='left', padx=5)
        
        # --- Tabela ---
        # Container da tabela com expand=True para ocupar o resto da tela
        frame_tabela = ttk.Frame(self)
        frame_tabela.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('id', 'nome', 'cpf', 'telefone', 'endereco')
        self.tree = ttk.Treeview(frame_tabela, columns=cols, show='headings')
        
        self.tree.heading('id', text='ID'); self.tree.column('id', width=30, anchor='center')
        self.tree.heading('nome', text='Nome/Razão'); self.tree.column('nome', width=200)
        self.tree.heading('cpf', text='CPF/CNPJ'); self.tree.column('cpf', width=120)
        self.tree.heading('telefone', text='Telefone'); self.tree.column('telefone', width=100)
        self.tree.heading('endereco', text='Endereço'); self.tree.column('endereco', width=250)
        
        # Barra de Rolagem
        scrolly = ttk.Scrollbar(frame_tabela, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrolly.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrolly.pack(side='right', fill='y')
        
        # Evento de Clique na Tabela
        self.tree.bind('<<TreeviewSelect>>', self.ao_selecionar)

    def carregar_lista(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for c in logic_clientes.listar_todos_clientes():
            # Ordem: id, nome, telefone, email, cpf, endereco
            self.tree.insert('', 'end', values=(c[0], c[1], c[4], c[2], c[5]))

    def ao_selecionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        
        self.limpar_campos()
        # Preenche os campos visíveis
        self.entry_nome.insert(0, item[1])
        self.entry_cpf.insert(0, str(item[2]))
        self.entry_tel.insert(0, str(item[3]))
        
        # Busca dados completos (Email e Endereço podem estar ocultos ou incompletos na tabela)
        try:
            cli_completo = logic_clientes.buscar_cliente_por_cpf(str(item[2]))
            if cli_completo:
                # cli_completo = (id, nome, telefone, email, cpf, endereco)
                self.entry_email.delete(0, 'end')
                self.entry_email.insert(0, cli_completo[3] if cli_completo[3] else "")
                
                self.entry_end.delete(0, 'end')
                self.entry_end.insert(0, cli_completo[5] if cli_completo[5] else "")
        except AttributeError:
            messagebox.showerror("Erro", "Função buscar_cliente_por_cpf não encontrada no logic!")

    def salvar(self):
        try:
            logic_clientes.adicionar_cliente(
                self.entry_nome.get(), self.entry_tel.get(), self.entry_email.get(),
                self.entry_cpf.get(), self.entry_end.get()
            )
            messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            self.limpar_campos()
            self.carregar_lista()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def atualizar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um cliente na tabela para atualizar.")
            return
        
        id_cliente = self.tree.item(sel[0])['values'][0]
        
        try:
            logic_clientes.atualizar_cliente(
                id_cliente,
                self.entry_nome.get(), self.entry_tel.get(), self.entry_email.get(),
                self.entry_cpf.get(), self.entry_end.get()
            )
            messagebox.showinfo("Sucesso", "Dados atualizados!")
            self.limpar_campos()
            self.carregar_lista()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def limpar_campos(self):
        self.entry_nome.delete(0, 'end')
        self.entry_cpf.delete(0, 'end')
        self.entry_tel.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_end.delete(0, 'end')