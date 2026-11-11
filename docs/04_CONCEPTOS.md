# Conceptos

## 📦 Mapeo entre esquemas

🎯 **Qué es:** traducir datos de un "molde" a otro.
🔧 **Para qué:** dos apps que hacen lo mismo casi nunca guardan igual.
💡 **Analogía:** mudanza entre dos cocinas. En una las especias van en un cajón ("following"), en la otra en un estante ("cH"). Tú decides qué va dónde, y algunas cosas (los comentarios) no tienen sitio.
🔗 **En el proyecto:** `MARK_TO_COLLECTION` y la tabla de 02_ARQUITECTURA.

## 📦 Identificadores externos

🎯 **Qué es:** el "DNI" que una base de datos da a cada cosa.
🔧 **Problema:** Breaking Bad es `1396` en TMDB, `tt0903747` en IMDb y `1388` en Trakt. Mismo título, tres DNIs.
💡 **Analogía:** el mismo libro tiene ISBN, código de biblioteca y referencia de la librería. Para pedirlo en una tienda necesitas *su* referencia.
🔗 **En el proyecto:** `Trakt.find()` hace de "ventanilla de traducción".

## 📦 Leer el importador, no solo el modelo

El modelo (`BackupShows.kt`) dice qué campos *acepta*. El importador (`BackupImportShowsRunner.kt`) dice qué *hace* con ellos. Solo leyendo el segundo supimos que:
- las notas de episodio necesitan el Trakt ID del episodio,
- las series que no encuentra se saltan sin avisar,
- las temporadas vistas se validan contra el nº de episodios.

**Lección:** en ingeniería inversa, la fuente de verdad es el código que *consume* los datos.

## 📦 Cache

🎯 Guardar respuestas para no repetir peticiones.
💡 Como apuntar en una libreta el teléfono que ya buscaste en la guía.
🔗 `output/trakt_cache.json`: si el script se corta en la ficha 200, al relanzarlo las 199 primeras salen de la libreta al instante.

## 📦 Rate limit y `Retry-After`

Trakt permite ~1000 GET cada 5 min. El script hace pausa fija de 0,3 s (~200/min) y si aun así recibe `429`, espera los segundos que indique la cabecera `Retry-After`.

## 📦 Redondeo bancario vs. medio hacia arriba

`round(6.5)` en Python da **6** (redondea al par: "banker's rounding"), `round(7.5)` da **8**. Para notas eso es incoherente. `math.floor(x + 0.5)` siempre sube los .5.

## 📦 Fechas: unix → ISO 8601 UTC

Playmax: `1679171524` (segundos) y `"18-03-2023 21:32:04 Europe/Madrid"`. Showly: `"2023-03-18T20:32:04.000Z"`. Usamos el unix (no ambiguo) y lo pasamos a UTC: por eso las 21:32 de Madrid salen como 20:32Z.

## 📦 Python `-I` con archivos descargados

`python3 -I` ignora la carpeta actual al importar módulos. Si un ZIP descargado trajera un `json.py` malicioso y ejecutas Python dentro de esa carpeta, `import json` cargaría el suyo. `-I` lo evita.
