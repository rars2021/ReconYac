# Guía para el agente de reconocimiento (página por página)

> **Para quién es esto:** otra sesión/cuenta de IA (Claude con visión) que continuará
> transcribiendo las muestras minerales de este repositorio, página por página, y
> subiendo el resultado a GitHub. Arrancas en frío: **todo lo que necesitas está aquí.**

---

## 0. Objetivo

Este repo (`rars2021/ReconYac`) es una **base de datos de descripción de muestras
minerales** con el **Formato GE-701** (UNI — Escuela de Geología). Cada muestra
(una página del formato) se convierte en un registro estructurado (`record.json`)
+ su imagen de página (`page.jpg`). El fin es tener una **memoria consultable** para
luego relacionar imágenes nuevas con lo ya descrito.

Tu tarea: **leer cada página de los PDF en `muestras_pdf/`, transcribirla a un
`record.json` según el esquema, guardar su imagen, regenerar índices y subir a
`main`.**

---

## 1. Preparación (una vez)

```bash
pip install pymupdf jsonschema
```

Ubícate en la raíz del repo (donde está este `docs/`, `schema/`, `scripts/`, `db/`).

> **Acceso a GitHub:** necesitas tu propio acceso de escritura al repo. El tráfico
> git de la sesión pasa por un proxy que aplica los permisos de la **Claude GitHub
> App**; si `git push` da **403 "Claude doesn't have GitHub access ... for your
> organization"**, hay que instalar/autorizar la app en `rars2021/ReconYac` desde
> https://github.com/apps/claude/installations/select_target (un token personal
> **no** sirve para saltarse el proxy). Si tienes la herramienta `add_repo`,
> adjunta el repo con acceso `push` antes de empezar.

---

## 2. Estructura del repo

```
muestras_pdf/                 PDFs fuente (MINAYA_DELGADO_STEVEN.pdf, Muestras_de_mano_240520.pdf, ...)
schema/sample.schema.json     Esquema JSON del registro GE-701 (CONTRATO — respétalo)
scripts/
  render_pdf.py               PDF -> PNG por página, a un dir temporal, PARA LEER
  save_page.py                Guarda db/samples/<CODIGO>/page.jpg (liviano) para el repo
  build_index.py              Genera record.md + db/index.json + db/catalog.md desde los record.json
db/
  samples/<CODIGO>/
    record.json               Ficha estructurada  <-- LO QUE TÚ CREAS (fuente de verdad)
    record.md                 GENERADO por build_index.py (no editar a mano)
    page.jpg                  Imagen de la página (la guardas con save_page.py)
  index.json                  GENERADO
  catalog.md                  GENERADO
docs/GUIA_RECONOCIMIENTO_AGENTE.md   (este archivo)
```

**Regla de oro:** solo escribes a mano `db/samples/<CODIGO>/record.json`. El
`record.md`, el `index.json` y el `catalog.md` se **regeneran** con
`scripts/build_index.py`. La imagen `page.jpg` la generas con `scripts/save_page.py`.

---

## 3. El registro GE-701 (`record.json`)

El esquema completo está en `schema/sample.schema.json`. Campos:

| Campo | Qué es |
|---|---|
| `codigo` | "Código de Muestra" tal como aparece en la hoja. Si falta, usa `<AUTOR_INICIALES>-p<NN>`. |
| `autor` | "Apellidos y Nombres" del recuadro superior derecho (incluye el código de alumno si está). |
| `fuente_pdf` | Nombre del PDF en `muestras_pdf/`. |
| `pagina` | Número de página (1-indexado) dentro de ese PDF. |
| `mineralogia_texturas` | Sección 1: lista de `{mineral, pct, texturas, observaciones}`. |
| `esquema` | Sección 2: `{descripcion, escala, imagen}`. Describe el dibujo (minerales y colores). `imagen` puede quedar `""`. |
| `ensambles_alteracion` | Sección 3: lista de `{mineral, pct, intensidad, observaciones}`. `intensidad` ∈ incipiente/débil/moderada/intensa/pervasiva. |
| `secuencia_paragenetica` | Sección 4 (si el formato la trae): `{descripcion, eventos:[{mineral, etapa, notas}]}`, eventos del más antiguo al más reciente. |
| `interpretacion` | Sección 5: `{protolito, alteraciones, condiciones_fq, tipo_yacimiento}`. |
| `confianza` | `alta` / `media` / `baja` según legibilidad del escaneo/manuscrito. |
| `notas_transcripcion` | Dudas, partes ilegibles, glifos ambiguos, etc. |

