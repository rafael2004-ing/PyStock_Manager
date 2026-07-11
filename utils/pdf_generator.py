import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_invoice_pdf(file_path, order, invoice):
    """
    Generates a professional PDF invoice from an Order and Invoice instance.
    Saves the PDF to the specified file_path.
    """
    # Setup document
    # page width = 612, height = 792 (letter size)
    # margins = 54 (0.75 in), content width = 504
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles palette (Corporate Premium Light theme)
    primary_color = colors.HexColor("#1e3a8a")     # Deep blue
    text_color = colors.HexColor("#1f2937")        # Neutral dark
    light_bg = colors.HexColor("#f3f4f6")          # Light grey
    
    # Modify default style
    styles['Normal'].textColor = text_color
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    
    # Header styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color
    )
    
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#6b7280")
    )
    
    meta_title_style = ParagraphStyle(
        'MetaTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=primary_color,
        alignment=2 # Right align
    )
    
    meta_text_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        alignment=2 # Right align
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=primary_color
    )

    bold_text = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14
    )
    
    right_text = ParagraphStyle(
        'RightText',
        parent=styles['Normal'],
        alignment=2
    )

    right_bold_text = ParagraphStyle(
        'RightBoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        alignment=2
    )

    story = []

    # 1. Header Section (Company vs Invoice Meta info)
    header_data = [
        [
            Paragraph("PyStock_Manager", title_style),
            Paragraph(f"FACTURA: {invoice.invoice_number}", meta_title_style)
        ],
        [
            Paragraph("SISTEMA DE GESTIÓN & INVENTARIO", subtitle_style),
            Paragraph(f"Fecha: {invoice.invoice_date or order.order_date or 'Hoy'}", meta_text_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[250, 254])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Divider line
    divider = Table([[""]], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, primary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # 2. Customer Info block
    cust_data = [
        [
            Paragraph("RECEPTOR / CLIENTE", section_heading),
            ""
        ],
        [
            Paragraph("Nombre / Razón Social:", bold_text),
            Paragraph(order.customer_name, styles['Normal'])
        ],
        [
            Paragraph("RIF / Cédula:", bold_text),
            Paragraph(order.customer_rif, styles['Normal'])
        ]
    ]
    cust_table = Table(cust_data, colWidths=[150, 354])
    cust_table.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('LINELEFT', (0,0), (0,-1), 4, primary_color),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 20))

    # 3. Itemized List Table
    table_headers = [
        Paragraph("<b>Código</b>", bold_text),
        Paragraph("<b>Descripción</b>", bold_text),
        Paragraph("<b>Cant.</b>", right_bold_text),
        Paragraph("<b>Precio Unit.</b>", right_bold_text),
        Paragraph("<b>Total</b>", right_bold_text)
    ]
    
    items_data = [table_headers]
    for item in order.items:
        items_data.append([
            Paragraph(item.product_code or "N/A", styles['Normal']),
            Paragraph(item.product_name, styles['Normal']),
            Paragraph(str(item.quantity), right_text),
            Paragraph(f"${item.price:,.2f}", right_text),
            Paragraph(f"${item.subtotal:,.2f}", right_text)
        ])
        
    # Table colWidths layout: Code=70, Desc=224, Qty=40, Price=80, Total=90 (Sum = 504)
    items_table = Table(items_data, colWidths=[70, 224, 40, 80, 90])
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), light_bg),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,0), 1, primary_color),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
    ]
    
    # Alternating row background colors
    for i in range(1, len(items_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor("#f9fafb")))
            
    items_table.setStyle(TableStyle(t_style))
    story.append(items_table)
    story.append(Spacer(1, 20))

    # 4. Totals Block (Subtotal, IVA 16%, Total)
    totals_data = [
        [
            "", 
            Paragraph("Subtotal:", bold_text), 
            Paragraph(f"${invoice.subtotal:,.2f}", right_text)
        ],
        [
            "", 
            Paragraph("I.V.A. (16%):", bold_text), 
            Paragraph(f"${invoice.tax:,.2f}", right_text)
        ],
        [
            "", 
            Paragraph("<b>TOTAL:</b>", ParagraphStyle('TotalLbl', parent=bold_text, textColor=primary_color)), 
            Paragraph(f"<b>${invoice.total:,.2f}</b>", ParagraphStyle('TotalVal', parent=right_bold_text, textColor=primary_color))
        ]
    ]
    totals_table = Table(totals_data, colWidths=[314, 100, 90])
    totals_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (1,0), (-1,-1), 6),
        ('RIGHTPADDING', (1,0), (-1,-1), 6),
        ('LINEBELOW', (1,0), (-1,1), 0.5, colors.HexColor("#e5e7eb")),
        ('LINEBELOW', (1,2), (-1,2), 1.5, primary_color),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 40))

    # 5. Footer Info
    footer_style = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        alignment=1, # Center
        textColor=colors.HexColor("#9ca3af"),
        fontSize=8
    )
    story.append(Paragraph("¡Gracias por su confianza y preferencia!", ParagraphStyle('ThankYou', parent=footer_style, fontName='Helvetica-Bold', fontSize=10, textColor=primary_color)))
    story.append(Spacer(1, 5))
    story.append(Paragraph("PyStock_Manager - Sistema Modular de Gestión e Inventario", footer_style))
    story.append(Paragraph("Si tiene alguna duda sobre esta factura, por favor contáctenos.", footer_style))

    # Build the document
    doc.build(story)


