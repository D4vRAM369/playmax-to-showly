# Paso a paso

## Sesión 1 — 2026-11-11

### Paso 1: Inventario del ZIP de Playmax con REA

**Qué:** saber qué contiene el export antes de tocar nada.
**Por qué REA y no solo `unzip -l`:** REA da un inventario con SHA-256 de cada archivo (cada evidencia lleva un ID y el SHA-256 del ZIP). Si mañana repites con otro export, puedes demostrar qué cambió.

Herramientas MCP: `open_binary` (ZIP) → `inspect_artifact`. Resultado: 27 entradas, 1 carpeta `data_in_csv/` que duplica los JSON en CSV, un avatar, y muchos JSON de 2 bytes (`[]` = vacíos).

Luego se descomprimió en una carpeta aislada (scratchpad) y se contó con Python `-I` (modo aislado: no carga módulos de la carpeta actual, por seguridad con archivos descargados):

```bash
python3 -I -c "import json,collections as C; f=json.load(open('fichas.json')); print(C.Counter(x['mark'] for x in f))"
```

Hallazgos: todas las fichas traen IMDb y TMDB; el prefijo de `idTheMovieDB` (`tv/` o `movie/`) dice si es serie o peli.

### Paso 2: Averiguar el formato de importación de Showly

1. Buscar documentación → no existe.
2. Showly es open source: el repo antiguo `michaldrabik/showly-2.0` ahora es **`trakt/showly`** (Trakt compró la app).
3. Clonar y buscar "backup":

```bash
git clone --depth 1 https://github.com/trakt/showly showly_src
grep -rli backup --include=*.kt showly_src
```

4. Leer `ui-backup/.../model/BackupScheme.kt`, `BackupShows.kt`, `BackupMovies.kt` → el esquema (ver 02_ARQUITECTURA).
5. Leer los **importadores** (`BackupImportShowsRunner.kt`, `BackupImportMoviesRunner.kt`) para saber qué hace *de verdad* con cada campo. Descubrimientos clave:
   - Cada serie/peli se busca por `traktId`; si no está en local, la descarga de Trakt (`detailsShow.load`). Si falla, **la salta en silencio**.
   - Episodios: descarga las temporadas de Trakt y marca vistos los que coincidan por **nº temporada + nº episodio**.
   - Notas de temporada/episodio se guardan con el Trakt ID **de la temporada/episodio**, no de la serie.
   - La versión se lee con un truco de texto (`substringAfter("version\":")`) → el JSON debe tener `"version":2` sin espacio tras los dos puntos. `json.dumps` por defecto pone `": "`… pero `substringBefore(",")` + `trim()` lo tolera. OK.
6. `BackupConfig.kt`: `SCHEME_VERSION = 2`, `platform = "android"`.

### Paso 3: El problema de los IDs

Playmax: TMDB + IMDb. Showly: Trakt. Hay que traducir. Prueba sin clave:

```bash
curl -s -o /dev/null -w "%{http_code}" -H "trakt-api-version: 2" https://api.trakt.tv/search/imdb/tt0903747
# 403
```

→ Hace falta Client ID (01_SETUP §3).

### Paso 4: El conversor `playmax_to_showly.py`

Piezas, de abajo arriba:

- `iso(unix)` → fecha ISO UTC con milisegundos y `Z`.
- `to_showly_rating(r)` → 0 = `None`; si no, `floor(r+0.5)` limitado a 1–10.
- `collection_for(mark, tiene_vistos)` → `cH` / `cW` / `cHid` / `None` (tabla en 02).
- `Trakt` → `get(path)` con cabeceras, cache en disco, reintento en `429`, 404 = `None`, pausa 0,3 s. `find(kind, tmdb, imdb)` prueba TMDB y luego IMDb.
- `load_zip()` → lee los `.json` de la raíz del ZIP sin descomprimir.
- `convert()` → recorre fichas, rellena `shows`/`movies` y un `report` con lo que no encaja.

Solo se piden temporadas a Trakt (`/shows/{id}/seasons?extended=episodes`) para series con episodios vistos o notas, no para todas.

### Paso 5: Test sin red

`test_convert.py` sustituye Trakt por un `FakeTrakt` y comprueba redondeo, clasificación, fechas, episodios sin match y título no encontrado.

```bash
python3 -I test_convert.py
# OK
```

### Paso 6 (pendiente): ejecución real e importación

Ver 08_COMANDOS_Y_MANUAL.
