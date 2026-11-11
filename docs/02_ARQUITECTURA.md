# Arquitectura

## El flujo (como una tubería de agua)

```
playmax.zip ──► leer JSON ──► por cada ficha ──► Trakt: ¿qué Trakt ID tiene? ──► clasificar ──► showly_backup.json
                                               └► Trakt: temporadas y episodios (IDs)          └► report.json
                                                    (todo cacheado en trakt_cache.json)
```

## Los dos esquemas cara a cara

### Playmax (lo que sale)

| Archivo | Contenido | Campos clave |
|---|---|---|
| `fichas.json` | series y películas marcadas | `idTheMovieDB` (`tv/1396`), `idImdb`, `mark`, `rating` (0–10 con .5), fechas unix |
| `episodes.json` | episodios vistos / con nota | `fichaId`, `season`, `episode`, `viewed`, `rating` |
| `seasons.json` | notas por temporada | `fichaId`, `season`, `rating` |
| `comments.json` | comentarios públicos (texto) | `text`, `date` |
| `lists`, `folders`, `chats`, `news`, `user_data`… | listas, mensajes, perfil | no se usan |

Valores posibles de `mark`: `following`, `viewed`, `pending`, `favorite`, `abandoned` o vacío.

### Showly (lo que entra) — `BackupScheme` versión 2

Sacado del código fuente (`ui-backup/.../model/*.kt`). Las claves JSON son abreviadas (`@Json(name = "cH")`):

```
{ version: 2, platform: "android", createdAt: ISO,
  shows:  { cH, cW, cHid,        ← colecciones: Mis series / Watchlist / Ocultas
            pEp, pSe,            ← progreso: episodios y temporadas vistas
            pP, pOH,             ← fijadas / en pausa (listas de Trakt ID)
            rS, rSe, rEp },      ← notas serie / temporada / episodio
  movies: { cH, cW, cHid, pP, rM },
  lists:  { l: [] } }
```

**Todo se identifica por Trakt ID** (`id`). `tmId` (TMDB) también va, pero el importador busca por Trakt.

### Los códigos del backup de Showly

**Por qué son tan cortos:** Showly guarda el backup en JSON y el nombre de cada campo se repite una vez por elemento. Si hay miles de episodios, `"progressEpisodes"` en vez de `"pEp"` engorda mucho el archivo. Por eso el código Kotlin usa nombres largos y legibles, y la anotación `@Json(name = "pEp")` le dice a Moshi qué nombre corto escribir en el JSON.

```kotlin
@Json(name = "pEp") val progressEpisodes: List<BackupEpisode>
//          ↑ en el archivo         ↑ en el código
```

**Cómo leerlos:** primera letra = tipo de dato (**c**ollection, **p**rogress, **r**ating). El resto = qué cosa.

| Código | Propiedad Kotlin | Qué es en la app | Elementos | Qué hace el importador |
|---|---|---|---|---|
| `cH` | `collectionHistory` | Mis series / Mis películas | `{id, tmId, t, a, u}` (`u` solo series) | Descarga la ficha de Trakt; en series, además temporadas + episodios y marca vistos los de `pEp` |
| `cW` | `collectionWatchlist` | Watchlist | `{id, tmId, t, a}` | Descarga la ficha y la mete en Watchlist (sin progreso) |
| `cHid` | `collectionHidden` | Ocultas | `{id, tmId, t, a}` | Descarga la ficha y la archiva |
| `pEp` | `progressEpisodes` | Episodios vistos | `{id, sId, stmId, sN, eN, a}` | Empareja por nº de temporada + episodio y lo marca visto con fecha `a` |
| `pSe` | `progressSeasons` | Temporadas vistas | `{id, sId, stmId, sN}` | La marca vista solo si además están vistos **todos** sus episodios |
| `pP` | `progressPinned` | Fijadas en Progreso | lista de Trakt ID | Las fija arriba |
| `pOH` | `progressOnHold` | En pausa | lista de Trakt ID | Las pone en pausa |
| `rS` / `rM` | `ratingsShows` / `ratingsMovies` | Nota de serie / película | `{id, tmId, r, rA}` | Guarda la nota si no había una |
| `rSe` | `ratingsSeasons` | Nota de temporada | `{id, sId, stmId, sN, r, rA}` | `id` = Trakt ID **de la temporada** |
| `rEp` | `ratingsEpisodes` | Nota de episodio | `{id, sId, stmId, sN, eN, r, rA}` | `id` = Trakt ID **del episodio** |

