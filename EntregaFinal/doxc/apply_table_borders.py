import os
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DOCX_PATH = r"C:\MisProyectos\ECCI\trasncriptor maestro\EntregaFinal\doxc\DOCUMENTO_FINAL_PROYECTO.docx"

def style_document(docx_path=None, output_path=None):
    if docx_path is None:
        docx_path = DOCX_PATH
    if output_path is None:
        output_path = docx_path

    doc = docx.Document(docx_path)
    total_tables = len(doc.tables)
    print(f"Total tables found: {total_tables}")

    # Forzar negrilla en todos los estilos de títulos y subtítulos del documento
    for s in doc.styles:
        if s.name and (s.name.startswith("Heading") or s.name in ["Title", "Subtitle"]):
            if hasattr(s, 'font'):
                s.font.bold = True

    # 1. Aplicar estilo riguroso a todas las tablas (bordes negros, padding, encabezados, cantSplit)
    for idx, table in enumerate(doc.tables):
        tblPr = table._tbl.tblPr

        # Quitar bordes previos
        existing_borders = tblPr.find(qn('w:tblBorders'))
        if existing_borders is not None:
            tblPr.remove(existing_borders)

        # Bordes negros sólidos (sz=8 es 1pt exterior, sz=6 es 0.75pt interior)
        tbl_borders_xml = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'  <w:left w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'  <w:right w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
            f'  <w:insideH w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:insideV w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'</w:tblBorders>'
        )
        tblPr.append(tbl_borders_xml)

        # Margen/padding interno de celdas (120 dxa = 6pt top/bottom, 160 dxa = 8pt left/right)
        existing_mar = tblPr.find(qn('w:tblCellMar'))
        if existing_mar is not None:
            tblPr.remove(existing_mar)

        cell_mar_xml = parse_xml(
            f'<w:tblCellMar {nsdecls("w")}>\n'
            f'  <w:top w:w="120" w:type="dxa"/>\n'
            f'  <w:left w:w="160" w:type="dxa"/>\n'
            f'  <w:bottom w:w="120" w:type="dxa"/>\n'
            f'  <w:right w:w="160" w:type="dxa"/>\n'
            f'</w:tblCellMar>'
        )
        tblPr.append(cell_mar_xml)

        # Centrado horizontal de la tabla
        existing_jc = tblPr.find(qn('w:jc'))
        if existing_jc is not None:
            tblPr.remove(existing_jc)
        jc_xml = parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>')
        tblPr.append(jc_xml)

        # Iterar filas y celdas
        for r_idx, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()

            # Evitar corte de fila entre páginas
            if trPr.find(qn('w:cantSplit')) is None:
                cant_split = parse_xml(f'<w:cantSplit {nsdecls("w")}/>')
                trPr.append(cant_split)

            # Repetir encabezado en cada página
            if r_idx == 0:
                if trPr.find(qn('w:tblHeader')) is None:
                    tbl_header = parse_xml(f'<w:tblHeader {nsdecls("w")}/>')
                    trPr.append(tbl_header)

            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()

                # Eliminar bordes individuales residuales blancos o nulos
                existing_tc_borders = tcPr.find(qn('w:tcBorders'))
                if existing_tc_borders is not None:
                    tcPr.remove(existing_tc_borders)

                # Sombreado gris claro (#EAEAEA) en encabezado
                if r_idx == 0:
                    existing_shd = tcPr.find(qn('w:shd'))
                    if existing_shd is not None:
                        tcPr.remove(existing_shd)
                    header_shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="EAEAEA"/>')
                    tcPr.append(header_shd)

    # 2. Recorrer la jerarquía de elementos del cuerpo para dar espaciado perfecto a párrafos, tablas y figuras
    body_elements = []
    for child in doc.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            body_elements.append(('p', Paragraph(child, doc)))
        elif tag == 'tbl':
            body_elements.append(('tbl', Table(child, doc)))

    # Identificar índices especiales
    table_prev_paras = set()
    table_next_paras = set()

    for i, (el_type, el) in enumerate(body_elements):
        if el_type == 'tbl':
            if i > 0 and body_elements[i-1][0] == 'p':
                table_prev_paras.add(body_elements[i-1][1])
            if i + 1 < len(body_elements) and body_elements[i+1][0] == 'p':
                table_next_paras.add(body_elements[i+1][1])

    # 3. Aplicar espaciados tipográficos y forzar negrilla en todos los títulos y subtítulos
    figure_count = 0
    table_title_count = 0
    note_count = 0
    list_count = 0
    heading_count = 0

    for el_type, p in [be for be in body_elements if be[0] == 'p']:
        text = p.text.strip()
        style_name = p.style.name if p.style else ""
        has_drawing = bool(p._p.xpath('.//w:drawing'))
        has_num = bool(p._p.xpath('.//w:numPr'))
        is_heading_style = style_name.startswith("Heading") or style_name in ["Title", "Subtitle"] or bool(p._p.xpath('.//w:pPr/w:outlineLvl'))

        # A) Detección y formato riguroso de títulos y subtítulos en negrilla
        if is_heading_style:
            heading_count += 1
            for run in p.runs:
                run.bold = True
            p.paragraph_format.keep_with_next = True
            if style_name == "Heading 1" or style_name == "Title":
                p.paragraph_format.space_before = Pt(18)
                p.paragraph_format.space_after = Pt(8)
            elif style_name == "Heading 2":
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(6)
            else:
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
            continue

        # B) Párrafo con dibujo/imagen de figura
        if has_drawing:
            figure_count += 1
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            continue

        # C) Párrafo de leyenda de figura (Figura X. ...)
        if text.startswith("Figura "):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(16)
            continue

        # D) Título de tabla (inmediatamente antes de una tabla o empieza por Tabla X)
        if p in table_prev_paras or text.startswith("Tabla "):
            table_title_count += 1
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            continue

        # E) Párrafo inmediatamente posterior a una tabla
        if p in table_next_paras:
            if text.startswith("Nota.") or text.startswith("Fuente:"):
                note_count += 1
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(16)
            else:
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
            continue

        # F) Párrafos de notas huérfanas si las hubiera
        if text.startswith("Nota."):
            note_count += 1
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(16)
            continue

        # G) Elementos de lista (viñetas y numeraciones)
        if has_num:
            list_count += 1
            p.paragraph_format.space_after = Pt(3)
            continue

        # H) Párrafos regulares de texto para que no queden pegados entre sí
        if p.paragraph_format.space_after is None or p.paragraph_format.space_after.pt < 4:
            p.paragraph_format.space_after = Pt(6)

    print(f"Titulos y subtitulos formateados en negrilla: {heading_count}")
    print(f"Figuras formateadas con espaciado editorial: {figure_count}")
    print(f"Titulos de tablas espaciados: {table_title_count}")
    print(f"Notas de tablas espaciadas: {note_count}")
    print(f"Elementos de lista formateados: {list_count}")

    # Guardar en archivo
    try:
        doc.save(output_path)
        print(f"Guardado exitosamente en: {output_path}")
    except PermissionError:
        alt_path = output_path.replace(".docx", "_nuevo.docx")
        doc.save(alt_path)
        print(f"ADVERTENCIA: Archivo bloqueado por Word. Guardado en ruta alternativa: {alt_path}")

if __name__ == "__main__":
    style_document(DOCX_PATH)
