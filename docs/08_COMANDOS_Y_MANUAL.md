# Comandos y manual

## Comandos usados (2026-11-11)

| Para qué | Comando |
|---|---|
| Ver versión de Python | `python3 --version` |
| Contar estados en Playmax | `python3 -I -c "import json,collections as C; print(C.Counter(x['mark'] for x in json.load(open('fichas.json'))))"` |
| Saber a dónde se movió el repo de Showly | `gh api repos/michaldrabik/showly-2.0 --jq .full_name` |
| Clonar código de Showly (solo último commit) | `git clone --depth 1 https://github.com/trakt/showly showly_src` |
| Buscar el código de backup | `grep -rli backup --include=*.kt showly_src` |
| Probar si Trakt pide clave | `curl -s -o /dev/null -w "%{http_code}" -H "trakt-api-version: 2" https://api.trakt.tv/search/imdb/tt0903747` |
| Test sin red | `python3 -I test_convert.py` |

## Manual de uso

### 1. Convertir

```bash
export TRAKT_CLIENT_ID=tu_client_id
python3 -I playmax_to_showly.py ~/Descargas/playmax-userdata-XX.zip output
```

Tarda unos minutos (una o dos peticiones por título, con pausa). Si se corta, relánzalo: la cache sigue donde lo dejó.

Genera en `output/`:
- `showly_backup_from_playmax.json` → el archivo a importar.
- `report.json` → qué no se pudo mapear + recuento por colección.
- `trakt_cache.json` → cache de Trakt (se puede borrar).

### Cómo leer la salida

Al acabar, el script imprime el recuento por **código de Showly**: cuántos elementos van en cada apartado del backup.

```
"series":    { "cH": 40, "cW": 12, "cHid": 2, "pEp": 950, ... }
"peliculas": { "cH": 25,  "cW": 10, "cHid": 0, "rM": 20 }
No encontrados: 1 | episodios sin match: 3
```

(Los números son de ejemplo.) Chuleta: **c** = colección, **p** = progreso, **r** = nota.

| Código | Léelo como |
|---|---|
| `cH` | Mis series / Mis películas |
| `cW` | Watchlist (pendientes) |
| `cHid` | Ocultas (abandonadas) |
| `pEp` / `pSe` | Episodios / temporadas vistas |
| `pP` / `pOH` | Fijadas (favoritas) / En pausa |
| `rS` `rSe` `rEp` `rM` | Notas de serie / temporada / episodio / película |

Tabla completa, con la estructura de cada elemento: [02_ARQUITECTURA.md](02_ARQUITECTURA.md#los-códigos-del-backup-de-showly).

**Comprobación rápida:** los números deben cuadrar con los estados de Playmax. Por ejemplo, películas `cH` = vistas + favoritas, y series `cW` = pendientes − pendientes con episodios vistos. Si `pEp` es menor que tus episodios vistos, la diferencia está en `episodios_sin_match`.

`report.json` trae el detalle:

| Clave | Qué significa | Qué hacer |
|---|---|---|
| `no_encontrados_en_trakt` | Títulos sin Trakt ID: Showly no puede importarlos | Añadirlos a mano |
| `episodios_sin_match` | Episodio sin pareja en Trakt (`(visto)` / `(nota)`) | Marcarlo a mano; mirar en Especiales |
| `solo_nota_sin_coleccion` | Nota importada, pero la ficha no tenía estado | Opcional: añadirla a una colección |
| `importados` | El recuento de arriba | Comparar con Showly tras importar |

### 2. Pasar al móvil

```bash
adb push output/showly_backup_from_playmax.json /sdcard/Download/
```

### 3. Importar en Showly

Showly → **Ajustes → Backup → Importar** → elige `showly_backup_from_playmax.json` en Descargas. Espera a que termine (descarga cada ficha de Trakt).

### 4. Verificar

- Mis series / Progreso: deberían aparecer las series "siguiendo" con sus episodios vistos.
- Watchlist: pendientes. Ocultas: abandonadas.
- Comparar con `report.json → importados`.

## Comandos usados en la importación (2026-11-11)

| Para qué | Comando |
|---|---|
| Ver si el móvil está conectado | `adb devices` |
| Copiar el backup a Descargas del móvil | `adb push output/showly_backup_from_playmax.json /sdcard/Download/` |
| Comprobar que llegó entero (mismo tamaño en bytes) | `adb shell ls -l /sdcard/Download/showly_backup_from_playmax.json` |
