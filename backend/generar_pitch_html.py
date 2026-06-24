"""
Genera docs/pitch_deck.html desde docs/pitch_deck.md.
Ábrelo en Chrome y presiona Ctrl+P -> Guardar como PDF.
"""
import re
from pathlib import Path

MD_PATH   = Path(__file__).parent.parent / "docs" / "pitch_deck.md"
HTML_PATH = Path(__file__).parent.parent / "docs" / "pitch_deck.html"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    color: #1a1a1a;
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 32px;
    line-height: 1.55;
}
h1 {
    background: #00509F;
    color: white;
    font-size: 26pt;
    padding: 20px 28px;
    margin: 0 -32px 24px;
    text-align: center;
    letter-spacing: 1px;
}
.subtitle {
    text-align: center;
    font-size: 11pt;
    color: #555;
    margin-top: -16px;
    margin-bottom: 24px;
}
h2 {
    background: #00509F;
    color: white;
    font-size: 12pt;
    padding: 7px 12px;
    margin: 20px 0 10px;
    border-radius: 3px;
}
h3 {
    color: #00509F;
    font-size: 11pt;
    margin: 12px 0 6px;
    border-bottom: 1px solid #c8d8f0;
    padding-bottom: 3px;
}
p { margin: 6px 0; }
ul, ol { padding-left: 20px; margin: 6px 0; }
li { margin: 3px 0; }
blockquote {
    background: #f0f5fc;
    border-left: 4px solid #00509F;
    padding: 8px 14px;
    margin: 10px 0;
    font-style: italic;
    color: #334;
    border-radius: 2px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 10pt;
}
th {
    background: #00509F;
    color: white;
    padding: 7px 10px;
    text-align: left;
    font-weight: 600;
}
td {
    padding: 6px 10px;
    border-bottom: 1px solid #dde8f5;
    vertical-align: top;
}
tr:nth-child(even) td { background: #f4f8ff; }
code {
    background: #f0f3f8;
    font-family: 'Consolas', monospace;
    font-size: 9pt;
    padding: 1px 4px;
    border-radius: 3px;
}
pre {
    background: #f0f3f8;
    border: 1px solid #d0d8e8;
    padding: 10px 14px;
    font-family: 'Consolas', monospace;
    font-size: 8.5pt;
    border-radius: 4px;
    overflow-x: auto;
    margin: 8px 0;
    white-space: pre-wrap;
}
hr {
    border: none;
    border-top: 1px solid #d0dcea;
    margin: 16px 0;
}
strong { color: #00509F; }
.meta {
    text-align: center;
    color: #666;
    font-size: 9.5pt;
    margin-top: 32px;
    padding-top: 12px;
    border-top: 1px solid #dde;
}
@media print {
    body { padding: 0; max-width: 100%; }
    h1 { margin: 0 0 18px; }
    h2 { page-break-after: avoid; }
    table, blockquote { page-break-inside: avoid; }
}
"""

def md_to_html(md: str) -> str:
    lines = md.splitlines()
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Bloque de código
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(escape(lines[i]))
                i += 1
            html_parts.append(f'<pre><code>{chr(10).join(code_lines)}</code></pre>')
            i += 1
            continue

        # Tabla markdown
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            html_parts.append(render_table(table_lines))
            continue

        # H1
        if line.startswith("# "):
            text = inline(line[2:])
            html_parts.append(f'<h1>{text}</h1>')

        # H2
        elif line.startswith("## "):
            text = inline(line[3:])
            html_parts.append(f'<h2>{text}</h2>')

        # H3
        elif line.startswith("### "):
            text = inline(line[4:])
            html_parts.append(f'<h3>{text}</h3>')

        # HR
        elif line.strip() == "---":
            html_parts.append("<hr>")

        # Blockquote
        elif line.startswith("> "):
            text = inline(line[2:])
            html_parts.append(f'<blockquote>{text}</blockquote>')

        # Lista sin orden
        elif line.startswith("- ") or line.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                items.append(f'<li>{inline(lines[i][2:])}</li>')
                i += 1
            html_parts.append("<ul>" + "".join(items) + "</ul>")
            continue

        # Lista numerada
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(f'<li>{inline(re.sub(r"^\d+\. ", "", lines[i]))}</li>')
                i += 1
            html_parts.append("<ol>" + "".join(items) + "</ol>")
            continue

        # Línea vacía
        elif line.strip() == "":
            html_parts.append("")

        # Párrafo
        else:
            html_parts.append(f'<p>{inline(line)}</p>')

        i += 1

    return "\n".join(html_parts)


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*",     r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`",       r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', text)
    return text

def render_table(table_lines: list) -> str:
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return ""

    # Detectar fila separadora (---|---|---)
    def is_separator(row):
        return all(re.match(r"^[-:]+$", c) for c in row if c)

    header = rows[0]
    data_rows = [r for r in rows[1:] if not is_separator(r)]

    thead = "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>"
    tbody = ""
    for row in data_rows:
        # Rellenar si la fila tiene menos columnas
        while len(row) < len(header):
            row.append("")
        tbody += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"

    return f"<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>"


def main():
    md = MD_PATH.read_text(encoding="utf-8")
    body = md_to_html(md)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MediRuta — Dossier YC-Style</title>
<style>{CSS}</style>
</head>
<body>
{body}
<div class="meta">
  Data Science con Python 2026-I &nbsp;·&nbsp; Universidad del Pacífico<br>
  Docente: Alexander Quispe &nbsp;·&nbsp; Evelyn Valeria Sarmiento Vasquez
</div>
</body>
</html>"""

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"OK - {HTML_PATH}")
    print("Abre en Chrome y usa Ctrl+P -> Guardar como PDF")


if __name__ == "__main__":
    main()
