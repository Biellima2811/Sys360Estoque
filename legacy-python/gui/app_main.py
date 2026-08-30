import tkinter as tk
from tkinter import messagebox, ttk
import os

# Telas
from gui.screen_dashboard import Dashboard
from gui.screen_estoque import TelaEstoque  # <--- Importamos a nova tela
from gui.screen_vendas import TelaVendas
from gui.screen_financeiro import TelaFinanceiro
from gui.screen_clientes import TelaGerenciarClientes
from gui.screen_frota import ScreenFrota
from gui.screen_historico import TelaHistoricoVendas
from gui.screen_analytics import TelaAnalytics
from gui.screen_config import TelaConfiguracao
from gui.screen_admin import TelaGerenciarUsuarios

try:
    from ttkthemes import ThemedTk
    JanelaPai = ThemedTk
except ImportError:
    JanelaPai = tk.Tk

class App(JanelaPai):
    def __init__(self):
        super().__init__()
        
        # Tema Moderno
        if JanelaPai == ThemedTk:
            self.set_theme("arc") # Um tema clean, azulado e moderno

        self.title("Sys360 ERP - Gestão Integrada")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Ícone
        try:
            caminho_icone = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "Estoque360.ico"))
            if os.path.exists(caminho_icone): self.iconbitmap(caminho_icone)
        except: pass

        self.usuario_logado = None
        
        # --- ESTILOS CUSTOMIZADOS (Menu Lateral) ---
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#2c3e50") # Azul escuro
        style.configure("Sidebar.TLabel", background="#2c3e50", foreground="white", font=("Segoe UI", 12))
        
        # Estilo dos Botões do Menu
        style.configure("Menu.TButton", 
                        font=("Segoe UI", 11), 
                        padding=10, 
                        anchor="w",
                        background="#2c3e50",
                        foreground="black") 
        
        # Layout Principal (Sidebar + Conteúdo)
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill='both', expand=True)

        self._criar_sidebar()
        self._criar_area_conteudo()
        
        # Inicia no Dashboard (se logado) ou Login
        # Nota: A lógica de login chama self.mostrar_dashboard() depois
    
    def _criar_sidebar(self):
        """Cria o menu lateral moderno."""
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False) # Mantém a largura fixa

        # Logo / Título
        lbl_logo = ttk.Label(self.sidebar, text="Sys360", style="Sidebar.TLabel", font=("Segoe UI", 20, "bold"))
        lbl_logo.pack(pady=(30, 10))
        
        ttk.Label(self.sidebar, text="Enterprise System", style="Sidebar.TLabel", font=("Arial", 9)).pack(pady=(0, 30))

        # Botões de Navegação
        # Dica: Use emojis como ícones se não tiver imagens PNG
        self._criar_botao_menu("📊 Dashboard", self.mostrar_dashboard)
        self._criar_botao_menu("🛒 Nova Venda (PDV)", self.abrir_tela_vendas)
        self._criar_botao_menu("📦 Estoque", self.abrir_tela_estoque)
        self._criar_botao_menu("👥 Clientes", self.abrir_tela_gerenciar_clientes)
        self._criar_botao_menu("🚚 Frota & Entrega", self.abrir_tela_frota)
        self._criar_botao_menu("💰 Financeiro", self.abrir_tela_financeiro)
        
        # Separador visual
        tk.Frame(self.sidebar, height=1, bg="#7f8c8d").pack(fill='x', padx=20, pady=20)
        
        self._criar_botao_menu("⚙️ Configurações", self.abrir_tela_config)
        self._criar_botao_menu("❌ Sair", self.realizar_logoff)
        
        # Info Usuário no Rodapé da Sidebar
        self.lbl_usuario = ttk.Label(self.sidebar, text="...", style="Sidebar.TLabel", font=("Arial", 9))
        self.lbl_usuario.pack(side='bottom', pady=20)

    def _criar_botao_menu(self, texto, comando):
        """Helper para criar botões padronizados."""
        btn = ttk.Button(self.sidebar, text=texto, command=comando, style="Menu.TButton")
        btn.pack(fill='x', padx=10, pady=5)

    def _criar_area_conteudo(self):
        """Área branca onde as telas aparecem."""
        self.content_area = tk.Frame(self.main_container, bg="#ecf0f1") # Cinza bem claro
        self.content_area.pack(side='right', fill='both', expand=True)

    # --- Navegação ---
    def limpar_conteudo(self):
        """Remove a tela atual para mostrar a próxima."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def mostrar_dashboard(self):
        self.limpar_conteudo()
        Dashboard(self.content_area, self)

    def abrir_tela_estoque(self):
        self.limpar_conteudo()
        TelaEstoque(self.content_area) # Instancia a classe que criamos no outro arquivo

    def abrir_tela_vendas(self):
        TelaVendas(self) # Vendas é Toplevel (abre por cima) ou você pode adaptar para Frame

    def abrir_tela_financeiro(self):
        if self.check_permissao(['admin', 'gestor']):
            self.limpar_conteudo()
            TelaFinanceiro(self.content_area) # Se Financeiro for Frame. Se for Toplevel, chame direto.

    def abrir_tela_gerenciar_clientes(self):
        TelaGerenciarClientes(self) # Mantivemos como Janela Separada

    def abrir_tela_frota(self):
        ScreenFrota(self) # Mantivemos como Janela Separada

    def abrir_tela_config(self):
        TelaConfiguracao(self)

    # --- Autenticação e Utilitários ---
    def check_permissao(self, roles_permitidas):
        if self.usuario_logado and self.usuario_logado[4] in roles_permitidas:
            return True
        messagebox.showwarning("Acesso Negado", "Você não tem permissão.")
        return False

    def realizar_logoff(self):
        if messagebox.askyesno("Logoff", "Deseja sair do sistema?"):
            # Opção A: Fecha tudo (usuário abre de novo)
            self.destroy()
