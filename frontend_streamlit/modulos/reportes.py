"""
Generación de reportes PDF / Word / Excel
Patrón: gemelo_digital_minero/modules/reportes.py del profesor
"""
import io
import pandas as pd
from datetime import datetime
import database as db

# ── PDF con ReportLab ─────────────────────────────────────────────────────────

def generar_pdf(usuario: str = "Sistema") -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=1*inch,      bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    # Estilos personalizados
    titulo_style = ParagraphStyle("Titulo", parent=styles["Title"],
                                  fontSize=20, textColor=colors.HexColor("#0f172a"),
                                  spaceAfter=12, alignment=TA_CENTER)
    sub_style    = ParagraphStyle("Sub", parent=styles["Heading2"],
                                  fontSize=14, textColor=colors.HexColor("#1e40af"),
                                  spaceAfter=8, spaceBefore=14)
    normal_style = ParagraphStyle("Normal2", parent=styles["Normal"],
                                  fontSize=10, leading=14, spaceAfter=6)
    foot_style   = ParagraphStyle("Footer", parent=styles["Normal"],
                                  fontSize=8, textColor=colors.HexColor("#94a3b8"),
                                  alignment=TA_CENTER)

    # ── Encabezado ──────────────────────────────────────────────────────────────
    story.append(Paragraph("🌾 VRI DIGITAL TWIN — SISTEMA DE RIEGO AUTÓNOMO", titulo_style))
    story.append(Paragraph("Reporte Ejecutivo de Operaciones", sub_style))
    story.append(Paragraph(
        f"Generado por: <b>{usuario}</b>  |  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))

    # ── Información del campo ───────────────────────────────────────────────────
    story.append(Paragraph("1. INFORMACIÓN DEL CAMPO", sub_style))
    campo_data = [
        ["Parámetro", "Valor"],
        ["Nombre",          "Campo San Pablo Sector A"],
        ["Cultivo",         "Maíz Amarillo Duro (Dekalb DK7088)"],
        ["Etapa",           "VT (Floración)"],
        ["Área Total",      "150.5 ha"],
        ["Tipo de Suelo",   "Franco Limosa"],
        ["Método de Riego", "Pivote Central VRI"],
    ]
    t = Table(campo_data, colWidths=[2.5*inch, 4*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("BACKGROUND",    (0,1), (-1,-1), colors.HexColor("#f0f9ff")),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    # ── Estado de zonas ─────────────────────────────────────────────────────────
    story.append(Paragraph("2. ESTADO DE ZONAS DE MANEJO", sub_style))
    zonas_df = db.get_zonas()
    zona_data = [["Zona", "Humedad 10cm (%)", "Temp. Canopía (°C)", "CWSI", "Dosis RL (mm)"]]
    for _, row in zonas_df.iterrows():
        zona_data.append([
            row["sector"],
            f"{row['humedad10']:.1f}",
            f"{row['temp_canopia']:.1f}",
            f"{row['cwsi']:.2f}",
            f"{row['dosis_mm']:.1f}",
        ])
    t2 = Table(zona_data, colWidths=[1*inch, 1.5*inch, 1.7*inch, 1*inch, 1.3*inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#15803d")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("BACKGROUND",    (0,1), (-1,-1), colors.HexColor("#f0fdf4")),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bbf7d0")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))

    # ── Decisiones RL ──────────────────────────────────────────────────────────
    story.append(Paragraph("3. HISTORIAL DE DECISIONES RL", sub_style))
    dec_df = db.get_decisiones()
    if not dec_df.empty:
        dec_data = [["ID", "Zona", "Dosis (mm)", "Confianza", "Estado", "Fecha"]]
        for _, row in dec_df.head(10).iterrows():
            dec_data.append([
                str(row["id"])[:12],
                row["zona_id"],
                f"{row['dosis_mm']:.2f}",
                f"{row['confianza']*100:.1f}%",
                row["estado"],
                str(row["timestamp"])[:16],
            ])
        t3 = Table(dec_data, colWidths=[1.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.5*inch])
        t3.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#7c3aed")),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("BACKGROUND",    (0,1), (-1,-1), colors.HexColor("#faf5ff")),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#ddd6fe")),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("ALIGN",         (2,0), (-1,-1), "CENTER"),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("No hay decisiones registradas.", normal_style))

    story.append(Spacer(1, 0.2*inch))

    # ── Ejecuciones de riego ────────────────────────────────────────────────────
    story.append(Paragraph("4. HISTORIAL DE EJECUCIONES DE RIEGO", sub_style))
    ej_df = db.get_ejecuciones(limit=10)
    if not ej_df.empty:
        ej_data = [["Zona", "Dosis (mm)", "Volumen (m³)", "Tipo", "Ejecutado por", "Fecha"]]
        for _, row in ej_df.iterrows():
            ej_data.append([
                row["zona_id"], f"{row['dosis_mm']:.2f}",
                f"{row['volumen_m3']:.3f}", row["tipo"],
                str(row["ejecutado_por"]), str(row["timestamp"])[:16],
            ])
        t4 = Table(ej_data, colWidths=[0.9*inch, 0.9*inch, 1*inch, 0.9*inch, 1.2*inch, 1.5*inch])
        t4.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#0369a1")),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("BACKGROUND",    (0,1), (-1,-1), colors.HexColor("#f0f9ff")),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bae6fd")),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(t4)
    else:
        story.append(Paragraph("No hay ejecuciones registradas aún.", normal_style))

    story.append(Spacer(1, 0.3*inch))

    # Recomendaciones
    story.append(Paragraph("5. RECOMENDACIONES", sub_style))
    recs = [
        "• Priorizar riego en Zona NE (CWSI = 0.61 — estrés crítico detectado).",
        "• Mantener humedad sobre 25% (PMP) en todos los horizontes.",
        "• Revisar sensores de la Zona SW — lecturas estables, sin estrés.",
        "• Programar próxima inferencia RL en ventana nocturna (22:00 – 04:00).",
        "• Actualizar parámetros del modelo PPO con feedback de las últimas ejecuciones.",
    ]
    for r in recs:
        story.append(Paragraph(r, normal_style))

    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("─" * 90, foot_style))
    story.append(Paragraph(
        "VRI Digital Twin — Sistema de Riego Autónomo con Aprendizaje por Refuerzo | "
        f"Generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        foot_style
    ))

    doc.build(story)
    return buffer.getvalue()


# ── Word con python-docx ──────────────────────────────────────────────────────

def generar_word(usuario: str = "Sistema") -> bytes:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT

    doc = Document()

    # Estilos base
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # Título
    t = doc.add_heading("VRI DIGITAL TWIN — INFORME DE RIEGO AUTÓNOMO", 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("Informe Técnico Detallado", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(f"Generado por: {usuario}  |  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 1. Resumen ejecutivo
    doc.add_heading("1. Resumen Ejecutivo", level=1)
    doc.add_paragraph(
        "El presente informe detalla el estado operativo del gemelo digital de riego variable (VRI) "
        "para el Campo San Pablo Sector A. El sistema integra un agente de aprendizaje por refuerzo (PPO) "
        "con sensores IoT para optimizar la aplicación de agua en tiempo real."
    )

    # 2. Estado de zonas
    doc.add_heading("2. Estado de Zonas de Manejo", level=1)
    zonas_df = db.get_zonas()
    headers  = ["Zona", "Humedad 10cm (%)", "Temp. Canopía (°C)", "CWSI", "Dosis RL (mm)"]
    table    = doc.add_table(rows=1, cols=len(headers))
    table.alignment   = WD_TABLE_ALIGNMENT.CENTER
    table.style       = "Light Grid Accent 1"
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True

    for _, row in zonas_df.iterrows():
        cells = table.add_row().cells
        cells[0].text = row["sector"]
        cells[1].text = f"{row['humedad10']:.1f}"
        cells[2].text = f"{row['temp_canopia']:.1f}"
        cells[3].text = f"{row['cwsi']:.2f}"
        cells[4].text = f"{row['dosis_mm']:.1f}"

    # 3. Decisiones RL
    doc.add_heading("3. Decisiones del Agente RL (PPO)", level=1)
    dec_df = db.get_decisiones()
    if not dec_df.empty:
        headers2 = ["ID", "Zona", "Dosis (mm)", "Confianza", "Estado", "Fecha"]
        t2       = doc.add_table(rows=1, cols=len(headers2))
        t2.alignment = WD_TABLE_ALIGNMENT.CENTER
        t2.style     = "Light Grid Accent 2"
        hc2 = t2.rows[0].cells
        for i, h in enumerate(headers2):
            hc2[i].text = h
            hc2[i].paragraphs[0].runs[0].font.bold = True
        for _, row in dec_df.head(10).iterrows():
            cells = t2.add_row().cells
            cells[0].text = str(row["id"])[:12]
            cells[1].text = row["zona_id"]
            cells[2].text = f"{row['dosis_mm']:.2f}"
            cells[3].text = f"{row['confianza']*100:.1f}%"
            cells[4].text = row["estado"]
            cells[5].text = str(row["timestamp"])[:16]
    else:
        doc.add_paragraph("No hay decisiones RL registradas aún.")

    # 4. Ejecuciones
    doc.add_heading("4. Historial de Ejecuciones de Riego", level=1)
    ej_df = db.get_ejecuciones(limit=10)
    if not ej_df.empty:
        headers3 = ["Zona", "Dosis (mm)", "Volumen (m³)", "Tipo", "Ejecutado por", "Fecha"]
        t3       = doc.add_table(rows=1, cols=len(headers3))
        t3.style = "Light Grid Accent 3"
        hc3 = t3.rows[0].cells
        for i, h in enumerate(headers3):
            hc3[i].text = h
            hc3[i].paragraphs[0].runs[0].font.bold = True
        for _, row in ej_df.iterrows():
            cells = t3.add_row().cells
            cells[0].text = row["zona_id"]
            cells[1].text = f"{row['dosis_mm']:.2f}"
            cells[2].text = f"{row['volumen_m3']:.3f}"
            cells[3].text = row["tipo"]
            cells[4].text = str(row["ejecutado_por"])
            cells[5].text = str(row["timestamp"])[:16]
    else:
        doc.add_paragraph("No hay ejecuciones registradas aún.")

    # 5. Conclusiones
    doc.add_heading("5. Conclusiones y Recomendaciones", level=1)
    conclusiones = [
        "Zona NE presenta el mayor estrés hídrico (CWSI=0.61) — priorizar riego.",
        "El agente PPO opera con confianza promedio superior al 90%.",
        "Se recomienda mantener humedad de 10cm sobre 27% para evitar marchitez.",
        "Programar reentrenamiento del modelo con los últimos 30 días de feedback.",
        "Revisar calibración de sensores de temperatura en Zona SW.",
    ]
    for c in conclusiones:
        doc.add_paragraph(c, style="List Number")

    doc.add_paragraph("")
    doc.add_paragraph(
        "VRI Digital Twin — Generado automáticamente. "
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ── Excel con openpyxl ────────────────────────────────────────────────────────

def generar_excel(usuario: str = "Sistema") -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.chart import BarChart, Reference

    wb = Workbook()

    # Helpers de estilo (patrón del minero)
    hdr_font  = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    hdr_fill_green  = PatternFill(start_color="15803d", end_color="15803d", fill_type="solid")
    hdr_fill_blue   = PatternFill(start_color="1e40af", end_color="1e40af", fill_type="solid")
    hdr_fill_purple = PatternFill(start_color="7c3aed", end_color="7c3aed", fill_type="solid")
    hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin      = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"),  bottom=Side(style="thin"),
    )

    def apply_header(ws, ncols, fill):
        for col in range(1, ncols + 1):
            cell = ws.cell(row=1, column=col)
            cell.font      = hdr_font
            cell.fill      = fill
            cell.alignment = hdr_align
            cell.border    = thin

    def auto_width(ws):
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=0)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    # ── Hoja 1: Zonas ──────────────────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "Zonas"
    zonas_df  = db.get_zonas()
    for r in dataframe_to_rows(zonas_df, index=False, header=True):
        ws1.append(r)
    apply_header(ws1, len(zonas_df.columns), hdr_fill_green)
    auto_width(ws1)

    # Gráfico de barras CWSI
    chart = BarChart()
    chart.title = "CWSI por Zona"
    chart.y_axis.title = "CWSI"
    chart.x_axis.title = "Zona"
    data   = Reference(ws1, min_col=11, min_row=1, max_row=len(zonas_df)+1)
    cats   = Reference(ws1, min_col=3,  min_row=2, max_row=len(zonas_df)+1)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 10
    chart.width  = 18
    ws1.add_chart(chart, "N2")

    # ── Hoja 2: Lecturas sensores ──────────────────────────────────────────────
    ws2       = wb.create_sheet("Lecturas_Sensores")
    lect_df   = db.get_lecturas(limit=200)
    for r in dataframe_to_rows(lect_df, index=False, header=True):
        ws2.append(r)
    apply_header(ws2, len(lect_df.columns), hdr_fill_blue)
    auto_width(ws2)

    # ── Hoja 3: Decisiones RL ─────────────────────────────────────────────────
    ws3    = wb.create_sheet("Decisiones_RL")
    dec_df = db.get_decisiones()
    if not dec_df.empty:
        for r in dataframe_to_rows(dec_df, index=False, header=True):
            ws3.append(r)
        apply_header(ws3, len(dec_df.columns), hdr_fill_purple)
        auto_width(ws3)
    else:
        ws3.append(["Sin decisiones registradas"])

    # ── Hoja 4: Ejecuciones ───────────────────────────────────────────────────
    ws4   = wb.create_sheet("Ejecuciones_Riego")
    ej_df = db.get_ejecuciones(limit=100)
    if not ej_df.empty:
        for r in dataframe_to_rows(ej_df, index=False, header=True):
            ws4.append(r)
        hdr_fill_cyan = PatternFill(start_color="0369a1", end_color="0369a1", fill_type="solid")
        apply_header(ws4, len(ej_df.columns), hdr_fill_cyan)
        auto_width(ws4)
    else:
        ws4.append(["Sin ejecuciones registradas"])

    # ── Hoja 5: Resumen KPIs ──────────────────────────────────────────────────
    ws5 = wb.create_sheet("KPIs")
    ws5.append(["KPI", "Valor"])
    kpis = [
        ["Fecha del reporte", datetime.now().strftime("%d/%m/%Y %H:%M")],
        ["Generado por", usuario],
        ["Zonas monitoreadas", len(zonas_df)],
        ["Lecturas totales", len(lect_df)],
        ["Decisiones RL registradas", len(dec_df)],
        ["Ejecuciones de riego", len(ej_df)],
        ["CWSI promedio", f"{zonas_df['cwsi'].mean():.3f}" if not zonas_df.empty else "N/A"],
        ["Humedad 10cm promedio (%)", f"{zonas_df['humedad10'].mean():.2f}" if not zonas_df.empty else "N/A"],
    ]
    for k in kpis:
        ws5.append(k)
    apply_header(ws5, 2, hdr_fill_green)
    auto_width(ws5)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
