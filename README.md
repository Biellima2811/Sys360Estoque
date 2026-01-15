# 📦 Sys360 ERP - Sistema de Gestão Empresarial

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Interface-Tkinter-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen?style=for-the-badge)

O **Sys360** é um ERP Desktop robusto e moderno desenvolvido em Python. Projetado para pequenas e médias empresas, ele oferece controle total sobre estoque, vendas, finanças e logística, com uma interface gráfica refinada e amigável.

---

## 🎨 Destaques Visuais & UX

O projeto se destaca por fugir do visual padrão de aplicações desktop antigas:

* **Login Moderno:** Interface "Split-Screen" com banner lateral e design minimalista.
* **Menu Lateral (Sidebar):** Navegação fluida estilo dashboard web.
* **Responsividade:** Telas que se adaptam ao tamanho da janela.

---

## 🚀 Funcionalidades Principais

### 📦 Gestão de Estoque
* Cadastro completo de produtos (Custo, Venda, Fornecedor).
* Controle de quantidade em tempo real.
* Busca rápida e filtros.

### 💰 Financeiro & Analytics
* **Fluxo de Caixa:** Registro de Receitas e Despesas.
* **Dashboards:** Cards de resumo (Saldo, Entradas, Saídas) e gráficos interativos.
* Histórico detalhado de movimentações.

### 🚚 Frota & Logística (Integração Google Maps)
* **Roteirização Inteligente:** O sistema coleta o endereço da sede e o endereço do cliente.
* **Geração de Rota:** Cria um link direto para o Google Maps com o trajeto otimizado para a entrega.
* Controle de veículos disponíveis e em rota.

### 🛒 Ponto de Venda (PDV)
* Registro rápido de vendas.
* Baixa automática no estoque.
* Geração de histórico por cliente.

### ⚙️ Administração
* **Rede Local:** Suporte para banco de dados compartilhado em rede (vários computadores acessando o mesmo sistema).
* Controle de Usuários e Permissões (Admin vs Funcionário).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.12
* **GUI:** Tkinter, Ttk, Ttkthemes
* **Banco de Dados:** SQLite3
* **Segurança:** Bcrypt (Hash de senhas)
* **Gráficos:** Matplotlib (Opcional para analytics)
* **Web:** Webbrowser & Urllib (Integração Maps)

---

## 📂 Estrutura do Projeto (MVC)

O código segue padrões profissionais de organização para facilitar a manutenção:

```bash
Sys360Estoque/
│
├── assets/             # Imagens, Ícones e Banners
├── core/               # Lógica de Negócio (Controllers)
│   ├── logic_produtos.py
│   ├── logic_financeiro.py
│   └── ...
├── database/           # Gerenciamento de Dados (Model/DAO)
│   └── db_manager.py
├── gui/                # Interface Gráfica (Views)
│   ├── app_main.py     # Janela Principal e Menu
│   ├── screen_login.py # Tela de Login
│   ├── screen_estoque.py
│   └── ...
├── main.py             # Ponto de Entrada (Entry Point)
└── config.json         # Configurações locais