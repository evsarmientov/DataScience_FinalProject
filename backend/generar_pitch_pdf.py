"""
Genera docs/pitch_deck.pdf a partir de docs/pitch_deck.md usando fpdf2.
"""
import re
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

MD_PATH   = Path(__file__).parent.parent / "docs" / "pitch_deck.md"
PDF_PATH  = Path(__file__).parent.parent / "docs" / "pitch_deck.pdf"
FONT_DIR  = Path("C:/Windows/Fonts")

BLUE   = (0, 80, 160)
RED    = (200, 40, 40)
LIGHT  = (240, 245, 252)
DARK   = (25, 25, 25)
GRAY   = (100, 100, 100)

L_MARGIN = 14
R_MARGIN = 14
PAGE_W   = 210
CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN  # 182 mm


def clean(text: str) -> str:
    """Quita marcas inline de Markdown."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"`(.+?)`",       r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]*\)", r"\1", text)
    text = text.replace("—", " - ").replace("–", "-")
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    return text.strip()


class PDF(FPDF):
    def header(self):
        self.set_fill_color(*BLUE)
        self.rect(0, 0, PAGE_W, 5, "F")

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6,
                  f"MediRuta - Dossier YC-Style  |  Data Science con Python 2026-I  |  Pagina {self.page_no()}",
                  align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def cover(self):
        self.add_page()
        # fondo
        self.set_fill_color(*LIGHT)
        self.rect(0, 5, PAGE_W, 287, "F")
        # franja azul
        self.set_fill_color(*BLUE)
        self.rect(0, 78, PAGE_W, 60, "F")
        # título
        self.set_xy(L_MARGIN, 88)
        self.set_font("Arial", "B", 34)
        self.set_text_color(255, 255, 255)
        self.cell(CONTENT_W, 14, "MediRuta", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Arial", "", 13)
        self.set_x(L_MARGIN)
        self.multi_cell(CONTENT_W, 7,
            "Le dice al paciente oncologico exactamente a que modulo del INEN ir,\n"
            "que documentos llevar y que estudios tener listos antes de salir de casa.",
            align="C")
        # metadata
        self.set_xy(L_MARGIN, 160)
        self.set_font("Arial", "", 11)
        self.set_text_color(*DARK)
        for line in [
            "Evelyn Valeria Sarmiento Vasquez",
            "ev.sarmientov@alum.up.edu.pe",
            "Data Science con Python 2026-I - Universidad del Pacifico",
            "Docente: Alexander Quispe",
            "",
            "App en vivo: mediruta.streamlit.app",
            "Repo: github.com/evsarmientov/DataScience_FinalProject",
        ]:
            self.set_x(L_MARGIN)
            self.cell(CONTENT_W, 8, line, align="C",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section(self, title: str):
        if self.get_y() > 245:
            self.add_page()
        self.ln(3)
        self.set_fill_color(*BLUE)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 12)
        self.set_x(L_MARGIN)
        self.cell(CONTENT_W, 8, f"  {title}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*DARK)
        self.ln(2)

    def h3(self, title: str):
        self.set_font("Arial", "B", 10)
        self.set_text_color(*BLUE)
        self.set_x(L_MARGIN)
        self.cell(CONTENT_W, 6, title,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*DARK)

    def body(self, text: str):
        self.set_font("Arial", "", 10)
        self.set_text_color(*DARK)
        self.set_x(L_MARGIN)
        self.multi_cell(CONTENT_W, 6, text)
        self.ln(1)

    def bullet(self, text: str):
        self.set_font("Arial", "", 10)
        self.set_text_color(*DARK)
        self.set_x(L_MARGIN + 3)
        self.cell(5, 6, "-", new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.multi_cell(CONTENT_W - 8, 6, text)

    def quote_block(self, text: str):
        self.set_fill_color(*LIGHT)
        self.set_font("Arial", "I", 10)
        self.set_text_color(60, 60, 120)
        self.set_x(L_MARGIN + 4)
        self.multi_cell(CONTENT_W - 4, 6, f'  "{text}"', fill=True)
        self.set_text_color(*DARK)
        self.ln(1)

    def table_row(self, cells):
        self.set_font("Arial", "", 9)
        self.set_text_color(*DARK)
        self.set_x(L_MARGIN)
        self.multi_cell(CONTENT_W, 5, "  |  ".join(cells))


def add_fonts(pdf: PDF):
    pdf.add_font("Arial",  "",   str(FONT_DIR / "arial.ttf"))
    pdf.add_font("Arial",  "B",  str(FONT_DIR / "arialbd.ttf"))
    pdf.add_font("Arial",  "I",  str(FONT_DIR / "ariali.ttf"))
    pdf.add_font("Arial",  "BI", str(FONT_DIR / "arialbi.ttf"))


def build(pdf: PDF):
    add_fonts(pdf)
    pdf.cover()
    pdf.add_page()

    lines = MD_PATH.read_text(encoding="utf-8").splitlines()
    i = 0
    in_code = False

    while i < len(lines):
        raw  = lines[i]
        line = clean(raw)
        i += 1

        if not line or line == "---":
            continue

        if raw.startswith("# "):        # H1 — skip (portada ya la tiene)
            continue

        if raw.startswith("## "):
            pdf.section(clean(raw[3:]))

        elif raw.startswith("### "):
            pdf.h3(clean(raw[4:]))

        elif raw.startswith("> "):
            pdf.quote_block(clean(raw[2:]))

        elif raw.startswith("- ") or raw.startswith("* "):
            pdf.bullet(clean(raw[2:]))

        elif re.match(r"^\d+\. ", raw):
            pdf.bullet(clean(re.sub(r"^\d+\. ", "", raw)))

        elif raw.startswith("|"):
            cells = [clean(c) for c in raw.strip("|").split("|")]
            cells = [c for c in cells if c and not re.match(r"^[-:]+$", c)]
            if cells:
                pdf.table_row(cells)

        elif raw.startswith("```"):
            while i < len(lines) and not lines[i].startswith("```"):
                code = lines[i].rstrip()
                # eliminar caracteres Unicode de box-drawing y flechas
                code = re.sub(r"[^\x00-\x7F]+", " ", code)
                if code.strip():
                    pdf.set_font("Arial", "", 8)
                    pdf.set_text_color(40, 40, 40)
                    pdf.set_x(L_MARGIN + 4)
                    pdf.multi_cell(CONTENT_W - 4, 5, code)
                    pdf.set_text_color(*DARK)
                i += 1
            i += 1  # saltar ```

        elif raw.startswith("**") and raw.rstrip().endswith("**"):
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(*BLUE)
            pdf.set_x(L_MARGIN)
            pdf.cell(CONTENT_W, 6, line,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(*DARK)

        elif line:
            pdf.body(line)


def main():
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(L_MARGIN, 14, R_MARGIN)
    build(pdf)
    pdf.output(str(PDF_PATH))
    size_kb = PDF_PATH.stat().st_size // 1024
    print(f"OK - {PDF_PATH.name}  ({size_kb} KB, {pdf.page} paginas)")


if __name__ == "__main__":
    main()
