import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

# ADICIONE ESTA LINHA:
import sys_estoque

# A importação do seu banco de dados
import database as db


def popular_treeview():
    """Limpa a TreeView e a preenche com os dados do banco de dados."""

    # CORREÇÃO AQUI: Acessamos a variável global correta, que é '_w1'.
    global _w1

    # Acessamos o widget ScrolledTreeView (que o PAGE nomeou de 'Frame_Lista')
    # usando a variável correta _w1.
    tree = _w1.Frame_Lista

    # Limpa a treeview antes de adicionar novos dados
    for item in tree.get_children():
        tree.delete(item)

    # Busca os dados no banco de dados
    produtos = db.listar_produtos()

    # Insere cada produto na treeview
    for produto in produtos:
        tree.insert('', 'end', values=produto)


# No final do arquivo sys_estoque_support.py

def Adicionar(*args):
    print('sys_estoque_support.Adicionar')
    sys.stdout.flush()


def Atualizar(*args):
    print('sys_estoque_support.Atualizar')
    sys.stdout.flush()


def Pesquisar(*args):
    print('sys_estoque_support.Pesquisar')
    sys.stdout.flush()


# Pode ser que o seu botão Remover não tenha um comando ainda,
# mas se tiver, crie esta função também.
def Remover(*args):
    print('sys_estoque_support.Remover')
    sys.stdout.flush()

def main(*args):
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = sys_estoque.Toplevel1(_top1)

    # Garante que o banco de dados e a tabela estão prontos.
    db.inicializar_db()

    # Popula a tabela com os dados existentes.
    popular_treeview()

    root.mainloop()