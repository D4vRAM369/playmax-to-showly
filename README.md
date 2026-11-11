# Playmax → Showly

<p align="center"><b>Español</b> · <a href="README-EN.md">English</a></p>

Convierte el export de datos de **Playmax** (`.zip`) en un **backup JSON que Showly importa** desde *Ajustes → Backup → Importar*: series, películas, episodios vistos, pendientes, abandonadas, favoritas y notas.

Python 3.10+, sin dependencias. Necesita un **Client ID de Trakt** (gratis).

---

## Resumen rápido

| | Qué |
|---|---|
| ✅ **Se importa** | Series que sigues o has visto, pendientes, abandonadas, favoritas, todos los episodios vistos (con fecha), películas vistas, pendientes y abandonadas, notas de serie, temporada, episodio y película |
| ⚠️ **Se importa adaptado** | Abandonada → Oculta · Favorita → Fijada (series) o Vista (películas) · Notas .5 → redondeadas hacia arriba |
| ✋ **A mano** | Episodios que Trakt numera distinto (salen en `report.json`) · Fichas con nota pero sin estado · Series que quieras poner "En pausa" |
| ❌ **No es posible** | Comentarios · Favoritos de películas · Medios puntos · Listas, carpetas, chats y mensajes de Playmax |

---

## Qué exporta Playmax

El ZIP de Playmax (*Perfil → Ajustes → Exportar datos*) trae cada tabla en JSON y en CSV (`data_in_csv/`). El script usa los JSON:

| Archivo | Qué contiene | ¿Se usa? |
|---|---|---|
| `fichas.json` | Cada serie/película con su estado (`mark`), nota, fecha e IDs de TMDB e IMDb | ✅ |
| `episodes.json` | Episodios: visto sí/no, fecha, nota | ✅ |
| `seasons.json` | Notas por temporada | ✅ |
| `comments.json` | Tus comentarios en fichas | ❌ Showly no tiene comentarios |
| `lists.json`, `folders.json`, `following_lists.json`, `rated_lists.json` | Listas y carpetas | ❌ No se convierten (ver abajo) |
| `chats.json`, `privates_messages.json`, `news.json`, `user_data.json`, avatar | Mensajes, perfil | ❌ No tienen equivalente |

## Qué importa Showly

Showly **no guarda un "estado"** como Playmax. Organiza por **colecciones** y calcula el resto con los episodios vistos:
- Una serie en "Mis series" con episodios pendientes sale en **Progreso**.
- Si están todos vistos, Showly la da por terminada.

### Equivalencias de estados

**Series**

| Estado en Playmax | En Showly | Código en el backup |
|---|---|---|
| Siguiendo | Mis series + Progreso | `cH` + `pEp` |
| Vista | Mis series (terminada porque tiene todos los episodios vistos) | `cH` + `pEp` |
| Pendiente | Watchlist | `cW` |
| Abandonada | Oculta (no existe "abandonada") | `cHid` |
| Favorita | Mis series + fijada arriba en Progreso (no existe "favorita") | `cH` + `pP` |
| Sin estado, con episodios vistos | Mis series, para no perder el progreso | `cH` + `pEp` |
| Pendiente, con episodios vistos | Mis series (la Watchlist no guarda progreso) | `cH` + `pEp` |
| Sin estado y sin episodios | Solo se importa la nota, si tiene | `rS` |
| — (no existe en Playmax) | En pausa | `pOH` (vacío) |

**Películas**

| Estado en Playmax | En Showly | Código en el backup |
|---|---|---|
| Vista | Mis películas / historial | `cH` |
| Pendiente | Watchlist | `cW` |
| Abandonada | Oculta | `cHid` |
| Favorita | Vista (no hay favoritas de películas) | `cH` |
| Sin estado | Solo la nota, si tiene | `rM` |

### Notas

| Playmax | Showly | Conversión |
|---|---|---|
| 0–10 con medios puntos, 0 = sin nota | 1–10 enteros | Medio punto hacia arriba: 7,5 → 8 · 0,5 → 1 · 0 → no se exporta |

---

## Los códigos del final (qué significa cada uno)

Al terminar, el script imprime un recuento como este:

```json
{
  "series":    { "cH": …, "cW": …, "cHid": …, "pEp": …, "pSe": …, "pP": …, "pOH": …, "rS": …, "rSe": …, "rEp": … },
  "peliculas": { "cH": …, "cW": …, "cHid": …, "pP": …, "rM": … }
}
No encontrados: N | episodios sin match: N
```

Son las **claves abreviadas que usa Showly en su archivo de backup**. No las inventa el script: vienen del código de Showly (`ui-backup/.../model/BackupShows.kt` y `BackupMovies.kt`). El número es cuántos elementos van en cada apartado.

La primera letra indica el tipo de dato: **c** = colección, **p** = progreso, **r** = rating (nota).

| Código | Nombre en el código de Showly | Qué es en la app | Series | Películas |
|---|---|---|---|---|
| `cH` | `collectionHistory` | **Mis series / Mis películas** (lo que sigues o has visto) | ✅ | ✅ |
| `cW` | `collectionWatchlist` | **Watchlist** (pendientes) | ✅ | ✅ |
| `cHid` | `collectionHidden` | **Ocultas** (aquí van las abandonadas) | ✅ | ✅ |
| `pEp` | `progressEpisodes` | **Episodios vistos**, con fecha | ✅ | — |
| `pSe` | `progressSeasons` | **Temporadas vistas**. Showly solo la marca si cuadra con todos sus episodios | ✅ | — |
| `pP` | `progressPinned` | **Fijadas** arriba en Progreso (aquí van las favoritas) | ✅ | ✅ (vacío) |
| `pOH` | `progressOnHold` | **En pausa** (Playmax no lo tiene, va vacío) | ✅ | — |
| `rS` | `ratingsShows` | Notas de **serie** | ✅ | — |
| `rSe` | `ratingsSeasons` | Notas de **temporada** | ✅ | — |
| `rEp` | `ratingsEpisodes` | Notas de **episodio** | ✅ | — |
| `rM` | `ratingsMovies` | Notas de **película** | — | ✅ |

