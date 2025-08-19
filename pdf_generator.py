import os
import webbrowser
from tkinter import messagebox
import gui_utils
import config
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors


def gerar_pdf_cotacao(dados, empresa_orcamento, diretorio=None):
    """Gera um arquivo PDF com os detalhes da cotação."""

    if diretorio:
        save_dir = diretorio
    else:
        save_dir = config.DIR_COTACOES

    os.makedirs(save_dir, exist_ok=True)
    arquivo_path = os.path.join(save_dir, f"{dados['numero']}_cotacao.pdf")

    c = canvas.Canvas(arquivo_path, pagesize=A4)
    width, height = A4

    left_margin = 30
    right_margin = width - 30
    y = height - 30

    # Informações da Empresa Fornecedora
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, empresa_orcamento.get("nome", "EMPRESA FORNECEDORA"))
    y -= 12
    c.setFont("Helvetica", 9)
    c.drawString(left_margin, y, f"CNPJ: {empresa_orcamento.get('cnpj', 'N/A')}")
    y -= 12
    c.drawString(left_margin, y, f"Endereço: {empresa_orcamento.get('endereco', 'N/A')}")
    y -= 12
    c.drawString(left_margin, y, f"Fone: {empresa_orcamento.get('fone', 'N/A')}")

    # Informações da Cotação
    y_cotacao_info = height - 30
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(right_margin, y_cotacao_info, f"COTAÇÃO Nº: {dados['numero']}")
    y_cotacao_info -= 16
    c.setFont("Helvetica", 10)
    c.drawRightString(right_margin, y_cotacao_info, f"Data: {dados['data']}")
    y_cotacao_info -= 16
    c.drawRightString(right_margin, y_cotacao_info, f"Vendedor: {dados.get('vendedor_nome', 'N/A')}")

    vendedor_codigo = dados.get('vendedor_codigo')
    vendedor_email = "N/A"
    vendedor_celular = ""
    if vendedor_codigo:
        for vendedor in config.vendedores_cadastrados:
            if vendedor.get('codigo') == vendedor_codigo:
                vendedor_email = vendedor.get('email', 'N/A')
                vendedor_celular = vendedor.get('celular', '')
                break
    y_cotacao_info -= 12
    c.drawRightString(right_margin, y_cotacao_info, f"Email: {vendedor_email}")
    if vendedor_celular:
        y_cotacao_info -= 12
        c.drawRightString(right_margin, y_cotacao_info, f"Celular: {vendedor_celular}")

    y = min(y, y_cotacao_info) - 25
    c.line(left_margin, y, right_margin, y)
    y -= 25

    # Informações do Cliente
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_margin, y, f"Cliente: {dados['empresa_cliente']}")
    c.drawString(width / 2 + 50, y, f"Contato: {dados['cliente']}")
    y -= 16
    c.drawString(left_margin, y, f"Depto: {dados['depto']}")
    c.drawString(width / 2 + 50, y, f"E-mail: {dados['email']}")
    y -= 25

    # Prepara os dados para a tabela
    styles = getSampleStyleSheet()
    style_header = ParagraphStyle(name='TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5,
                                  alignment=TA_CENTER)
    style_body_left = ParagraphStyle(name='TableBodyLeft', parent=styles['Normal'], fontName='Helvetica', fontSize=7,
                                     alignment=TA_LEFT, leading=9)
    style_body_center = ParagraphStyle(name='TableBodyCenter', parent=styles['Normal'], fontName='Helvetica',
                                       fontSize=7, alignment=TA_CENTER, leading=9)
    style_body_right = ParagraphStyle(name='TableBodyRight', parent=styles['Normal'], fontName='Helvetica', fontSize=7,
                                      alignment=TA_RIGHT, leading=9)

    header_data = [
        Paragraph('Item', style_header), Paragraph('Produto', style_header), Paragraph('NCM', style_header),
        Paragraph('Qtd', style_header), Paragraph('Unitário', style_header), Paragraph('Total', style_header),
        Paragraph('IPI', style_header), Paragraph('ST/DIFAL', style_header)
    ]

    table_data = [header_data]

    total_ibpt_fed = 0
    total_ibpt_est = 0
    contem_consumo_sem_ie = False
    primeira_operacao = dados['itens'][0]['operacao'] if dados['itens'] else ''
    total_difal_val = dados.get('total_difal', 0)
    uf_faturamento = dados['itens'][0]['uf_destino'] if dados['itens'] else ''

    for idx, it in enumerate(dados['itens'], 1):
        if 'Consumo' in it.get('operacao', ''):
            total_ibpt_fed += round(config.ibpt_fed.get(it['cf'], 0.0) * it['valor'] / 100, 2)
            total_ibpt_est += round(config.ibpt_est.get(it['cf'], 0.0) * it['valor'] / 100, 2)
        if it.get('operacao') == 'Consumo sem IE':
            contem_consumo_sem_ie = True

        # --- ALTERAÇÃO: Lógica para exibir "Isento" no IPI ---
        ipi_val = it.get('ipi', 0)
        ipi_pct = it.get('ipi_pct', 0)
        ipi_str = ""
        if ipi_pct == 0:
            ipi_str = "Isento"
        else:
            ipi_str_val = gui_utils.moeda(ipi_val)
            if ipi_val > 0:
                ipi_pct_str = f"{ipi_pct:.2f}".rstrip('0').rstrip('.')
                ipi_str = f"{ipi_str_val}<br/>({ipi_pct_str}%)"
            else:
                ipi_str = ipi_str_val
        # --- FIM DA ALTERAÇÃO ---

        st_difal_val = it.get('icms_st', 0) + it.get('difal', 0)
        st_difal_str = gui_utils.moeda(st_difal_val)
        if st_difal_val > 0:
            icms_int_pct = config.icms_interno_dict.get((it['uf_destino'], it['cf']), 0)
            icms_inter_pct = config.icms_inter_dict.get((it['uf_destino'], it['cf']), 0)
            fcp_pct = config.fcp_dict.get((it['uf_destino'], it['cf']), 0)
            difal_pct = (icms_int_pct + fcp_pct) - icms_inter_pct
            difal_pct_str = f"{difal_pct:.2f}".rstrip('0').rstrip('.')
            st_difal_str = f"{st_difal_str}<br/>({difal_pct_str}%)"

        row = [
            Paragraph(str(idx), style_body_center),
            Paragraph(it.get('descricao_usuario', it['descricao']), style_body_left),
            Paragraph(it['ncm'], style_body_center),
            Paragraph(str(int(it['qtd'])) if it['qtd'] == int(it['qtd']) else str(it['qtd']), style_body_right),
            Paragraph(gui_utils.moeda(it['unitario']), style_body_right),
            Paragraph(gui_utils.moeda(it['valor']), style_body_right),
            Paragraph(ipi_str, style_body_right),
            Paragraph(st_difal_str, style_body_right),
        ]
        table_data.append(row)

    col_widths = [30, 175, 55, 30, 65, 65, 65, 50]

    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    table_width, table_height = t.wrapOn(c, width, height)

    if y - table_height < 150:
        c.showPage()
        y = height - 40

    y -= table_height + 10
    t.drawOn(c, left_margin, y)

    # Totalização Final
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, y, f"Total Produtos: {gui_utils.moeda(dados['total_produtos'])}")
    y -= 16
    c.drawString(left_margin, y, f"Total IPI: {gui_utils.moeda(dados['total_ipi'])}")
    y -= 16
    total_st = dados.get('total_icms_st', 0)
    total_difal = dados.get('total_difal', 0)
    if total_st > 0:
        c.drawString(left_margin, y, f"Total ICMS ST: {gui_utils.moeda(total_st)}")
        y -= 16
    if total_difal > 0:
        c.drawString(left_margin, y, f"Total GNRE A RECOLHER: {gui_utils.moeda(total_difal)}")
        y -= 16
    total_ibpt = total_ibpt_fed + total_ibpt_est
    if total_ibpt > 0 and dados['total_produtos'] > 0:
        percentual_ibpt = (total_ibpt / dados['total_produtos']) * 100
        c.drawString(left_margin, y,
                     f"Total Aprox. Tributos (IBPT): {gui_utils.moeda(total_ibpt)} ({percentual_ibpt:.2f}%)")
        y -= 16
    y -= 8
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, y, f"TOTAL GERAL DA NOTA FISCAL: {gui_utils.moeda(dados['total_geral'])}")
    y -= 35

    footer_text = []
    footer_text.append("ICMS incluso, IPI (Ver Item)")
    footer_text.append(f"Fabricação: Prazo de fabricação: {dados.get('prazo', '___')} dias úteis após confirmação.")
    footer_text.append("Material posto em fábrica.")

    condpag = (dados.get('condpag', '') or '').strip()
    if condpag and any(char.isdigit() for char in condpag):
        if not condpag.upper().endswith('DDL'):
            condpag += " DDL"
    footer_text.append(f"Condição de pagamento: {condpag}.")
    footer_text.append("Validade da proposta: 30 dias.")
    footer_text.append(f"Faturado para (UF): <b>{uf_faturamento.upper()}</b>")
    footer_text.append(f"MATERIAL TEM COMO DESTINO: {primeira_operacao.upper()}")

    observacao = dados.get("observacao", "").strip()
    if observacao:
        footer_text.append(f"<br/><b>OBS.:</b>&nbsp;&nbsp;&nbsp;{observacao.replace(os.linesep, '<br/>')}")

    if contem_consumo_sem_ie:
        footer_text.append(f"<br/><b>OBSERVAÇÃO DIFAL EMBUTIDO de {gui_utils.moeda(total_difal_val)}</b>")
        footer_text.append(
            '\"MERCADORIA SEGUE PARA USO E CONSUMO. RECOLHIMENTO DO DIFAL PARA NÃO CONTRIBUINTE CONFORME EC 87/2015 E CONVÊNIO ICMS 93/2015.\"')

    footer_style = ParagraphStyle(
        name='FooterStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
    )

    footer_content = "<br/>".join(footer_text)
    p = Paragraph(footer_content, footer_style)

    p_width, p_height = p.wrap(right_margin - left_margin, height)

    if y - p_height < 40:
        c.showPage()
        y = height - 40

    p.drawOn(c, left_margin, y - p_height)

    c.save()

    try:
        if os.name == 'nt':
            os.startfile(arquivo_path)
        else:
            webbrowser.open(f"file://{os.path.abspath(arquivo_path)}")
    except Exception as e:
        messagebox.showerror("Erro",
                             f"Não foi possível abrir o PDF. Verifique se há um visualizador de PDF instalado. Erro: {e}")

    return arquivo_path