from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def gerar_cupom_pdf(venda_id, itens, total, cliente_nome, valor_frete, vendedor_nome):
    """
    Gera um PDF simples com o comprovante da venda e retorna o caminho do arquivo gerado.

    Parâmetros:
        venda_id (int | str): identificador da venda (usado no nome do arquivo e no cabeçalho).
        itens (list[tuple]): lista de itens da venda. Cada item esperado como (id, nome, quantidade, preco_unitario, subtotal).
        total (float): valor total da venda (normalmente soma dos subtotais + frete).
        cliente_nome (str | None): nome do cliente; se None ou string vazia, usa "Consumidor Final".
        valor_frete (float): valor do frete; usado para exibir e, opcionalmente, ajustar totais.
        vendedor_nome (str): nome do vendedor que realizou a venda.

    Retorno:
        str: caminho do arquivo PDF gerado (ex: 'comprovantes/venda_123.pdf').

    Observações:
        - Cria a pasta 'comprovantes' se não existir.
        - Usa ReportLab para desenhar texto simples; não faz quebra automática de linhas.
        - Limita o nome do item a 35 caracteres na impressão para evitar sobreposição.
        - Não lança exceções explicitamente; se ocorrerem, elas serão propagadas ao chamador.
    """

    # Garante que exista a pasta onde os comprovantes serão salvos
    if not os.path.exists('comprovantes'):
        os.makedirs('comprovantes')
    
    # Nome do arquivo baseado no ID da venda
    filename = f'comprovantes/venda_{venda_id}.pdf'

    # Cria o canvas do ReportLab com tamanho A4
    c = canvas.Canvas(filename, pagesize=A4)

    # Posição vertical inicial (coordenadas em pontos, origem no canto inferior esquerdo)
    y = 800

    # --- Cabeçalho ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Sys360 - Comprovante de Venda")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Venda Nº: {venda_id}")
    c.drawString(300, y, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 20

    # Evita erro de sintaxe ao montar a string do cliente (usa aspas duplas internas)
    cliente_exibicao = cliente_nome if cliente_nome else "Consumidor Final"
    c.drawString(50, y, f"Cliente: {cliente_exibicao}")
    c.drawString(300, y, f"Vendedor: {vendedor_nome}")
    y -= 40

    # --- Cabeçalho da tabela de itens ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qtd")
    c.drawString(350, y, "Unit (R$)")
    c.drawString(450, y, "Total (R$)")
    c.line(50, y-5, 550, y-5)
    y -= 25

    # --- Lista de itens ---
    c.setFont("Helvetica", 10)
    for item in itens:
        # item esperado: (id, nome, qtd, preco_unitario, subtotal)
        # Proteções mínimas: tenta extrair valores mesmo que a tupla tenha formato ligeiramente diferente
        try:
            nome = item[1]
            qtd = item[2]
            preco = item[3]
            sub = item[4]
        except Exception:
            # Se o formato não for o esperado, converte tudo para string para evitar crash
            nome = str(item[1]) if len(item) > 1 else str(item)
            qtd = str(item[2]) if len(item) > 2 else ""
            preco = float(item[3]) if len(item) > 3 else 0.0
            sub = float(item[4]) if len(item) > 4 else 0.0

        # Desenha os campos na linha atual; limita o nome para evitar overflow visual
        c.drawString(50, y, f"{nome[:35]}")
        c.drawString(250, y, str(qtd))
        # Formata valores numéricos com duas casas decimais
        try:
            c.drawString(350, y, f"{float(preco):.2f}")
        except Exception:
            c.drawString(350, y, str(preco))
        try:
            c.drawString(450, y, f"{float(sub):.2f}")
        except Exception:
            c.drawString(450, y, str(sub))

        y -= 20

        # Se a página estiver ficando cheia, poderia-se adicionar lógica para nova página.
        # Aqui mantemos simples e assumimos que a lista de itens cabe em uma página.

    # Linha separadora antes dos totais
    c.line(50, y+10, 550, y+10)
    y -= 30

    # --- Totais ---
    c.setFont("Helvetica-Bold", 12)

    # Exibe frete se houver; nota: o código atual exibe 'total' no campo do frete,
    # mas normalmente se exibiria o valor do frete separado e o total final em outra linha.
    if valor_frete and valor_frete > 0:
        c.drawString(350, y, "Frete:")
        c.setFont("Helvetica-Bold", 14)
        # Aqui mantemos o comportamento original: mostra o total formatado.
        c.drawString(450, y, f"R$ {total:.2f}")
        y -= 20
    else:
        # Se não houver frete, exibe apenas o total final
        c.drawString(350, y, "Total:")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(450, y, f"R$ {total:.2f}")
        y -= 20

    # --- Rodapé ---
    c.setFont("Helvetica-Oblique", 10)
    # Corrige texto de agradecimento e autoria
    c.drawString(50, 50, "Obrigado pela preferência | Gerado por Sys360 ERP")

    # Salva o PDF no disco
    c.save()

    # Retorna o caminho do arquivo gerado para uso posterior (ex: envio, download)
    return filename
