from fpdf import FPDF
from typing import Any, Dict
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Title on left (accent color) and timestamp on right
        self.set_font('Arial', 'B', 14)
        self.set_text_color(33, 150, 243)  # blue
        self.cell(0, 10, 'Medical Analysis Report', 0, 0, 'L')
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 9)
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.cell(0, 10, now, 0, 1, 'R')
        # Divider line
        self.set_draw_color(220, 220, 220)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(2)

    def chapter_title(self, title):
        # Section title with light background
        self.set_fill_color(245, 247, 250)
        self.set_draw_color(220, 220, 220)
        self.set_text_color(33, 33, 33)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, title, 0, 1, 'L', fill=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(self._content_width(), 5, body)
        self.ln()

    def _safe_string(self, value: Any, max_token_len: int = 60) -> str:
        # Convert any value to a printable string
        s = "" if value is None else str(value)
        # Break very long tokens (no spaces) to avoid FPDF width errors
        parts = []
        for token in s.split():
            if len(token) > max_token_len:
                # chunk the long token
                chunks = [token[i:i+max_token_len] for i in range(0, len(token), max_token_len)]
                parts.append(" ".join(chunks))
            else:
                parts.append(token)
        # Preserve original spacing when possible
        if parts:
            return " ".join(parts)
        # If string had no spaces, split by fixed width
        if len(s) > max_token_len:
            return " ".join([s[i:i+max_token_len] for i in range(0, len(s), max_token_len)])
        return s

    def _content_width(self) -> float:
        # Effective page width (guard against extreme margins)
        width = self.w - self.l_margin - self.r_margin
        # Ensure a minimum width to avoid FPDF errors
        return max(width, 10)

    def _force_chunk(self, s: str, size: int = 30) -> str:
        if not s:
            return s
        return " ".join([s[i:i+size] for i in range(0, len(s), size)])

    def _multi_cell_safe(self, w: float, h: float, txt: str):
        try:
            self.multi_cell(max(w, 10), h, txt)
        except Exception:
            # Retry with smaller font
            current_family = self.font_family
            current_style = self.font_style
            current_size_pt = self.font_size_pt
            try:
                self.set_font(current_family or 'Arial', current_style, max(current_size_pt - 2, 6))
                self.multi_cell(max(w, 10), h, txt)
            except Exception:
                # Force chunk the text to add breakpoints
                safe_txt = self._force_chunk(txt, 20)
                self.set_font(current_family or 'Arial', current_style, max(current_size_pt - 2, 6))
                self.multi_cell(max(w, 10), h, safe_txt)

    def _label_value_row(self, label: str, value: str):
        # Render a two-column label/value row
        label_w = min(45, self._content_width() * 0.35)
        value_w = self._content_width() - label_w
        self.set_font('Arial', 'B', 10)
        self.set_text_color(90, 90, 90)
        self.cell(label_w, 6, self._safe_string(label), 0, 0)
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        # Use multi-cell for values to wrap
        x, y = self.get_x(), self.get_y()
        self._multi_cell_safe(value_w, 6, self._safe_string(value))
        # If multi_cell advanced to next line, ensure label row height matches
        self.ln(1)

    def add_patient_info(self, patient_info: Dict[str, Any]):
        # Render patient info as a small table section
        self.chapter_title('Patient Information')
        ordered_keys = ['patientId', 'age', 'gender', 'medicalHistory', 'currentMedications', 'urgency']
        labels = {
            'patientId': 'Patient ID',
            'age': 'Age',
            'gender': 'Gender',
            'medicalHistory': 'Medical History',
            'currentMedications': 'Current Medications',
            'urgency': 'Urgency'
        }
        for key in ordered_keys:
            if key in patient_info and patient_info[key] not in (None, ''):
                self._label_value_row(labels[key], str(patient_info[key]))
        self.ln(3)

    def add_analysis_section(self, title, data):
        self.chapter_title(title)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.set_font('Arial', 'B', 10)
                    self.cell(0, 5, f"{key}:")
                    self.ln()
                    self.set_font('Arial', '', 10)
                    for item in value:
                        if isinstance(item, dict):
                            item_str = ', '.join([f"{k}: {self._safe_string(v)}" for k, v in item.items()])
                            self._multi_cell_safe(self._content_width(), 5, f"  - {self._safe_string(item_str)}")
                        else:
                            self._multi_cell_safe(self._content_width(), 5, f"  - {self._safe_string(item)}")
                else:
                    self.set_font('Arial', 'B', 10)
                    self.cell(0, 5, f"{key}:")
                    self.ln()
                    self.set_font('Arial', '', 10)
                    self._multi_cell_safe(self._content_width(), 5, self._safe_string(value))
                self.ln(2)
        elif isinstance(data, str):
            self.chapter_body(self._safe_string(data))
        self.ln(5)

    def footer(self):
        # Page number
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, 'C')
        self.set_text_color(0, 0, 0)


def generate_pdf_from_analysis(analysis_data: dict) -> bytes:
    pdf = PDF()
    pdf.add_page()
    pdf.alias_nb_pages()

    # Optional patient info section
    patient_info = analysis_data.get('patient_info') or {}
    if isinstance(patient_info, dict) and patient_info:
        pdf.add_patient_info(patient_info)

    if 'symptom_analysis' in analysis_data:
        pdf.add_analysis_section('Symptom Analysis', analysis_data['symptom_analysis'])
    
    if 'literature' in analysis_data:
        pdf.add_analysis_section('Literature Review', analysis_data['literature'])

    if 'case_matcher' in analysis_data:
        pdf.add_analysis_section('Case Matching Results', analysis_data['case_matcher'])

    if 'treatment' in analysis_data:
        pdf.add_analysis_section('Treatment Suggestions', analysis_data['treatment'])

    if 'summary' in analysis_data:
        pdf.add_analysis_section('Final Summary', analysis_data['summary'])

    out = pdf.output(dest='S')
    # fpdf2 may return str, bytes, or bytearray depending on version
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return out.encode('latin-1')

