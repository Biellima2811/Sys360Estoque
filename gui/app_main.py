# gui/app_main.py
# Arquivo principal da aplicação gráfica (GUI) usando Tkinter

import tkinter as tk                  # Importa o módulo base do Tkinter
from tkinter import messagebox, ttk   # Importa caixas de diálogo e widgets temáticos
import os                             # Importa funções para manipulação de caminhos e arquivos

# --- Imports da Lógica (Core) ---
from core import logic_produtos as lg_produtos   # Lógica de negócio relacionada a produtos
from core import logic_usuarios as lg_usuarios   # Lógica de negócio relacionada a usuários
from core import logic_clientes as lg_clientes   # Lógica de negócio relacionada a clientes

# --- Imports da GUI (Telas) ---
from .screen_admin import TelaGerenciarUsuarios      # Tela de gerenciamento de usuários
from .screen_clientes import TelaGerenciarClientes   # Tela de gerenciamento de clientes
from .screen_vendas import TelaVendas                # Tela de vendas (PDV)
from .screen_financeiro import TelaFinanceiro        # Tela do módulo financeiro
from .screen_dashboard import Dashboard              # Tela inicial (dashboard)
from .screen_frota import ScreenFrota
from .screen_historico import TelaHistoricoVendas
from .screen_analytics import TelaAnalytics
from .screen_config import TelaConfiguracao

try:
    from ttkthemes import ThemedTk    # Tenta importar suporte a temas visuais
    JanelaPai = ThemedTk              # Define a janela principal com suporte a temas
except ImportError:
    JanelaPai = tk.Tk                # Caso falhe, usa Tk padrão como janela principal

