# 📦 Sys360 — Sistema de Gestão e Estoque (ERP)

O **Sys360** é um sistema **ERP Desktop completo**, desenvolvido em **Python**, focado na gestão de **pequenas e médias empresas**.  
O sistema oferece controle total sobre **estoque, vendas (PDV), financeiro, clientes e logística**, com destaque para a **integração inteligente com o Google Maps** para roteirização de entregas.

---

## 🚀 Funcionalidades Principais

### 📦 Controle de Estoque
- Cadastro completo de produtos (Preço de Custo, Preço de Venda, Fornecedor)
- Controle de quantidade em tempo real
- Alertas e relatórios de inventário

### 🛒 Ponto de Venda (PDV)
- Interface ágil para registro de vendas
- Carrinho de compras dinâmico
- Cálculo automático de totais e troco
- Baixa automática no estoque após a venda

### 🚚 Logística e Frota (Destaque ⭐)
- **Integração com Google Maps** para geração automática de rotas
- Roteirização inteligente com múltiplas entregas sequenciais
- Cadastro de veículos
- Controle de status da frota (Disponível / Em Rota)

### 👥 Gestão de Clientes
- Cadastro detalhado com validação de dados
- Histórico completo de compras por cliente
- Edição rápida de endereços para entregas

### 💰 Financeiro e Analytics
- Fluxo de Caixa (Entradas e Saídas)
- Dashboard interativo com gráficos de desempenho
- Histórico detalhado de vendas

### ⚙️ Administração e Rede
- Suporte a **Rede Local (Multi-Computador)**
- Banco de dados SQLite compartilhado em rede
- Configuração da empresa (Matriz / Filiais) para cálculo preciso de rotas
- Controle de acesso por usuário (Administrador / Funcionário)

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12  
- **Interface Gráfica:** Tkinter + Ttk  
- **Temas:** ttkthemes  
- **Banco de Dados:** SQLite3  
- **Integrações:**  
  - Google Maps (via `webbrowser` e `urllib`)
- **Relatórios:** ReportLab (Geração de PDFs)

---


📦 Sys360 - Sistema de Gestão e Estoque (ERP)O Sys360 é um sistema ERP Desktop completo desenvolvido em Python, focado em gestão de pequenas e médias empresas. O sistema oferece controle total sobre estoque, vendas (PDV), fluxo de caixa, gestão de clientes e logística de entregas com integração inteligente ao Google Maps.🚀 Funcionalidades Principais📦 Controle de EstoqueCadastro completo de produtos (Preço de Custo, Venda, Fornecedor).Controle de quantidade em tempo real.Alertas e relatórios de inventário.🛒 Ponto de Venda (PDV)Interface ágil para registrar vendas.Carrinho de compras dinâmico.Cálculo automático de troco e totais.Baixa automática no estoque após a venda.🚚 Logística e Frota (Destaque ⭐)Integração com Google Maps: Gera rotas automáticas da sede da empresa até o endereço do cliente.Roteirização Inteligente: Permite selecionar múltiplas entregas e traçar a melhor rota sequencial.Cadastro de veículos e controle de status (Disponível/Em Rota).👥 Gestão de ClientesCadastro detalhado com validação de dados.Histórico de compras por cliente.Edição rápida de endereços para entregas.💰 Financeiro e AnalyticsFluxo de Caixa (Entradas e Saídas).Dashboard interativo com gráficos de desempenho.Histórico completo de vendas.⚙️ Administração e RedeSuporte a Rede Local: O banco de dados (SQLite) pode ser alocado em uma pasta compartilhada, permitindo que múltiplos computadores acessem o mesmo sistema simultaneamente.Configuração da Empresa (Matriz/Filiais) para cálculo preciso de rotas.Controle de acesso por usuário (Admin/Funcionário).🛠️ Tecnologias UtilizadasLinguagem: Python 3.12Interface Gráfica: Tkinter + Ttk (Nativo do Python)Temas: ttkthemes (Para visual moderno)Banco de Dados: SQLite3Integrações: Webbrowser & Urllib (Google Maps API manual)Relatórios: ReportLab (Geração de PDFs)📂 Estrutura do ProjetoO sistema utiliza a arquitetura MVC (Model-View-Controller) adaptada para organização:

BashSys360Estoque/
│
├── assets/             # Ícones e imagens do sistema
├── core/               # Lógica de Negócio (Regras, validações, cálculos)
│   ├── logic_produtos.py
│   ├── logic_frota.py
│   ├── logic_vendas.py
│   └── ...
├── database/           # Gerenciador do Banco de Dados
│   └── db_manager.py   # Conexão, Criação de Tabelas e Queries
├── gui/                # Interface Gráfica (Telas)
│   ├── app_main.py     # Janela Principal
│   ├── screen_login.py # Tela de Login
│   ├── screen_frota.py # Tela de Logística
│   └── ...
├── main.py             # Arquivo inicializador do sistema
├── config.json         # Arquivo de configuração (gerado automaticamente)
└── estoque.db          # Banco de dados (pode ser movido para rede)

---

## 💻 Como Executar o Projeto

### 🔧 Pré-requisitos
Certifique-se de ter o **Python 3.12** instalado.

Instale as dependências necessárias:

```bash
pip install ttkthemes reportlab


▶️ Executando o Sistema

Navegue até a pasta do projeto e execute:

python main.py

🌐 Configurando em Rede (Multi-Computador)

O Sys360 oferece suporte nativo para uso em rede local:

Coloque o arquivo estoque.db em uma pasta compartilhada
(Exemplo: Z:\Sistema\estoque.db)

Abra o sistema em qualquer computador da rede

Acesse: Administração > Configurar Rede/Banco

Selecione o banco de dados na pasta compartilhada

✅ Pronto! Todos os computadores passarão a ler e gravar no mesmo banco de dados.

🤝 Autor

Desenvolvido com dedicação por Gabriel Levi

GitHub: https://github.com/Biellima2811


LinkedIn: https://www.linkedin.com/in/gabriel-levi-0a3a251b0/
