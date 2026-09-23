#!/usr/bin/env python3
"""Regenera db/index.json y db/catalog.md a partir de los db/samples/*/record.json.

Uso:
    python scripts/build_index.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_DIR = os.path.join(ROOT, "db", "samples")
INDEX_PATH = os.path.join(ROOT, "db", "index.json")
CATALOG_PATH = os.path.join(ROOT, "db", "catalog.md")


def minerals(rows):
    return [r.get("mineral", "").strip() for r in (rows or []) if r.get("mineral", "").strip()]


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join((c or "").replace("\n", " ") for c in r) + " |")
    return "\n".join(out)


def render_record_md(rec):
    interp = rec.get("interpretacion", {}) or {}
    esq = rec.get("esquema", {}) or {}
    seq = rec.get("secuencia_paragenetica", {}) or {}
    L = []
    L.append(f"# Muestra {rec.get('codigo','(sin codigo)')}")
    L.append("")
    L.append(f"- **Autor:** {rec.get('autor','')}")
    if rec.get("formato"):
        L.append(f"- **Formato:** {rec['formato']}")
    L.append(f"- **Fuente:** {rec.get('fuente_pdf','')} (pagina {rec.get('pagina','')})")
    if rec.get("confianza"):
        L.append(f"- **Confianza transcripcion:** {rec['confianza']}")
    L.append("")
    L.append("![pagina](page.jpg)")
    L.append("")
    L.append("## 1. Mineralogia y Texturas (Menas y Gangas)")
    mt = rec.get("mineralogia_texturas") or []
    if mt:
        L.append(md_table(["Mineral", "%", "Texturas", "Observaciones"],
                          [[m.get("mineral",""), m.get("pct",""), m.get("texturas",""), m.get("observaciones","")] for m in mt]))
    L.append("")
    L.append("## 2. Esquema")
    if esq.get("descripcion"):
        L.append(esq["descripcion"])
    if esq.get("escala"):
        L.append(f"\n_Escala:_ {esq['escala']}")
    L.append("")
    L.append("## 3. Ensambles de Minerales de Alteracion")
    ea = rec.get("ensambles_alteracion") or []
    if ea:
        L.append(md_table(["Mineral", "%", "Intensidad", "Observaciones"],
                          [[m.get("mineral",""), m.get("pct",""), m.get("intensidad",""), m.get("observaciones","")] for m in ea]))
    L.append("")
    ven = rec.get("venillas") or []
    if ven:
        L.append("## Tipo de venillas")
        L.append(md_table(["Venilla", "Espesor (mm)", "Asociaciones minerales", "Observaciones"],
                          [[v.get("tipo",""), v.get("espesor_mm",""), v.get("asociaciones",""), v.get("observaciones","")] for v in ven]))
        L.append("")
    pd_ = rec.get("ensambles_proximal_distal") or []
    if pd_:
        L.append("## Ensambles minerales proximal / distal")
        L.append(md_table(["Mineral", "%", "Asociacion", "Observaciones"],
                          [[m.get("mineral",""), m.get("pct",""), m.get("asociacion",""), m.get("observaciones","")] for m in pd_]))
        L.append("")
    if seq:
        L.append("## 4. Secuencia paragenetica")
        if seq.get("descripcion"):
            L.append(seq["descripcion"])
        ev = seq.get("eventos") or []
        if ev:
            L.append(md_table(["Mineral / asociacion", "Etapa", "Notas"],
                              [[e.get("mineral",""), e.get("etapa",""), e.get("notas","")] for e in ev]))
        L.append("")
    L.append("## 5. Interpretacion")
    L.append(f"- **Protolito:** {interp.get('protolito','')}")
    L.append(f"- **Alteraciones:** {interp.get('alteraciones','')}")
    L.append(f"- **Condiciones Fisico-Quimicas:** {interp.get('condiciones_fq','')}")
    L.append(f"- **Tipo de Yacimiento:** {interp.get('tipo_yacimiento','')}")
    if rec.get("notas_transcripcion"):
        L.append("")
        L.append(f"> Notas: {rec['notas_transcripcion']}")
    L.append("")
    return "\n".join(L)


def load_records():
    recs = []
    for rj in sorted(glob.glob(os.path.join(SAMPLES_DIR, "*", "record.json"))):
        with open(rj, encoding="utf-8") as f:
            rec = json.load(f)
        rec["_dir"] = os.path.basename(os.path.dirname(rj))
        recs.append(rec)
    return recs


def build_index(recs):
    entries = []
    for r in recs:
        interp = r.get("interpretacion", {}) or {}
        entries.append({
            "codigo": r.get("codigo", ""),
            "dir": r["_dir"],
            "autor": r.get("autor", ""),
            "fuente_pdf": r.get("fuente_pdf", ""),
            "pagina": r.get("pagina", 0),
            "tipo_yacimiento": interp.get("tipo_yacimiento", ""),
            "protolito": interp.get("protolito", ""),
            "minerales_mena": minerals(r.get("mineralogia_texturas")),
            "minerales_alteracion": minerals(r.get("ensambles_alteracion")),
            "confianza": r.get("confianza", ""),
        })
    entries.sort(key=lambda e: (e["fuente_pdf"], e["pagina"]))
    return entries


def build_catalog(entries):
    lines = [
        "# Catalogo de muestras (ReconYac)",
        "",
        f"Total: **{len(entries)}** muestras.",
        "",
        "| Codigo | Autor | Tipo de yacimiento | Minerales de mena | Alteracion | Fuente (pag) | Conf. |",
        "|---|---|---|---|---|---|---|",
    ]
    for e in entries:
        mena = ", ".join(e["minerales_mena"][:6])
        alt = ", ".join(e["minerales_alteracion"][:6])
        src = f"{e['fuente_pdf']} (p{e['pagina']})"
        link = f"[{e['codigo'] or e['dir']}](samples/{e['dir']}/record.md)"
        lines.append(
            f"| {link} | {e['autor']} | {e['tipo_yacimiento']} | {mena} | {alt} | {src} | {e['confianza']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    recs = load_records()
    # (re)generate record.md next to each record.json
    for r in recs:
        md_path = os.path.join(SAMPLES_DIR, r["_dir"], "record.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(render_record_md(r))
    entries = build_index(recs)
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump({"total": len(entries), "muestras": entries}, f, ensure_ascii=False, indent=2)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        f.write(build_catalog(entries))
    print(f"index.json: {len(entries)} muestras")
    print(f"catalog.md: {CATALOG_PATH}")


if __name__ == "__main__":
    main()
