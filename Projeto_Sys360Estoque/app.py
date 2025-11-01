import tkinter as tk
from ttkthemes import ThemedStyle
from tkinter import messagebox, ttk
import database as db
import logic as lg
import os

# Novo bloco de importação para o tema
try:
    from ttkthemes import ThemedTk
    # Se funcionar, a JanelaPai será ThemedTk
    JanelaPai = ThemedTk
except ImportError:
    # Se falhar, a JanelaPai será a padrão
    JanelaPai = tk.Tk

# ==========================================================
# --- CLASSE DA TELA DE LOGIN ---
# ==========================================================
class TelaLogin(tk.Toplevel):
    """
    Esta é uma janela 'Toplevel', o que significa que é uma
    janela pop-up que aparece sobre a janela principal.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sys360 - Login")
        self.geometry("350x200")
        self.resizable(False, False)

        # --- Define o Ícone ---
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)
        self.parent = parent # Guarda a referência da janela principal

        # --- Atributo para guardar o resultado ---
        self.usuario_logado = None

        # --- Widgets da Tela de Login ---
        self.frame = ttk.Frame(self, padding="20 20 20 20")
        self.frame.pack(expand=True, fill='both')

        lbl_login = ttk.Label(self.frame, text="Usuario: ")
        lbl_login.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.entry_login = ttk.Entry(self.frame, width=30)
        self.entry_login.grid(row=0, column=1, padx=5, pady=5)

        lbl_senha = ttk.Label(self.frame, text="Senha: ")
        lbl_senha.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.entry_senha = ttk.Entry(self.frame, width=30, show='*')
        self.entry_senha.grid(row=1, column=1, padx=5, pady=5)

        btn_login = ttk.Button(self.frame, text="Entrar", command=self._on_login_click, style="Accent.TButton")
        btn_login.grid(row=2, column=0, columnspan=2, pady=20)

        # Foco inicial
        self.entry_login.focus_set()

        # --- Modal ---
        # Esses comandos tornam a janela "modal", ou seja,
        # o usuário NÃO consegue clicar na janela principal
        # enquanto esta não for fechada.
        self.transient(parent) # Mantém a janela no topo
        self.grab_set() # Bloqueia eventos para outras janelas

        # Bloqueia eventos para outras janelas
        self.wait_window()
    
    def _on_login_click(self):
        """Chamado quando o botão 'Entrar' é clicado."""
        login = self.entry_login.get()
        senha = self.entry_senha.get()

        try:
            # 1. TENTA verificar o login (chama o logic.py)
            # Isso pode disparar um 'ValueError'
            usuario_db = lg.verificar_login(login, senha)

            # 2. SUCESSO!
            self.usuario_logado = usuario_db # Guarda os dados do usuário
            messagebox.showinfo("Autenticação Validada!", f"Bem-Vindo, {self.usuario_logado[1]}")
            self.destroy() # Fecha a janela de login
        except ValueError as e:
            # 3. FALHA! (O alarme 'ValueError' tocou)
            messagebox.showerror("Aviso!", f'Erro de login: {e}')
            self.entry_senha.delete(0, 'end')# Limpa a senha
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
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "Estoque360.ico"))
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
        
        lista_usuarios = lg.listar_todos_usuarios()
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
            lg.registrar_novo_usuario(nome, login, senha, role)

            # 3. Sucesso, caso todas as informações bata com a base de dados 
            messagebox.showinfo("Sucesso", f"Usuario '{login}' foi criado com sucesso!")
            self._limpar_campos_from()
            self._popular_tabela_usuarios() # Atualiza a lista de usuarios
        
        except ValueError as e:
            # 4. Falha (pega o erro do logic.py)
            messagebox.showerror("Erro de Validação", str(e), parent=self)
    
    def _limpar_campos_from(self):
        """Limpa os campos de entrada do formulário."""
        self.entry_nome_completo.delete(0, 'end')
        self.entry_login.delete(0, 'end')
        self.entry_senha.delete(0, 'end')
        self.combo_role.set('funcionario')    

class App(JanelaPai):
    def __init__(self):
        super().__init__()

        # --- Aplica o tema (se disponível) ---
        if JanelaPai == ThemedTk:
            # --- Configuração da Janela Principal ---
            self.set_theme("clearlooks")
        
        self.title("Sys360 - Controle de Estoque")
        self.geometry("850x550")
        self.resizable(True, True)

        # --- Define o Ícone ---
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        self.usuario_logado = None
        
        # --- Inicializa o banco de dados ---
        # Garante que a tabela exista antes de qualquer operação
        db.inicializar_db()

        # --- Chamada da função que cria os widgets ---
        #self.criar_widgets()

        # --- Chamada da função que popula a tabela ---
        #self.popular_tabela()
    
    def criar_widgets(self):
        """Cria e organiza todos os widgets da interface usando .grid()"""
        # ==========================================================
        # --- 0. BARRA DE MENU PRINCIPAL ---
        # ==========================================================
        self.menu_principal= tk.Menu(self)
        self.config(menu=self.menu_principal)# Informa a janela que este é o menu

        # --- Menu "Arquivo" ---
        menu_arquivo = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Sair", command=self.quit) # self.quit fecha a app
        
        # --- Menu "Ajuda" ---
        menu_ajuda = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Ajuda", menu=menu_ajuda)
        # 'command' chama uma nova função
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)


        # ==========================================================
        # --- 0.1 NOVO MENU: Cadastros (COM VERIFICAÇÃO DE ROLE) ---
        # ==========================================================
        menu_cadastros = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Cadastro", menu=menu_cadastros)

        # self.usuario_logado foi definido na inicialização
        # A tupla do usuário é: (id, nome, login, hash, role)
        # O 'role' está no índice 4
        role_usuario = self.usuario_logado[4]

        # Comando para abrir a nova tela de usuários
        menu_cadastros.add_command(
            label="Gerenciar Usuarios",
            command=self.abrir_tela_gerenciar_usuarios
        )

        # --- A MÁGICA DA PERMISSÃO ---
        if role_usuario != 'admin':
            # Se não for admin, DESABILITA o menu
            menu_cadastros.entryconfig("Gerenciar Usuarios", state='disabled')

        # --- 1. Frame de Dados do Produto (Formulário) ---
        frame_dados = ttk.LabelFrame(self, text="Dados do Produto")
        # .grid() - Coloca o frame na linha 0, coluna 0
        # 'sticky="ew"' faz ele se esticar horizontalmente
        # 'padx' e 'pady' dão um espaçamento externo
        frame_dados.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        # Labels e Entradas (Campos do formulário)
        lbl_nome = ttk.Label(frame_dados, text="Nome do Produto:")
        lbl_nome.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # 'self.entry_nome' - Armazenamos como atributo da classe
        # para poder acessá-lo em outras funções (como 'adicionar_produto')
        self.entry_nome_produto = ttk.Entry(frame_dados, width=50)
        self.entry_nome_produto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        lbl_qtde = ttk.Label(frame_dados, text="Quantidade:")
        lbl_qtde.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.entry_qtde = ttk.Entry(frame_dados, width=15)
        self.entry_qtde.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        lbl_preco = ttk.Label(frame_dados, text="Preço (R$):")
        lbl_preco.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        self.entry_preco = ttk.Entry(frame_dados, width=15)
        self.entry_preco.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # Faz a coluna 1 (onde estão os campos de entrada) se expandir
        frame_dados.grid_columnconfigure(1, weight=1)


        # --- 2. Frame de Busca e Botões de Ação ---
        frame_acoes = ttk.Frame(self)
        frame_acoes.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        lbl_buscar = ttk.Label(frame_acoes, text="Buscar por Nome: ")
        lbl_buscar.grid(row=0, column=0, padx=5, pady=5)

        self.entry_buscar_produto = ttk.Entry(frame_acoes, width=30)
        self.entry_buscar_produto.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # --- Botões de Ação ---
        btn_buscar = ttk.Button(frame_acoes, text="Buscar", command=self.buscar_produto)
        btn_buscar.grid(row=0, column=2, padx=5, pady=5)

        btn_adicionar = ttk.Button(frame_acoes, text="Adicionar", command=self.adicionar_produto, style="Accent.TButton")
        btn_adicionar.grid(row=0, column=3, padx=5, pady=5)

        btn_atualizar = ttk.Button(frame_acoes, text="Atualizar Selecionado", command=self.atualizar_produto)
        btn_atualizar.grid(row=0, column=4, padx=5, pady=5)

        btn_remover = ttk.Button(frame_acoes, text="Remover Selecionado", command=self.remover_produto)
        btn_remover.grid(row=0, column=5, padx=5, pady=5)

        # Configura a coluna 1 para "empurrar" os botões para a direita
        frame_acoes.grid_columnconfigure(1, weight=1)

        # --- 3. Frame da Tabela (TreeView) ---
        frame_tabela = ttk.Frame(self)
        frame_tabela.grid(row=2, column=0, sticky='nsew', padx=20, pady=20)

        # Configura a linha 2 e a coluna 0 da JANELA PRINCIPAL
        # para se expandirem (weight=1), fazendo a tabela crescer.
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # definição de colunas 
        colunas = ("nome", "quantidade", "preco")
        self.tabela_produtos = ttk.Treeview(frame_tabela, columns=colunas, show='headings')

        # Cabeçalhos
        self.tabela_produtos.heading("nome", text="Nome do Produto")
        self.tabela_produtos.heading('quantidade', text="Quantidade")
        self.tabela_produtos.heading('preco', text='Preço (R$)', anchor='center') # Alinhamento

        # Configuração das colunas
        self.tabela_produtos.column('nome', width=300, stretch=True) # stretch = alongar
        self.tabela_produtos.column('quantidade', width=100, stretch=False)
        self.tabela_produtos.column('preco', width=100, stretch=False, anchor='center') # anchor = âncora 

        # Adicionando Scrollbars (Barras de Rolagem)
        barra_de_rolagem_y = ttk.Scrollbar(frame_tabela, orient='vertical', command=self.tabela_produtos.yview)
        barra_de_rolagem_x = ttk.Scrollbar(frame_tabela, orient='horizontal', command=self.tabela_produtos.xview)
        self.tabela_produtos.configure(yscrollcommand=barra_de_rolagem_y.set, xscrollcommand=barra_de_rolagem_x.set)

        # Posicionando a tabela e as scrollbars com .grid()
        self.tabela_produtos.grid(row=0, column=0, sticky='nsew')
        barra_de_rolagem_y.grid(row=0, column=1, sticky='ns')
        barra_de_rolagem_x.grid(row=1, column=0, sticky='ew')

        # Configurando a expansão da tabela dentro do seu frame
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)

        # --- Evento de Clique ---
        # Adiciona um evento para quando o usuário clicar em um item da tabela
        self.tabela_produtos.bind('<<TreeviewSelect>>', self.preencher_campos)

        # --- 4. Rodapé ---
        self.lbl_assinatura = ttk.Label(self, text="© 2025 Desenvolvido por Gabriel Levi")
        self.lbl_assinatura.grid(row=3, column=0, sticky='w', padx=10, pady=5)

    # ===================================================================
    # FUNÇÕES DE LÓGICA DA INTERFACE (FICAM EM APP.PY)
    # ===================================================================

    def popular_tabela(self, produtos_lista=None):
        """Limpa e preenche a tabela com dados."""
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)

        if produtos_lista is None:
            produtos_lista = lg.listar_todos_produtos()

        for produto in produtos_lista:
            self.tabela_produtos.insert('', 'end', text=produto[0], values=(produto[1], produto[2], f"{produto[3]:.2f}"))
    
    def limpar_campos(self):
        """Limpa os campos de entrada do formulário."""
        self.entry_nome_produto.delete(0, 'end')
        self.entry_qtde.delete(0, 'end')
        self.entry_preco.delete(0, 'end')
        self.entry_buscar_produto.delete(0, 'end')
        self.entry_nome_produto.focus_set()

        # Desseleciona item na tabela
        selecionado = self.tabela_produtos.focus()
        if selecionado:
            self.tabela_produtos.selection_remove(selecionado)
    
    def preencher_campos(self, event):
        """Quando um item é clicado, preenche os campos."""
        item_selecionado = self.tabela_produtos.focus()
        
        if not item_selecionado:
            return # Se não for selecionado não retorna nada!
        
        dados_item = self.tabela_produtos.item(item_selecionado)
        valores = dados_item['values']

        self.limpar_campos() # Limpa primeiro, para garantir o cadastro com informações do produto
        self.entry_nome_produto.insert(0, valores[0])
        self.entry_qtde.insert(0, valores[1])
        self.entry_preco.insert(0, valores[2])
    
    def mostrar_sobre(self):
        """Exibe uma janela 'Sobre' com informações."""
        messagebox.showinfo(
            "Sobre o Sys360",
            "Sys360 - Controle de Estoque\n"
            "Versão 1.0 (ERP Core)\n\n"
            "Desenvolvido por Gabriel Levi.")
        
    def abrir_tela_gerenciar_usuarios(self):
        """Abre a janela de gerenciamento de usuários."""
        # A verificação de permissão já foi feita no menu,
        # mas podemos (opcionalmente) verificar de novo por segurança.
        if self.usuario_logado[4] == 'admin':
            TelaGerenciarUsuarios(self)
        else:
            messagebox.showwarning("Acesso Negado", "Você não tem permissão para acessar esta área.", parent=self)
    # ===================================================================
    # FUNÇÕES DE "PONTE" (Ligam a Interface à Lógica)
    # ===================================================================
    
    def adicionar_produto(self):
        """Pega dados da tela e ENVIA para a camada de lógica."""
        try:
            # 1. Pega os dados da interface
            nome = self.entry_nome_produto.get()
            quantidade = self.entry_qtde.get()
            preco = self.entry_preco.get()

            # 2. Envia para o 'logic.py' fazer o trabalho pesado
            lg.adicionar_produto(nome, quantidade, preco)

            # 3. Se deu certo, atualiza a interface
            messagebox.showinfo("Sucesso!", f"Produto {nome} adicionado com sucesso!")
            self.limpar_campos()
            self.popular_tabela()
        except ValueError as e:
            # 4. Se o 'logic.py' deu erro (ValueError), mostra na tela
            messagebox.showerror("ERRO!", f"Ocorreu um erro de validação do porduto: {e}")
    
    def atualizar_produto(self):
        """Pega dados da tela e ENVIA para a camada de lógica atualizar."""
        
        # 1. Pega o ID (única coisa que a UI precisa saber)
        item_selecionado = self.tabela_produtos.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", f"Selecione um produto para atualizar.")
            return
        
        id_produto = self.tabela_produtos.item(item_selecionado)['text']

        try:
            # 2. Pega os dados dos campos
            nome = self.entry_nome_produto.get()
            quantidade = self.entry_qtde.get()
            preco = self.entry_preco.get()

            # 3. Envia para o 'logic.py'
            lg.atualizar_produto(id_produto, nome, quantidade, preco)

            # 4. Se deu certo, atualiza a interface
            messagebox.showinfo("Sucesso!", 'Produto atualizado com sucesso!')
            self.limpar_campos()
            self.popular_tabela()
        
        except ValueError as e:
            messagebox.showerror("ERRO", f"Ocorreu um erro de validação do produto: {e}")

    def remover_produto(self):
        """Pega o ID da tela e ENVIA para a camada de lógica remover."""

        item_selecionado = self.tabela_produtos.focus()
        if not item_selecionado:
            messagebox.showwarning("Aviso", f"Selecione um produto para atualizar.")
            return
        
        if messagebox.askyesno('Confirmação', 'Tem certeza que deseja remover este produto ?'):
            try:
                id_produto = self.tabela_produtos.item(item_selecionado)['text']

                # 2. Envia para o 'logic.py'
                lg.remover_produto(id_produto)

                # 3. Se deu certo, atualiza a interface
                messagebox.showinfo('Sucesso!', 'Produto foi removido com sucesso!')
                self.limpar_campos()
                self.popular_tabela()
            except ValueError as e:
                messagebox.showerror('Erro!', f'Ocorre um erro ao executa a exclusão do produto: {e}')
            
            finally:
                print('Operação executada!')
    
    def buscar_produto(self):
        """Pega o texto da busca e ENVIA para a camada de lógica."""
        try:
            nome_busca = self.entry_buscar_produto.get()

            # 1. Envia para o 'logic.py' (ele sabe o que fazer se estiver vazio)
            resultados = lg.buscar_produtos(nome_busca)

            # 2. Atualiza a interface com os resultados
            self.popular_tabela(produtos_lista=resultados)

            # 3. Se a busca foi por nome, limpa os campos principais
            if nome_busca:
                self.limpar_campos()
        except ValueError as e:
            # 'logic.py' nos avisa se não encontrar nada
            messagebox.showerror("Erro!", f'Ocorreu um erro ao buscar o produto, verifique o nome ou se realmente está cadastrado. {e}')
            self.popular_tabela()
        finally:
            print('Operação de busca na base foi realizada!')

# ===================================================================
# INICIALIZAÇÃO DA APLICAÇÃO (FICA EM APP.PY)
# ===================================================================
if __name__ == "__main__":
    
    # --- 0. Inicializa o DB e cria o admin ---
    # Isso garante que o DB e o usuário 'admin' existam
    # antes de qualquer janela ser criada.
    db.inicializar_db()
    lg.criar_primeiro_admin() # Chama a nova função do logic.py

    # --- 1. Cria a App principal, mas a esconde ---
    app = App()
    app.withdraw() # 'withdraw' esconde a janela principal

    # --- 2. Aplica o estilo (necessário para a TelaLogin) ---
    estilo = ttk.Style(app)
    estilo.configure("Accent.TButton", background="#007bff", font=('Helvetica', 9, 'bold'))

    # --- 3. Mostra a Tela de Login ---
    # O código vai "pausar" aqui até a TelaLogin ser fechada
    login_window = TelaLogin(app)
    
    # --- 4. Verifica se o login foi bem-sucedido ---
    if login_window.usuario_logado:
        # SUCESSO!
        app.usuario_logado = login_window.usuario_logado # Passa os dados do usuário para a app
        app.title(f"Sys360 - (Usuário: {app.usuario_logado[2]})") # Atualiza o título
        app.criar_widgets()
        app.criar_widgets()
        app.deiconify() # 'deiconify' RE-EXIBE a janela principal
        app.mainloop()
    else:
        # FALHA!
        # Se o login_window.usuario_logado for None, o usuário
        # fechou a janela de login sem logar. O programa termina.
        print("Login cancelado. Encerrando aplicação.")
        app.destroy()