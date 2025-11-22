from fpdf import FPDF
import tempfile
from datetime import datetime
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Technischer Versuchsbericht', 0, 1, 'L')
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')

def create_project_pdf(project):
    # ... (Alter Projekt Code bleibt gleich, nur verkürzt dargestellt) ...
    pdf = PDFReport(); pdf.add_page(); pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, project['title'], 0, 1); pdf.output(tempfile.mktemp(suffix=".pdf"))
    return None # Platzhalter, da Fokus auf Labor liegt

def create_lab_report_pdf(exp):
    pdf = PDFReport()
    pdf.add_page()
    
    # --- KOPFDATEN ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 8, "Versuch:", 0, 0); pdf.set_font('Arial', '', 12); pdf.cell(0, 8, exp['name'], 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 8, "Datum:", 0, 0); pdf.set_font('Arial', '', 12); pdf.cell(0, 8, datetime.now().strftime("%d.%m.%Y"), 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 8, "Prüfer:", 0, 0); pdf.set_font('Arial', '', 12); pdf.cell(0, 8, exp.get('tester', 'N/A'), 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 8, "Gesamturteil:", 0, 0)
    
    urteil = exp.get('conclusion', 'Offen')
    if "Freigabe" in urteil: pdf.set_text_color(0, 150, 0)
    elif "Keine" in urteil: pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 8, urteil, 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(5)
    
    # --- 1. ZIELSETZUNG ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "1. Aufgabenstellung & Parameter", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, exp['description'])
    pdf.ln(5)
    
    # --- 2. ERGEBNISSE (MATRIX) ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "2. Testergebnisse", 0, 1)
    
    if exp.get('matrix_data') and exp.get('matrix_columns'):
        cols = exp['matrix_columns']
        # Table Header
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 230, 230)
        
        # Calculate width
        name_width = 45
        # Avoid division by zero
        col_count = len(cols) if len(cols) > 0 else 1
        data_width = (190 - name_width) / col_count
        
        pdf.cell(name_width, 8, "Probe / Muster", 1, 0, 'L', 1)
        for c in cols:
            pdf.cell(data_width, 8, c[:15], 1, 0, 'C', 1)
        pdf.ln()
        
        # Table Body
        pdf.set_font('Arial', '', 9)
        for row in exp['matrix_data']:
            pdf.cell(name_width, 8, row['sample_name'][:25], 1)
            for c in cols:
                val = str(row.get(c, '-'))
                if val in ["n.i.O.", "Fail", "V", "R", "DURCHGEFALLEN"]: pdf.set_text_color(200, 0, 0)
                elif val in ["i.O.", "Pass", "Bestanden"]: pdf.set_text_color(0, 150, 0)
                
                pdf.cell(data_width, 8, val[:20], 1, 0, 'C')
                pdf.set_text_color(0, 0, 0)
            pdf.ln()
    else:
        pdf.set_font('Arial', 'I', 11)
        pdf.cell(0, 10, "Keine Messdaten vorhanden.", 0, 1)
        
    pdf.ln(5)

    # --- 3. FAZIT ---
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "3. Zusammenfassung", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, exp.get('result_summary', ''))
    pdf.ln(5)
    
    # --- 4. BILDER ---
    if exp.get('images'):
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, "4. Bilddokumentation", 0, 1)
        
        y_pos = 40
        for img in exp['images']:
            if os.path.exists(img['path']):
                if y_pos > 200: 
                    pdf.add_page(); y_pos = 20
                
                try:
                    pdf.image(img['path'], x=10, y=y_pos, w=100)
                    pdf.set_xy(115, y_pos)
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 5, f"Bild: {img['caption']}")
                    y_pos += 80
                except: pass

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        pdf.output(temp_file.name)
        return temp_file.name
    except: return None