def generate_sales_report_pdf(file_path, start_date, end_date, report_data):
    """
    Generates a professional PDF sales report.
    report_data should be a dictionary:
    {
        "total_revenue": str,
        "order_count": str/int,
        "average_order": str,
        "orders": list of Order objects
    }
    """
    from datetime import datetime
    
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#1e3a8a")     # Deep blue
    text_color = colors.HexColor("#1f2937")        # Neutral dark
    light_bg = colors.HexColor("#f3f4f6")          # Light grey
    
    styles['Normal'].textColor = text_color
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#6b7280")
    )
    
    meta_title_style = ParagraphStyle(
        'MetaTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=primary_color,
        alignment=2
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=primary_color
    )

    bold_text = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14
    )
    
    right_text = ParagraphStyle(
        'RightText',
        parent=styles['Normal'],
        alignment=2
    )

    right_bold_text = ParagraphStyle(
        'RightBoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        alignment=2
    )

    story = []

    # 1. Header (Report name vs Date range)
    header_data = [
        [
            Paragraph("REPORTE DE VENTAS", title_style),
            Paragraph("PyStock_Manager", meta_title_style)
        ],
        [
            Paragraph(f"Período: {start_date} al {end_date}", ParagraphStyle('PeriodText', parent=styles['Normal'], fontName='Helvetica-Bold', textColor=colors.HexColor("#4b5563"))),
            Paragraph("SISTEMA DE GESTIÓN & INVENTARIO", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[300, 204])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Divider line
    divider = Table([[""]], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, primary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # 2. Stats Dashboard
    stats_data = [
        [
            Paragraph("<b>Ingreso Total</b>", ParagraphStyle('StatLbl1', parent=styles['Normal'], alignment=1, textColor=colors.HexColor("#4b5563"))),
            Paragraph("<b>Facturas Emitidas</b>", ParagraphStyle('StatLbl2', parent=styles['Normal'], alignment=1, textColor=colors.HexColor("#4b5563"))),
            Paragraph("<b>Ticket Promedio</b>", ParagraphStyle('StatLbl3', parent=styles['Normal'], alignment=1, textColor=colors.HexColor("#4b5563")))
        ],
        [
            Paragraph(f"<b>{report_data['total_revenue']}</b>", ParagraphStyle('StatVal1', parent=styles['Normal'], alignment=1, fontSize=16, leading=20, textColor=colors.HexColor("#16a34a"))),
            Paragraph(f"<b>{report_data['order_count']}</b>", ParagraphStyle('StatVal2', parent=styles['Normal'], alignment=1, fontSize=16, leading=20, textColor=primary_color)),
            Paragraph(f"<b>{report_data['average_order']}</b>", ParagraphStyle('StatVal3', parent=styles['Normal'], alignment=1, fontSize=16, leading=20, textColor=primary_color))
        ]
    ]
    stats_table = Table(stats_data, colWidths=[168, 168, 168])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#d1d5db")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d1d5db")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))

    # 3. Sales Table Section Heading
    story.append(Paragraph("DETALLE DE FACTURAS EMITIDAS", section_heading))
    story.append(Spacer(1, 8))

    # 4. Sales Table
    table_headers = [
        Paragraph("<b>Factura ID</b>", bold_text),
        Paragraph("<b>Fecha Emisión</b>", bold_text),
        Paragraph("<b>Cliente</b>", bold_text),
        Paragraph("<b>Subtotal</b>", right_bold_text),
        Paragraph("<b>Impuesto (16%)</b>", right_bold_text),
        Paragraph("<b>Total</b>", right_bold_text)
    ]
    
    table_data = [table_headers]
    for o in report_data["orders"]:
        table_data.append([
            Paragraph(f"FAC-{o.id:04d}", styles['Normal']),
            Paragraph(o.order_date[:19] if o.order_date else "N/A", styles['Normal']),
            Paragraph(f"{o.customer_name} ({o.customer_rif})", styles['Normal']),
            Paragraph(f"${o.subtotal:,.2f}", right_text),
            Paragraph(f"${o.tax:,.2f}", right_text),
            Paragraph(f"${o.total:,.2f}", right_text)
        ])
        
    sales_table = Table(table_data, colWidths=[65, 105, 144, 65, 60, 65])
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), light_bg),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,0), 1, primary_color),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
    ]
    
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor("#f9fafb")))
            
    sales_table.setStyle(TableStyle(t_style))
    story.append(sales_table)
    story.append(Spacer(1, 30))

    # 5. Footer Info
    footer_style = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        alignment=1, # Center
        textColor=colors.HexColor("#9ca3af"),
        fontSize=8
    )
    story.append(Paragraph("PyStock_Manager - Reporte Generado Automáticamente", footer_style))
    story.append(Paragraph(f"Fecha de Impresión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    doc.build(story)
