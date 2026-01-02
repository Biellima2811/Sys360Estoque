# gui/app_main.py
import tkinter as tk
from tkinter import messagebox, ttk
import os
# --- Imports da Lógica (Core) ---
# Importa *módulos* específicos
from core import logic_produtos as lg_produtos
from core import logic_usuarios as lg_usuarios
from core import logic_clientes as lg_clientes

# --- Imports da GUI (Telas) ---
# O '.' significa "da mesma pasta"
from .screen_admin import TelaGerenciarUsuarios
from .screen_clientes import TelaGerenciarClientes
from .screen_vendas import TelaVendas
from .screen_financeiro import TelaFinanceiro
# Novo bloco de importação para o tema
try:
    from ttkthemes import ThemedTk
    # Se funcionar, a JanelaPai será ThemedTk
    JanelaPai = ThemedTk
except ImportError:
    # Se falhar, a JanelaPai será a padrão
    JanelaPai = tk.Tk

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
        caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
        if os.path.exists(caminho_icone):
            self.iconbitmap(caminho_icone)

        self.usuario_logado = None
        
        # --- Inicializa o banco de dados ---
        # Garante que a tabela exista antes de qualquer operação
        
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
        menu_arquivo.add_command(label="Fazer Logoff / Trocar Usuário", command=self.realizar_logoff)
        menu_arquivo.add_separator() # Uma linha divisória bonita
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
        # role_usuario = self.usuario_logado[4]

        # Comando para abrir a nova tela de usuários
        menu_cadastros.add_command(
            label="Gerenciar Usuarios",
            command=self.abrir_tela_gerenciar_usuarios
        )
        menu_cadastros.add_command(
            label="Gerenciar Clientes",
            command=self.abrir_tela_gerenciar_clientes
        )
        # Chama a função que define se o usuário pode ou não ver isso
        self._atualizar_permissoes_interface()
        
        # ==========================================================
        # --- 0.2 NOVO MENU: Vendas / Operações ---
        # ==========================================================
        menu_operacoes = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Vendas", menu=menu_operacoes)

        menu_operacoes.add_command(
        label="Nova Venda (PDV)",
        command=self.abrir_tela_vendas
        )
        # ==========================================================
        # --- 0.3 NOVO MENU: Financeiro ---
        # ==========================================================
        menu_financeiro = tk.Menu(self.menu_principal, tearoff = 0)
        self.menu_principal.add_cascade(label='Financeiro', menu=menu_financeiro)
        menu_financeiro.add_command(
            label= "Fluxo de Caixa/ Despesas",
            command=self.abrir_tela_financeiro
        )

        # --- 1. Frame de Dados do Produto (Formulário) ---
        frame_dados = ttk.LabelFrame(self, text="Dados do Produto")
        frame_dados.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        # === LINHA 0: Nome e Categoria ===
        ttk.Label(frame_dados, text="Nome do Produto:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_nome_produto = ttk.Entry(frame_dados, width=30)
        self.entry_nome_produto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_dados, text="Categoria:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_categoria = ttk.Entry(frame_dados, width=20)
        self.entry_categoria.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # === LINHA 1: Quantidade e Fornecedor ===
        ttk.Label(frame_dados, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_qtde = ttk.Entry(frame_dados, width=15)
        self.entry_qtde.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_dados, text="Fornecedor:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.entry_fornecedor = ttk.Entry(frame_dados, width=20)
        self.entry_fornecedor.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # === LINHA 2: Preços (Custo e Venda) ===
        ttk.Label(frame_dados, text="Preço Custo (R$):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_preco_custo = ttk.Entry(frame_dados, width=15)
        self.entry_preco_custo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_dados, text="Preço Venda (R$):").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.entry_preco_venda = ttk.Entry(frame_dados, width=15)
        self.entry_preco_venda.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # Configura a coluna 1 para expandir se a janela for redimensionada
        frame_dados.grid_columnconfigure(1, weight=1)


        # --- 2. Frame de Busca e Botões de Ação ---
        frame_acoes = ttk.Frame(self)
        frame_acoes.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        lbl_buscar = ttk.Label(frame_acoes, text="Buscar por Nome: ")
        lbl_buscar.grid(row=0, column=0, padx=5, pady=5)

        self.entry_buscar_produto = ttk.Entry(frame_acoes, width=40)
        self.entry_buscar_produto.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # --- Botões de Ação ---
        btn_buscar = ttk.Button(frame_acoes, text="Buscar", command=self.buscar_produto)
        btn_buscar.grid(row=0, column=2, padx=5, pady=5)

        btn_adicionar = ttk.Button(frame_acoes, text="Adicionar", command=self.adicionar_produto)
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
        frame_rodape = ttk.Frame(self)
        frame_rodape.grid(row=3, column=0, sticky='ew', padx=10, pady=5)

        self.lbl_assinatura = ttk.Label(self, text="© 2025 Desenvolvido por Gabriel Levi")
        self.lbl_assinatura.grid(row=3, column=0, sticky='w', padx=10, pady=5)

        btn_logoff = ttk.Button(frame_rodape, text="🔒 Logoff", command=self.realizar_logoff, width=10)
        btn_logoff.pack(side='right')
    # ===================================================================
    # FUNÇÕES DE LÓGICA DA INTERFACE (FICAM EM APP.PY)
    # ===================================================================

    def popular_tabela(self, produtos_lista=None):
        """Limpa e preenche a tabela com dados."""
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)

        if produtos_lista is None:
            produtos_lista = lg_produtos.listar_todos_produtos()

        for prod in produtos_lista:
            # prod é (id, nome, qtd, preco_venda, preco_custo, categoria, fornecedor)
            # Vamos mostrar ID, Nome, Qtd, Preço Venda na tabela
            self.tabela_produtos.insert('', 'end', text=prod[0], values=(prod[1], prod[2], f"{prod[3]:.2f}"))
    
    def limpar_campos(self):
        """Limpa os campos de entrada do formulário."""
        self.entry_nome_produto.delete(0, 'end')
        self.entry_qtde.delete(0, 'end')
        self.entry_preco_custo.delete(0, 'end') # Novo
        self.entry_preco_venda.delete(0, 'end')
        self.entry_categoria.delete(0, 'end')   # Novo
        self.entry_fornecedor.delete(0, 'end')  # Novo
        self.entry_buscar_produto.delete(0, 'end')
        self.entry_nome_produto.focus_set()
        
        # Desseleciona item na tabela
        selecionado = self.tabela_produtos.focus()
        if selecionado:
            self.tabela_produtos.selection_remove(selecionado)
    
    def preencher_campos(self, event):
        """Quando um item é clicado, busca os dados completos e preenche os campos."""
        try:
            item_selecionado = self.tabela_produtos.focus()
            
            if not item_selecionado:
                return # Se não for selecionado não retorna nada!
            
            # 1. Pega o ID do produto (que fica escondido na propriedade 'text' da linha)
            id_produto = self.tabela_produtos.item(item_selecionado)['text']
            
            # 2. Busca os dados COMPLETOS no banco de dados
            # (id, nome, qtd, preco_venda, preco_custo, categoria, fornecedor)
            produto = lg_produtos.obter_produto_por_id(id_produto)
            
            if produto:
                self.limpar_campos() # Limpa antes de preencher
                
                # Preenche os campos com os dados do banco
                # O índice [0] é o ID, então começamos do [1]
                self.entry_nome_produto.insert(0, produto[1])
                self.entry_qtde.insert(0, produto[2])
                self.entry_preco_venda.insert(0, f"{produto[3]:.2f}") # Formata com 2 casas
                self.entry_preco_custo.insert(0, f"{produto[4]:.2f}")
                self.entry_categoria.insert(0, produto[5])
                self.entry_fornecedor.insert(0, produto[6])
                
        except Exception as e:
            # Mostra erro se algo falhar (ex: banco desconectado)
            print(f"Erro ao preencher campos: {e}")
    
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
    
    # ==========================================================
    # --- NOVA FUNÇÃO DE CALLBACK (CLIENTES) ---
    # ==========================================================
    def abrir_tela_gerenciar_clientes(self):
        """Abre a janela de gerenciamento de clientes."""
        # Note: Sem verificação de 'admin', qualquer usuário logado pode abrir
        TelaGerenciarClientes(self)
        
    def abrir_tela_vendas(self):
        """Abre a tela de Frente de Caixa."""
        TelaVendas(self)
    
    def _atualizar_permissoes_interface(self):
        """
        Verifica o cargo do usuário logado e habilita/desabilita menus.
        Chamado na inicialização e após o Logoff.
        """
        if not self.usuario_logado:
            return
        
        # self.usuario_logado = (id, nome, login, hash, role)
        role = self.usuario_logado[4]

        # Regra: Apenas admin acessa o menu de usuários
        estado = 'normal' if role == 'admin' else 'disabled'
        
        # Atualiza o menu (índice 0 é "Gerenciar Usuarios")
        try:
            self.menu_cadastros.entryconfig("Gerenciar Usuarios", state=estado)
        except Exception:
            pass # Caso o menu ainda não tenha sido criado
    
    def realizar_logoff(self):
        """Fecha a tela principal (esconde) e abre o Login novamente."""
        if messagebox.askyesno("Logoff", "Deseja realmente trocar de usuario?"):
            # 1. Esconde a janela principal
            self.withdraw()

            # 2. Limpa o usuário atual
            self.usuario_logado = None

            # 3. Importação Local para evitar erro de ciclo (Circular Import)
            from gui.screen_login import TelaLogin

            # 4. Abre o Login
            login_window = TelaLogin(self)

            # 5. Verifica o resultado
            if login_window.usuario_logado:
                # Se logou, atualiza os dados na App
                self.usuario_logado = login_window.usuario_logado
                self.title(f'Sys360 - (Usuario: {self.usuario_logado[1]})')

                # REAPLICA AS PERMISSÕES (Importante!)
                self._atualizar_permissoes_interface()

                # Mostra a janela principal de novo
                self.dieconify()
                # Opcional: Maximizar novamente
                try:
                    self.state('zoomed')
                except:
                    self.attributes('-zoomed', True)
            else:
                # Se fechou a janela de login sem entrar, encerra tudo
                self.quit()

    # ===================================================================
    # FUNÇÕES DE "PONTE" (Ligam a Interface à Lógica)
    # ===================================================================
    
    def adicionar_produto(self):
        """Pega dados da tela e ENVIA para a camada de lógica."""
        try:
            # 1. Pega os dados da interface
            nome = self.entry_nome_produto.get()
            quantidade = self.entry_qtde.get()
            preco_venda = self.entry_preco_venda.get()
            preco_custo = self.entry_preco_custo.get()
            categoria = self.entry_categoria.get()
            fornecedor = self.entry_fornecedor.get()

            # 2. Envia para o 'logic.py' (AGORA COM TODOS OS 6 ARGUMENTOS)
            lg_produtos.adicionar_produto(nome, quantidade, preco_venda, preco_custo, categoria, fornecedor)

            # 3. Se deu certo
            messagebox.showinfo("Sucesso!", f"Produto {nome} adicionado com sucesso!")
            self.limpar_campos()
            self.popular_tabela()
        except ValueError as e:
            messagebox.showerror("ERRO!", f"Ocorreu um erro de validação: {e}")
    
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
            lg_produtos.atualizar_produto(id_produto, nome, quantidade, preco)

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
                lg_produtos.remover_produto(id_produto)

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
            resultados = lg_produtos.buscar_produtos(nome_busca)

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

    def abrir_tela_financeiro(self):
        """Abre a tela de gestão financeira."""
        if self.usuario_logado[4] in ['admin', 'gestor']:
            TelaFinanceiro(self)
        else:
            # Se for funcionário, apenas pode vender
            # Por enquanto bloquear.
            messagebox.showwarning("Acesso Negado!", "Apenas Gerentes/Admins acessam o financeiro.", parent=self)