class App(JanelaPai):
    def __init__(self):
        super().__init__()            # Inicializa a classe pai (Tk ou ThemedTk)

        # --- Aplica o tema (se disponível) ---
        if JanelaPai == ThemedTk:     # Verifica se o suporte a temas está disponível
            self.set_theme("clearlooks")  # Define o tema visual
        
        self.title("Sys360 - Controle de Estoque")  # Define o título da janela
        self.geometry("850x550")                   # Define o tamanho inicial da janela
        self.resizable(True, True)                 # Permite redimensionamento

        # --- Define o Ícone ---
        caminho_icone = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico")
        )                                          # Monta o caminho absoluto do ícone
        if os.path.exists(caminho_icone):          # Verifica se o ícone existe
            self.iconbitmap(caminho_icone)         # Define o ícone da aplicação

        self.usuario_logado = None                 # Armazena o usuário autenticado
        
        # Container Principal
        self.container_principal = ttk.Frame(self) # Frame principal que recebe as telas
        self.container_principal.pack(fill="both", expand=True)  # Expande em toda a janela

        self.frames = {}                           # Dicionário para possíveis telas

        # Inicializa o menu
        self.criar_menus() 

        # O dashboard será carregado pelo main.py após o login
    
    
    def criar_menus(self):
        """Cria a barra de menus superior."""
        self.menu_principal = tk.Menu(self)        # Cria a barra de menus
        self.config(menu=self.menu_principal)      # Associa o menu à janela

        # --- Menu Arquivo ---
        menu_arquivo = tk.Menu(self.menu_principal, tearoff=0)  # Menu Arquivo
        self.menu_principal.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Início / Dashboard", command=self.mostrar_dashboard)
        menu_arquivo.add_separator()                # Linha separadora
        menu_arquivo.add_command(label="Fazer Logoff", command=self.realizar_logoff)
        menu_arquivo.add_command(label="Sair", command=self.quit)

        # Menu Administração (Novo)
        menu_admin = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Administração", menu=menu_admin)
        menu_admin.add_command(label="Configurar Rede/Banco", command=self.abrir_tela_config)
        
        # --- Menu Cadastros ---
        self.menu_cadastros = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Cadastro", menu=self.menu_cadastros)
        self.menu_cadastros.add_command(
            label="Gerenciar Usuarios", command=self.abrir_tela_gerenciar_usuarios
        )
        self.menu_cadastros.add_command(
            label="Gerenciar Clientes", command=self.abrir_tela_gerenciar_clientes
        )
        
        # --- Menu Vendas ---
        menu_operacoes = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Vendas", menu=menu_operacoes)
        
        menu_operacoes.add_command(
            label="Nova Venda (PDV)", command=self.abrir_tela_vendas
        )
        menu_operacoes.add_separator()
        menu_operacoes.add_command(label="Histórico de Vendas", command=self.abrir_tela_historico)


        # --- Menu Financeiro ---
        menu_financeiro = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label='Financeiro', menu=menu_financeiro)
        menu_financeiro.add_command(
            label="Fluxo de Caixa", command=self.abrir_tela_financeiro
        )
        # --- Menu Gestão / Analytics ---
        menu_gestao = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label='Gestão', menu=menu_gestao)
        menu_gestao.add_command(label='Dashboard & Gráficos',command=self.abrir_tela_analytics)
        
        # --- Menu Frota ---
        menu_frota = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label='Frota', menu=menu_frota)
        menu_frota.add_command(label='Veículos e Frete', command=self.abrir_tela_frota)
        
        # --- Menu Ajuda ---
        menu_ajuda = tk.Menu(self.menu_principal, tearoff=0)
        self.menu_principal.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)


    def criar_tela_estoque(self):
        self._limpar_container()      # Remove widgets anteriores do container
        
        # Frame de Dados (Formulário)
        frame_dados = ttk.LabelFrame(
            self.container_principal, text="Dados do Produto"
        )
        frame_dados.pack(fill='x', padx=10, pady=5)

        # LINHA 0
        ttk.Label(frame_dados, text="Nome do Produto:").grid(
            row=0, column=0, padx=5, pady=5, sticky='w'
        )
        self.entry_nome_produto = ttk.Entry(frame_dados, width=30)
        self.entry_nome_produto.grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )

        ttk.Label(frame_dados, text="Categoria:").grid(
            row=0, column=2, padx=5, pady=5, sticky='w'
        )
        self.entry_categoria = ttk.Entry(frame_dados, width=20)
        self.entry_categoria.grid(
            row=0, column=3, padx=5, pady=5, sticky="ew"
        )

        # LINHA 1
        ttk.Label(frame_dados, text="Quantidade:").grid(
            row=1, column=0, padx=5, pady=5, sticky='w'
        )
        self.entry_qtde = ttk.Entry(frame_dados, width=15)
        self.entry_qtde.grid(
            row=1, column=1, padx=5, pady=5, sticky="w"
        )

        ttk.Label(frame_dados, text="Fornecedor:").grid(
            row=1, column=2, padx=5, pady=5, sticky='w'
        )
        self.entry_fornecedor = ttk.Entry(frame_dados, width=20)
        self.entry_fornecedor.grid(
            row=1, column=3, padx=5, pady=5, sticky="ew"
        )

        # LINHA 2
        ttk.Label(frame_dados, text="Preço Custo (R$):").grid(
            row=2, column=0, padx=5, pady=5, sticky='w'
        )
        self.entry_preco_custo = ttk.Entry(frame_dados, width=15)
        self.entry_preco_custo.grid(
            row=2, column=1, padx=5, pady=5, sticky="w"
        )

        ttk.Label(frame_dados, text="Preço Venda (R$):").grid(
            row=2, column=2, padx=5, pady=5, sticky='w'
        )
        self.entry_preco_venda = ttk.Entry(frame_dados, width=15)
        self.entry_preco_venda.grid(
            row=2, column=3, padx=5, pady=5, sticky="w"
        )

        frame_dados.grid_columnconfigure(1, weight=1)  # Permite expansão da coluna

        # --- Ações ---
        frame_acoes = ttk.Frame(self.container_principal)
        frame_acoes.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_acoes, text="Buscar por Nome: ").pack(side='left', padx=5)
        self.entry_buscar_produto = ttk.Entry(frame_acoes, width=30)
        self.entry_buscar_produto.pack(side='left', padx=5)
        
        ttk.Button(
            frame_acoes, text="Buscar", command=self.buscar_produto
        ).pack(side='left', padx=5)
        
        # Botões à direita
        ttk.Button(
            frame_acoes, text="Remover", command=self.remover_produto
        ).pack(side='right', padx=5)
        ttk.Button(
            frame_acoes, text="Atualizar", command=self.atualizar_produto
        ).pack(side='right', padx=5)
        ttk.Button(
            frame_acoes, text="Adicionar", command=self.adicionar_produto
        ).pack(side='right', padx=5)

        # --- Tabela ---
        frame_tabela = ttk.Frame(self.container_principal)
        frame_tabela.pack(fill='both', expand=True, padx=10, pady=5)

        colunas = ("nome", "quantidade", "preco")   # Define colunas da tabela
        self.tabela_produtos = ttk.Treeview(
            frame_tabela, columns=colunas, show='headings'
        )
        self.tabela_produtos.heading("nome", text="Nome do Produto")
        self.tabela_produtos.heading('quantidade', text="Qtd")
        self.tabela_produtos.heading('preco', text='Venda (R$)')

        self.tabela_produtos.column('nome', width=300)
        self.tabela_produtos.column('quantidade', width=50, anchor='center')
        self.tabela_produtos.column('preco', width=80, anchor='center')

        scrolly = ttk.Scrollbar(
            frame_tabela, orient='vertical', command=self.tabela_produtos.yview
        )
        self.tabela_produtos.configure(yscrollcommand=scrolly.set)

        self.tabela_produtos.pack(side='left', fill='both', expand=True)
        scrolly.pack(side='right', fill='y')

        self.tabela_produtos.bind(
            '<<TreeviewSelect>>', self.preencher_campos
        )

        # --- Rodapé ---
        frame_rodape = ttk.Frame(self.container_principal)
        frame_rodape.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame_rodape, text="© 2025 Sys360").pack(side='left')
        
        ttk.Button(
            frame_rodape, text="🏠 Início", command=self.mostrar_dashboard
        ).pack(side='right')

    # --- Navegação ---
    def _limpar_container(self):
        for widget in self.container_principal.winfo_children():
            widget.destroy()          # Remove todos os widgets do container

    def mostrar_dashboard(self):
        self._limpar_container()      # Limpa a tela atual
        Dashboard(self.container_principal, self)  # Exibe o dashboard

    def mudar_tela(self, nome_tela):
        if nome_tela == "estoque":    # Verifica se a tela solicitada é estoque
            self.criar_tela_estoque()
            self.popular_tabela()

    # --- Lógica de Interface ---
    def popular_tabela(self, produtos_lista=None):
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)  # Limpa a tabela
        
        if produtos_lista is None:
            produtos_lista = lg_produtos.listar_todos_produtos()

        for prod in produtos_lista:
            self.tabela_produtos.insert(
                '', 'end', text=prod[0],
                values=(prod[1], prod[2], f"{prod[3]:.2f}")
            )

    def limpar_campos(self):
        self.entry_nome_produto.delete(0, 'end')
        self.entry_qtde.delete(0, 'end')
        self.entry_preco_custo.delete(0, 'end')
        self.entry_preco_venda.delete(0, 'end')
        self.entry_categoria.delete(0, 'end')
        self.entry_fornecedor.delete(0, 'end')
        self.entry_buscar_produto.delete(0, 'end')
        self.entry_nome_produto.focus_set()
        
        if self.tabela_produtos.selection():
            self.tabela_produtos.selection_remove(
                self.tabela_produtos.selection()
            )

    def preencher_campos(self, event):
        try:
            item = self.tabela_produtos.focus()
            if not item:
                return
            
            id_prod = self.tabela_produtos.item(item)['text']
            prod = lg_produtos.obter_produto_por_id(id_prod)
            
            if prod:
                self.limpar_campos()
                self.entry_nome_produto.insert(0, prod[1])
                self.entry_qtde.insert(0, prod[2])
                self.entry_preco_venda.insert(0, f"{prod[3]:.2f}")
                self.entry_preco_custo.insert(0, f"{prod[4]:.2f}")
                self.entry_categoria.insert(0, prod[5])
                self.entry_fornecedor.insert(0, prod[6])
        except Exception as e:
            print(f"Erro ao preencher: {e}")

    # --- Funções de Abertura de Telas ---
    def abrir_tela_gerenciar_usuarios(self):
        if self.usuario_logado[4] == 'admin':
            TelaGerenciarUsuarios(self)
        else:
            messagebox.showwarning(
                "Acesso Negado", "Apenas administradores."
            )

    def abrir_tela_gerenciar_clientes(self):
        TelaGerenciarClientes(self)

    def abrir_tela_vendas(self):
        TelaVendas(self)

    def abrir_tela_frota(self):
        ScreenFrota(self)
        
    def abrir_tela_financeiro(self):
        if self.usuario_logado[4] in ['admin', 'gestor']:
            TelaFinanceiro(self)
        else:
            messagebox.showwarning(
                "Acesso Negado", "Apenas Gerentes/Admins."
            )

    def mostrar_sobre(self):
        messagebox.showinfo(
            "Sobre", "Sys360 Estoque v1.0\nDesenvolvido por Gabriel Levi"
        )

    def _atualizar_permissoes_interface(self):
        if not self.usuario_logado:
            return
        role = self.usuario_logado[4]
        estado = 'normal' if role == 'admin' else 'disabled'
        try:
            self.menu_cadastros.entryconfig(
                "Gerenciar Usuarios", state=estado
            )
        except:
            pass

    def realizar_logoff(self):
        if messagebox.askyesno(
            "Logoff", "Deseja trocar de usuário?"
        ):
            self.withdraw()
            self.usuario_logado = None
            from gui.screen_login import TelaLogin
            login = TelaLogin(self)
            
            if login.usuario_logado:
                self.usuario_logado = login.usuario_logado
                self.title(
                    f"Sys360 - ({self.usuario_logado[1]})"
                )
                self._atualizar_permissoes_interface()
                self.mostrar_dashboard()
                self.deiconify()
                try:
                    self.state('zoomed')
                except:
                    self.attributes('-zoomed', True)
            else:
                self.quit()

    # --- CRUD Produtos (Pontes) ---
    def adicionar_produto(self):
        try:
            lg_produtos.adicionar_produto(
                self.entry_nome_produto.get(),
                self.entry_qtde.get(),
                self.entry_preco_venda.get(),
                self.entry_preco_custo.get(),
                self.entry_categoria.get(),
                self.entry_fornecedor.get()
            )
            messagebox.showinfo(
                "Sucesso", "Produto adicionado!"
            )
            self.limpar_campos()
            self.popular_tabela()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def atualizar_produto(self):
        item = self.tabela_produtos.focus()
        if not item:
            messagebox.showwarning(
                "Aviso", "Selecione um produto."
            )
            return
        try:
            id_prod = self.tabela_produtos.item(item)['text']
            lg_produtos.atualizar_produto(
                id_prod,
                self.entry_nome_produto.get(),
                self.entry_qtde.get(),
                self.entry_preco_venda.get(),
                self.entry_preco_custo.get(),
                self.entry_categoria.get(),
                self.entry_fornecedor.get()
            )
            messagebox.showinfo(
                "Sucesso", "Produto atualizado!"
            )
            self.limpar_campos()
            self.popular_tabela()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def remover_produto(self):
        item = self.tabela_produtos.focus()
        if not item:
            return
        if messagebox.askyesno(
            "Confirmar", "Remover este produto?"
        ):
            try:
                id_prod = self.tabela_produtos.item(item)['text']
                lg_produtos.remover_produto(id_prod)
                messagebox.showinfo("Sucesso", "Removido!")
                self.limpar_campos()
                self.popular_tabela()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

    def buscar_produto(self):
        try:
            res = lg_produtos.buscar_produtos(
                self.entry_buscar_produto.get()
            )
            self.popular_tabela(res)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            self.popular_tabela()
    
    def abrir_tela_historico(self):
        TelaHistoricoVendas(self)
    
    def abrir_tela_analytics(self):
        TelaAnalytics(self)
    
    def abrir_tela_config(self):
        TelaConfiguracao(self)