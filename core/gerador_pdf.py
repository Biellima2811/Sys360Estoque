from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def gerar_cupom_pdf(venda_id, itens, total, cliente_nome, valor_frete, vendedor_nome, metodo_pagto, valor_pago, troco):
    if not os.path.exists('comprovantes'):
        os.makedirs('comprovantes')
    
    filename = f'comprovantes/venda_{venda_id}.pdf'
    c = canvas.Canvas(filename, pagesize=A4)
    y = 800

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Sys360 - Comprovante de Venda")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Venda Nº: {venda_id}")
    c.drawString(300, y, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    c.drawString(50, y, f"Cliente: {cliente_nome if cliente_nome else 'Consumidor Final'}")
    c.drawString(300, y, f"Vendedor: {vendedor_nome}")
    y -= 40

    # Itens
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Item")
    c.drawString(250, y, "Qtd")
    c.drawString(350, y, "Unit")
    c.drawString(450, y, "Total")
    c.line(50, y-5, 550, y-5)
    y -= 25

    c.setFont("Helvetica", 10)
    for item in itens:
        # item: (id, nome, qtd, preco, subtotal)
        nome = str(item[1])
        c.drawString(50, y, f"{nome[:35]}")
        c.drawString(250, y, str(item[2]))
        c.drawString(350, y, f"{float(item[3]):.2f}")
        c.drawString(450, y, f"{float(item[4]):.2f}")
        y -= 20

    c.line(50, y+10, 550, y+10)
    y -= 30

    # Totais e Pagamento
    c.setFont("Helvetica-Bold", 12)
    
    if valor_frete > 0:
        c.drawString(350, y, "Frete:")
        c.drawString(450, y, f"R$ {valor_frete:.2f}")
        y -= 20
        
    c.drawString(350, y, "TOTAL A PAGAR:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(450, y, f"R$ {total:.2f}")
    y -= 30
    
    # Detalhes do Pagamento
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Forma de Pagamento: {metodo_pagto}")
    y -= 15
    c.drawString(50, y, f"Valor Pago: R$ {valor_pago:.2f}")
    y -= 15
    c.drawString(50, y, f"Troco: R$ {troco:.2f}")

    # Rodapé
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Obrigado pela preferência | Sys360 ERP")
    c.save()
    return filename