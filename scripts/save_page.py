#!/usr/bin/env python3
"""Guarda la imagen canonica de una muestra: db/samples/<CODIGO>/page.jpg

Uso:
    python scripts/save_page.py <pdf> <pagina> <CODIGO> [--dpi 130] [--quality 75]

Nota: para LEER las paginas (renderizado de alta resolucion a un dir temporal)
usar scripts/render_pdf.py; este script guarda la version liviana para el repo.
"""
import argparse
import os
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("Falta PyMuPDF. Instala con: pip install pymupdf")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("pagina", type=int)
    ap.add_argument("codigo")
    ap.add_argument("--dpi", type=int, default=130)
    ap.add_argument("--quality", type=int, default=75)
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)
    zoom = args.dpi / 72.0
    pix = doc[args.pagina - 1].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    out_dir = os.path.join(ROOT, "db", "samples", args.codigo)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "page.jpg")
    pix.save(out, jpg_quality=args.quality)
    print(f"{out}  {os.path.getsize(out)//1024} KB  {pix.width}x{pix.height}")


if __name__ == "__main__":
    main()
