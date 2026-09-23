# ReconYac — Base de datos de descripción de muestras minerales

Base de datos estructurada de muestras de mano descritas con el **Formato de
Descripción de Muestras Minerales GE-701** (UNI — Facultad de Ingeniería
Geológica, Minera y Metalúrgica, Escuela de Geología).

El objetivo es tener una **memoria consultable**: cada muestra queda registrada con
su mineralogía, texturas, esquema, ensambles de alteración, secuencia paragenética
e interpretación, junto con la imagen de la página original. Así, al recibir una
imagen nueva, se puede relacionar con las muestras ya descritas.

## Estructura

```
muestras_pdf/                 PDFs fuente (subidos por lote)
schema/sample.schema.json     Esquema JSON del registro GE-701
scripts/
  render_pdf.py               PDF -> PNG por página (para lectura visual)
  build_index.py              Genera record.md, db/index.json y db/catalog.md
db/
  samples/<CODIGO>/
    record.json               Ficha estructurada (fuente de verdad, editable)
    record.md                 Ficha legible (GENERADA, no editar a mano)
    page.jpg                  Imagen de la página de la muestra
  index.json                  Índice maestro para búsqueda (GENERADO)
  catalog.md                  Catálogo legible con enlaces (GENERADO)
```

`record.json` es la **fuente de verdad**. `record.md`, `index.json` y `catalog.md`
se **regeneran** con `build_index.py`.

## Campos del registro (GE-701)

1. **Mineralogía y Texturas (Menas y Gangas)** — mineral · % · texturas · observaciones
2. **Esquema** — descripción del dibujo + escala
3. **Ensambles de Minerales de Alteración Hidrotermal / Supérgeno** — mineral · % ·
   intensidad (incipiente/débil/moderada/intensa/pervasiva) · observaciones
4. **Secuencia paragenética** — eventos en orden temporal (cuando el formato la incluye)
5. **Interpretación** — protolito · alteraciones · condiciones físico-químicas · tipo de yacimiento

## Cómo agregar un lote de muestras

1. Copiar el/los PDF a `muestras_pdf/`.
2. Renderizar las páginas para leerlas:
   ```bash
   python scripts/render_pdf.py muestras_pdf/<archivo>.pdf --pages 1-50 --out _work
   ```
   (los PNG van a `_work/`, que está en `.gitignore`).
3. Por cada muestra, crear `db/samples/<CODIGO>/record.json` (según `schema/`) y
   guardar la imagen de su página (JPEG liviano):
   ```bash
   python scripts/save_page.py muestras_pdf/<archivo>.pdf <pagina> <CODIGO>
   ```
4. Regenerar índices y fichas legibles:
   ```bash
   python scripts/build_index.py
   ```
5. Validar (opcional):
   ```bash
   python -c "import json,glob,jsonschema; s=json.load(open('schema/sample.schema.json')); [jsonschema.validate(json.load(open(f)),s) for f in glob.glob('db/samples/*/record.json')]"
   ```

## Requisitos

```bash
pip install pymupdf jsonschema
```

## Consulta ("memoria")

`db/catalog.md` da una vista tabular rápida; `db/index.json` permite búsquedas por
mineral de mena, mineral de alteración, tipo de yacimiento o protolito.
