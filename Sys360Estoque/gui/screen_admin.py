import tkinter as tk
from tkinter import messagebox, ttk
import os
# NOVOS IMPORTS DE LÓGICA:
from core.logic_usuarios import listar_todos_usuarios, registrar_novo_usuario
# ==========================================================
# --- CLASSE DA TELA DE GERENCIAMENTO DE USUÁRIOS (ADMIN) ---
# ==========================================================

class TelaGerenciarUsuarios(tk.Toplevel):
    """
    Janela Toplevel para Admins gerenciarem usuários.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Gerenciar Usuários")
        self.geometry("700x500")

        # --- Ícone ---
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        # --- Widgets ---
        self._criar_widgets()
        
        # --- Popular a tabela ---
        self._popular_tabela_usuarios()

        # --- Modal ---
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _criar_widgets(self):
        # --- Frame Principal ---
        frame_main = ttk.Frame(self, padding="10")
        frame_main.pack(fill='both', expand=True)

        # --- 1. Frame de Cadastro (Formulário) ---
        frame_from_Cadastro_Usuario = ttk.LabelFrame(frame_main, text='Adicionar Novo Usuario')
        frame_from_Cadastro_Usuario.pack(fill='x', padx=5, pady=5)
    
        # Labels e Entradas
        ttk.Label(frame_from_Cadastro_Usuario, text='Nome Completo: ').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.entry_nome_completo = ttk.Entry(frame_from_Cadastro_Usuario, width=40)
        self.entry_nome_completo.grid(row=0, column=1, padx=5, pady=2, sticky='we')

        ttk.Label(frame_from_Cadastro_Usuario, text='Login: ').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.entry_login = ttk.Entry(frame_from_Cadastro_Usuario, width=40)
        self.entry_login.grid(row=1, column=1, sticky='we', padx=5, pady=2)

        ttk.Label(frame_from_Cadastro_Usuario, text="Senha (min 4 chars): ").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.entry_senha = ttk.Entry(frame_from_Cadastro_Usuario, width=40, show='*')
        self.entry_senha.grid(row=2, column=1, sticky='we', padx=5, pady=2)

        ttk.Label(frame_from_Cadastro_Usuario, text='Função: ').grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.combo_role = ttk.Combobox(frame_from_Cadastro_Usuario, values=['funcionario', 'admin'], state="readonly") 
        self.combo_role.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        self.combo_role.set('funcionario') # Default


            # Botão Salvar
        btn_salvar = ttk.Button(frame_from_Cadastro_Usuario, 
                                text='Salvar Novo usuario', 
                                command=self._on_salvar_usuario_click, 
                                style="Accent.TButton")
        btn_salvar.grid(row=4, column=0, columnspan=4, pady=10)

        frame_from_Cadastro_Usuario.grid_columnconfigure(1, weight=1)
        frame_from_Cadastro_Usuario.grid_columnconfigure(3, weight=1)

        # --- 2. Frame da Tabela de Usuários ---
        frame_tabela = ttk.LabelFrame(frame_main, text='Usuarios Cadastros')
        frame_tabela.pack(expand=True, fill='both', padx=5, pady=10)

        colunas = ('id', 'nome', 'login', 'role')
        self.tabela_usuarios = ttk.Treeview(frame_tabela, columns=colunas, show='headings')

        # Configurações das tabelas do gerenciamos de usuarios
        self.tabela_usuarios.heading('id', text='ID')
        self.tabela_usuarios.heading('nome', text='Nome Completo')
        self.tabela_usuarios.heading('login', text='Login')
        self.tabela_usuarios.heading('role', text='Função')
        
        self.tabela_usuarios.column('id', width=40, stretch=False)
        self.tabela_usuarios.column('nome', width=250, stretch=False)
        self.tabela_usuarios.column('login', width=150, stretch=False)
        self.tabela_usuarios.column('role', width=100, stretch=False)
        # Scrollbar
        barra_de_rolagem_y = ttk.Scrollbar(frame_tabela, orient='vertical', command=self.tabela_usuarios.yview)
        self.tabela_usuarios.configure(yscrollcommand=barra_de_rolagem_y.set)
        self.tabela_usuarios.pack(side='left', expand=True, fill='both')
        barra_de_rolagem_y.pack(side='right', fill='y')
        
    def _popular_tabela_usuarios(self):
        """Limpa e preenche a tabela com dados do logic.py."""
        for item in self.tabela_usuarios.get_children():
            self.tabela_usuarios.delete(item)
        
        lista_usuarios = listar_todos_usuarios()
        for usuario in lista_usuarios:
            # Insere a tupla (id, nome, login, role)
            self.tabela_usuarios.insert('', 'end', values=usuario)

    def _on_salvar_usuario_click(self):
        """Pega dados do form, envia para logic.py e atualiza."""
        try:
            # 1. Coletar dados da UI
            nome = self.entry_nome_completo.get()
            login = self.entry_login.get()
            senha = self.entry_senha.get()
            role = self.combo_role.get()

            # 2. Enviar para a lógica (que pode dar erro)
            registrar_novo_usuario(nome, login, senha, role)

            # 3. Sucesso, caso todas as informações bata com a base de dados 
            messagebox.showinfo("Sucesso", f"Usuario '{login}' foi criado com sucesso!")
            self._limpar_campos_form()
            self._popular_tabela_usuarios() # Atualiza a lista de usuarios
        
        except ValueError as e:
            # 4. Falha (pega o erro do logic.py)
            messagebox.showerror("Erro de Validação", str(e), parent=self)
    
    def _limpar_campos_form(self):
        """Limpa os campos de entrada do formulário."""
        self.entry_nome_completo.delete(0, 'end')
        self.entry_login.delete(0, 'end')
        self.entry_senha.delete(0, 'end')
        self.combo_role.set('funcionario')