Las dos líneas finales:
- **No encontrados:** títulos para los que Trakt no devolvió ID. Showly no podría descargarlos, así que no van en el backup.
- **Episodios sin match:** episodios vistos o con nota cuyo número (temporada × episodio) no existe en Trakt. Suele pasar con especiales y telefilms numerados distinto.

El detalle de ambos está en `output/report.json`:

| Clave en `report.json` | Qué significa | Qué hacer |
|---|---|---|
| `no_encontrados_en_trakt` | Títulos sin Trakt ID | Añadirlos a mano en Showly |
| `episodios_sin_match` | Episodios sin pareja en Trakt (`(visto)` o `(nota)`) | Marcarlos a mano. Suelen estar en "Especiales" |
| `solo_nota_sin_coleccion` | Fichas con nota pero sin estado en Playmax | Opcional: añadirlas a la colección que quieras |
| `importados` | El mismo recuento de códigos de arriba | Comparar con lo que muestra Showly tras importar |

---

## ✋ Qué hay que hacer a mano

1. **Episodios de `episodios_sin_match`:** márcalos como vistos en Showly. Si no aparecen en su temporada, busca en *Especiales* (temporada 0).
2. **Títulos de `no_encontrados_en_trakt`:** búscalos y añádelos a mano en Showly.
3. **Fichas de `solo_nota_sin_coleccion`:** la nota sí se importa, pero no entran en ninguna colección. Añádelas si quieres verlas.
4. **"En pausa":** si alguna serie que seguías en realidad la tienes parada, ponla en pausa en Showly.

## ❌ Qué no es posible (y por qué)

| Dato | Por qué no |
|---|---|
| Comentarios | El backup de Showly no tiene campo de texto ni comentarios |
| Favoritos de películas | Showly no tiene "favorita" ni "fijada" con sentido para películas vistas |
| Distinguir "Siguiendo" de "Vista" | Showly no guarda la etiqueta, la calcula con los episodios (el resultado es el mismo) |
| Medios puntos en notas | Showly solo admite enteros 1–10 |
| Listas y carpetas de Playmax | Las listas de Showly son de Trakt y el script no las crea. Ver *Mejoras posibles* |
| Chats, mensajes, noticias, perfil | No existen en Showly |
| Fecha en que marcaste "pendiente" vs. "siguiendo" | Showly guarda una sola fecha de alta |

---

## Uso

### 1. Client ID de Trakt

Showly identifica todo por **Trakt ID** y Playmax solo trae TMDB e IMDb, así que el script pregunta a la API de Trakt.

1. Entra en https://app.trakt.tv/settings/apps/api/new con tu cuenta de Trakt.
2. **App name:** cualquiera · **App type:** Development · **Redirect URIs:** `http://localhost` · lo demás vacío.
3. Crea la app y copia el **Client ID**. El *Client Secret* no hace falta: no lo compartas.

### 2. Convertir

```bash
read -s -p "Trakt Client ID: " TRAKT_CLIENT_ID && export TRAKT_CLIENT_ID && echo
```

```bash
python3 -I playmax_to_showly.py /ruta/playmax-userdata-XX.zip output
```

Tarda unos minutos. Si se corta, relánzalo: `output/trakt_cache.json` evita repetir peticiones.

Genera en `output/`:
- `showly_backup_from_playmax.json`: el archivo a importar.
- `report.json`: lo que no se pudo mapear y el recuento.
- `trakt_cache.json`: cache de Trakt, se puede borrar.

> ⚠️ `output/` contiene todo tu historial. Está en `.gitignore`: no lo subas.

### 3. Pasar al móvil

Cópialo a *Descargas* del móvil (por cable, nube, etc.). Con ADB:

```bash
adb push output/showly_backup_from_playmax.json /sdcard/Download/
```

### 4. Importar en Showly

*Ajustes → Backup → Importar* → elige el archivo. Showly descarga de Trakt cada ficha, así que tarda. Al acabar, compara con `importados` de `report.json`.

## Test

```bash
python3 -I test_convert.py
```

No usa red: sustituye Trakt por una versión falsa y comprueba redondeo de notas, clasificación de estados, fechas y el informe.

## Cómo se averiguó el formato

- **Playmax:** inventario del ZIP con [REA](https://github.com/morluto/rea) y lectura de los JSON.
- **Showly:** no tiene documentación del backup. Se leyó su código fuente ([trakt/showly](https://github.com/trakt/showly), antes `michaldrabik/showly-2.0`): los modelos (`BackupScheme`, `BackupShows`, `BackupMovies`) y, sobre todo, los importadores (`BackupImportShowsRunner`, `BackupImportMoviesRunner`), que muestran qué hace la app con cada campo.

## Mejoras posibles

- Crear una lista "Favoritas" en el backup (`lists.l`) para no perder las películas favoritas.
- Buscar por título los episodios sin match.
- Subir el historial directamente a Trakt (`/sync/history`) en lugar de generar un backup.