### Plantilla `record.json`

```json
{
  "codigo": "",
  "autor": "",
  "fuente_pdf": "",
  "pagina": 0,
  "mineralogia_texturas": [
    {"mineral": "", "pct": "", "texturas": "", "observaciones": ""}
  ],
  "esquema": {"descripcion": "", "escala": "", "imagen": ""},
  "ensambles_alteracion": [
    {"mineral": "", "pct": "", "intensidad": "", "observaciones": ""}
  ],
  "secuencia_paragenetica": {
    "descripcion": "",
    "eventos": [{"mineral": "", "etapa": "", "notas": ""}]
  },
  "interpretacion": {
    "protolito": "", "alteraciones": "", "condiciones_fq": "", "tipo_yacimiento": ""
  },
  "confianza": "alta",
  "notas_transcripcion": ""
}
```

> Un registro de ejemplo ya resuelto: `db/samples/MA-Y-19/record.json` (léelo como
> referencia de estilo y nivel de detalle).

---

## 4. Flujo por página (el bucle principal)

Trabaja **un PDF a la vez**. Para cada PDF:

### 4.1 Renderiza un bloque de páginas para leerlas

```bash
# Renderiza a un dir temporal (NO al repo). Máx cómodo: bloques de 5-10 páginas.
python scripts/render_pdf.py muestras_pdf/<ARCHIVO>.pdf --pages 5-14 --out /tmp/work
```

Esto crea `/tmp/work/<stem>/pNNN.png` y un `text.jsonl` con el texto embebido de
cada página (útil solo en PDFs nativos; en escaneados el texto viene vacío).

### 4.2 Lee cada PNG con tu visión

Abre `/tmp/work/<stem>/pNNN.png` y transcribe. Ten en cuenta:

- **Páginas de portada / separadores:** algunas páginas no son muestras sino títulos
  de sección (p.ej. MINAYA página 1 dice *"MUESTRAS MAGMÁTICOS"*). **No** generes
  registro para esas; anótalas mentalmente para saber a qué grupo pertenece lo que
  sigue.
- **Una muestra = una hoja GE-701.** Cada hoja trae arriba "Código de Muestra" y
  "Apellidos y Nombres".