Campos dentro de cada elemento:

| Campo | Significado |
|---|---|
| `id` | Trakt ID del elemento (serie, peli, temporada o episodio según el apartado) |
| `tmId` | TMDB ID |
| `sId` / `stmId` | Trakt ID / TMDB ID **de la serie** a la que pertenece |
| `sN` / `eN` | Número de temporada / episodio |
| `t` | Título (solo para mostrar el progreso durante la importación) |
| `a` | *addedAt*: fecha de alta, o de visionado en episodios |
| `u` | *updatedAt*: en series, la usa como "última vez visto" |
| `r` / `rA` | Nota 1–10 / fecha de la nota |

## Decisiones de mapeo

🏗️ DECISIÓN: ¿Cómo se traduce cada estado?

| Playmax `mark` | Serie en Showly | Película en Showly | Por qué |
|---|---|---|---|
| `following` | `cH` Mis series + episodios vistos | — | "Siguiendo" = la estás viendo |
| `viewed` | `cH` + episodios | `cH` Historial (vista) | Showly no distingue "terminada": lo deduce de los episodios |
| `favorite` | `cH` + `pP` fijada | `cH` | Showly no tiene favoritos; "fijar" es lo más parecido |
| `pending` | `cW` Watchlist | `cW` Watchlist | Equivalente directo |
| `abandoned` | `cHid` Oculta | `cHid` Oculta | Showly no tiene "abandonada"; ocultar es lo más cercano |
| vacío | solo nota | solo nota | No hay estado que importar |
| cualquiera **con episodios vistos** (salvo abandonada) | → `cH` | — | Si tienes progreso, debe verse en Progreso (caso: 1 pendiente con vistos) |

🏗️ DECISIÓN: ¿Cómo conseguir el Trakt ID?

| Opción A: API Trakt con Client ID propio | Opción B: Scraping web de trakt.tv | Opción C: Sacar la clave del APK de Showly |
|---|---|---|
| ✅ Oficial, estable, gratis | ✅ Sin clave | ✅ Sin registrarse |
| ✅ Da IDs de temporadas y episodios | ❌ Frágil, solo da slugs | ❌ Usa credenciales de otro (no es tuyo) |
| ❌ 2 minutos de registro | ❌ Contra términos de uso | ❌ Contra términos de uso |

**Elegida: A.** Se probó sin clave → `403` (ver 05_ERRORES).

🏗️ DECISIÓN: Notas 0–10 con medios → 1–10 enteros

Redondeo "medio hacia arriba" (`floor(x + 0.5)`): 7.5 → 8, 0.5 → 1. **No** se usa `round()` de Python porque redondea al par (`round(6.5) = 6`), lo que bajaría unas notas y subiría otras al azar. 0 = sin nota → no se exporta.

🏗️ DECISIÓN: Temporadas vistas (`pSe`)

Se listan todas las temporadas con algún episodio visto. Showly (en `loadSeasonsEpisodes`) solo la marca como vista si además el nº de episodios vistos == nº de episodios en Trakt, así que no hay riesgo de marcar de más.

## Lo que NO se puede importar (y por qué)

| Dato Playmax | Motivo |
|---|---|
| Comentarios | Showly no tiene comentarios ni notas de texto en el backup |
| Fecha exacta de "pendiente" vs "siguiendo" | Showly solo guarda `addedAt` |
| Estado "favorito" de películas | No hay campo; las favoritas van como vistas |
| Medios puntos | Showly usa enteros |
| Títulos que Trakt no conoce | Sin Trakt ID Showly no puede bajar la ficha → `report.json` |
