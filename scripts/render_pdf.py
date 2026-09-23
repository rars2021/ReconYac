#!/usr/bin/env python3
"""Renderiza las paginas de un PDF a PNG (para lectura visual) y, si el PDF es
nativo-digital, extrae tambien el texto de cada pagina.

Uso:
    python scripts/render_pdf.py <pdf> [--pages 1-10] [--dpi 170] [--out DIR]

Salida (por defecto en un dir temporal de trabajo, NO en el repo):
    <out>/<stem>/p001.png, p002.png, ...
    <out>/<stem>/text.jsonl   (una linea por pagina: {"page":N,"text":"..."})
"""
import argparse
import json
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Falta PyMuPDF. Instala con: pip install pymupdf")


def parse_pages(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [p for p in out if 1 <= p <= n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages", default="")
    ap.add_argument("--dpi", type=int, default=170)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    stem = os.path.splitext(os.path.basename(args.pdf))[0]
    out_base = args.out or os.environ.get(
        "RENDER_OUT",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_work"),
    )
    out_dir = os.path.join(out_base, stem)
    os.makedirs(out_dir, exist_ok=True)

    pages = parse_pages(args.pages, doc.page_count)
    zoom = args.dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    text_path = os.path.join(out_dir, "text.jsonl")
    with open(text_path, "w", encoding="utf-8") as tf:
        for p in pages:
            page = doc[p - 1]
            pix = page.get_pixmap(matrix=mat)
            png = os.path.join(out_dir, f"p{p:03d}.png")
            pix.save(png)
            txt = page.get_text().strip()
            tf.write(json.dumps({"page": p, "text": txt}, ensure_ascii=False) + "\n")
            print(f"p{p:03d}  {pix.width}x{pix.height}  text_chars={len(txt)}  -> {png}")

    print(f"\nOK: {len(pages)} paginas -> {out_dir}")
    print(f"Texto por pagina: {text_path}")


if __name__ == "__main__":
    main()
