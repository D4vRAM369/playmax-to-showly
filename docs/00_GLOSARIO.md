# Glosario

| Término | Qué significa | Dónde aparece |
|---|---|---|
| **Export / Backup** | Copia de tus datos en un archivo para guardarla o llevarla a otro sitio. | ZIP de Playmax, JSON de Showly |
| **JSON** | Formato de texto para datos estructurados: `{"clave": valor}` y listas `[...]`. Lo lee cualquier lenguaje. | Todo el proyecto |
| **CSV** | Tabla en texto, columnas separadas por comas. Playmax lo incluye duplicado en `data_in_csv/`; usamos el JSON porque conserva tipos (números, booleanos). | Export de Playmax |
| **Esquema (schema)** | El "molde" de los datos: qué campos hay, cómo se llaman y de qué tipo son. | `BackupScheme` de Showly |
| **Mapeo** | Regla que dice "este campo de A va a este campo de B". | `MARK_TO_COLLECTION` |
| **Ficha** | En Playmax, cada serie o película. Tiene un `mark` (estado) y `rating`. | `fichas.json` |
| **mark** | Estado en Playmax: `following` (siguiendo), `viewed` (vista), `pending` (pendiente), `favorite`, `abandoned`, o vacío. | `fichas.json` |
| **TMDB** | The Movie Database: base de datos pública de cine/TV. Cada título tiene un número (Breaking Bad = `tv/1396`). | `idTheMovieDB` |
| **IMDb ID** | Identificador de IMDb, empieza por `tt` (Breaking Bad = `tt0903747`). | `idImdb` |
| **Trakt** | Servicio de seguimiento de series/pelis con API pública. Showly está construida encima de Trakt. | Toda la conversión |
| **Trakt ID** | Número interno de Trakt para cada serie, temporada, episodio o peli. Showly lo usa como clave de todo. | Campo `id` del backup |
| **API REST** | Forma de pedir datos a un servidor por URL (`GET /search/tmdb/1396`), recibiendo JSON. | `Trakt.get()` |
| **Client ID / API key** | "Carné" que identifica tu programa ante una API. Trakt lo exige en la cabecera `trakt-api-key`. | `TRAKT_CLIENT_ID` |
| **Cabecera HTTP (header)** | Metadatos que viajan con la petición (versión de API, clave, User-Agent). | `Trakt.get()` |
| **Rate limit** | Límite de peticiones por tiempo. Si te pasas, el servidor responde `429 Too Many Requests`. | `Retry-After` |
| **Cache** | Guardar respuestas ya obtenidas para no volver a pedirlas. | `output/trakt_cache.json` |
| **ISO 8601** | Formato estándar de fecha: `2023-03-18T20:32:04.000Z`. La `Z` = UTC. | `iso()` |
| **Unix timestamp** | Segundos desde el 1-1-1970 UTC. Playmax lo da en `*DateUnix`. | `markDateUnix` |
| **UTC** | Hora universal, sin zona horaria. Playmax exporta en Europe/Madrid; convertimos a UTC. | `iso()` |
| **Moshi** | Librería Kotlin que convierte JSON ↔ objetos. Showly la usa para leer el backup; es estricta con los campos obligatorios. | Showly |
| **Ingeniería inversa (RE)** | Entender cómo funciona algo a partir del producto terminado, no de su documentación. | REA |
| **REA** | Herramienta MCP de ingeniería inversa; aquí, inventario verificado (con hashes SHA-256) del ZIP. | Paso 1 |
| **MCP** | Model Context Protocol: forma estándar de dar herramientas a un asistente de IA. | REA |
| **SHA-256** | Huella digital de un archivo. Si cambia un byte, cambia la huella. Sirve para probar que analizamos *ese* archivo. | Evidencia REA |
| **ADB** | Android Debug Bridge: control del móvil Android desde el PC por USB. | Paso final |
| **stdlib** | Librería estándar: lo que trae Python sin instalar nada (`json`, `zipfile`, `urllib`). | Todo el script |
| **Watchlist** | Lista de "quiero ver". En Showly = `cW`. | Mapeo |
| **Oculto (Hidden/Archive)** | Colección de Showly para cosas que no quieres ver en progreso. Equivalente a "abandonada". | `cHid` |
| **Pinned** | En Showly, fijado arriba en la pestaña Progreso. Usado para los favoritos. | `pP` |