- **Colores del esquema:** describe qué mineral representa cada color (ej. "gris =
  piroxenos, naranja = feldespato potásico").
- **Manuscrito ambiguo:** transcribe tu mejor lectura y **deja constancia en
  `notas_transcripcion`**; baja `confianza` a `media`/`baja` si toca. Mantén
  coherencia dentro del mismo autor (mismo glifo → misma letra).
- **% que no suman 100 / celdas vacías:** transcribe lo que hay, no "corrijas".

### 4.3 Escribe el `record.json`

- Carpeta = el `codigo` **saneado** (sin espacios ni `/`): reemplaza espacios y `/`
  por `-`. Ej.: código `MA-Y-19` → `db/samples/MA-Y-19/record.json`.
- Si dos muestras comparten código, añade sufijo `-b`, `-c`, … y anótalo.

### 4.4 Guarda la imagen de la página (liviana)

```bash
python scripts/save_page.py muestras_pdf/<ARCHIVO>.pdf <PAGINA> <CODIGO>
# -> db/samples/<CODIGO>/page.jpg  (~150-200 KB)
```

### 4.5 Repite hasta terminar el PDF, luego regenera e verifica

```bash
# Regenera record.md de cada muestra + index.json + catalog.md
python scripts/build_index.py

# Valida TODOS los registros contra el esquema
python -c "import json,glob,jsonschema; s=json.load(open('schema/sample.schema.json')); [jsonschema.validate(json.load(open(f)),s) for f in glob.glob('db/samples/*/record.json')]; print('schema OK')"
```

Si la validación falla, corrige el `record.json` señalado y vuelve a correr.

---

## 5. Subir a GitHub (`main`)

El propietario pidió trabajar **directo sobre `main`**, en **commits pequeños**
(uno por PDF, o cada ~10 muestras) para poder reanudar sin perder trabajo.

```bash
git add -A
git commit -m "Muestras <ARCHIVO>: transcripción páginas <A>-<B> (<n> muestras)"
git fetch origin main
git rebase origin/main       # por si main avanzó; resuelve y repite si hace falta
git push origin HEAD:main
```

- Antes de cada tanda haz `git fetch origin main && git rebase origin/main` para no
  chocar con otros commits.
- **No borres ni reproceses** carpetas `db/samples/<CODIGO>/` que ya existan (ver §6).
- Usa la atribución de commits que corresponda a **tu** sesión/cuenta (no reutilices
  identidades de otra sesión).

---

## 6. Reanudar sin duplicar (idempotencia)

Antes de procesar, mira qué códigos ya existen y sáltalos:

```bash
ls db/samples/                       # códigos ya hechos
```

Estado inicial conocido (al escribir esta guía):

| PDF | Páginas | Hecho | Pendiente |
|---|---|---|---|
| `MINAYA_DELGADO_STEVEN.pdf` | 50 | p1 = portada "MAGMÁTICOS"; **MA-Y-19** (p2), **MA-Y-20** (p3), **MA-Y-22** (p4) | **p5–p50** (ojo: puede haber más portadas de sección entre medio) |
| `Muestras_de_mano_240520.pdf` | 50 | — | **p1–p50** (este formato incluye "4.- Secuencia paragenética"; el texto embebido son solo las etiquetas del formato, el contenido es manuscrito → léelo con visión) |

> Nota sobre el código de MINAYA: la letra central se lee ambigua en el escaneo; se
> viene transcribiendo como **"Y"** (`MA-Y-NN`). Mantén ese criterio salvo que el
> dueño indique otra cosa, y déjalo en `notas_transcripcion`.

---

## 7. Checklist por muestra (resumen)

- [ ] Identifiqué que la página es una hoja GE-701 (no una portada).
- [ ] `codigo`, `autor`, `fuente_pdf`, `pagina` correctos.
- [ ] Sección 1 (mineralogía/texturas) completa.
- [ ] Sección 2 (esquema) descrita, con colores↔minerales.
- [ ] Sección 3 (alteración) con `intensidad` válida.
- [ ] Sección 4 (secuencia paragenética) si la hoja la tiene.
- [ ] Sección 5 (interpretación): protolito, alteraciones, condiciones FQ, tipo.
- [ ] `confianza` y `notas_transcripcion` puestos.
- [ ] `page.jpg` guardado con `save_page.py`.
- [ ] `build_index.py` corrido y validación de esquema OK.
- [ ] Commit + push a `main`.

---

## 8. Errores comunes

- **`pdftoppm is not installed`** al usar `Read` sobre un PDF: no uses `Read` sobre el
  PDF; usa `scripts/render_pdf.py` (PyMuPDF, no necesita poppler) y lee los PNG.
- **PNG enormes en el repo:** nunca comitees los PNG de `/tmp/work` ni `_work/` (están
  en `.gitignore`). Al repo solo va `page.jpg` (vía `save_page.py`).
- **`record.md` desincronizado:** no lo edites a mano; corrige el `record.json` y corre
  `build_index.py`.
- **Push 403:** es acceso de la GitHub App, no el contenido (ver §1).
