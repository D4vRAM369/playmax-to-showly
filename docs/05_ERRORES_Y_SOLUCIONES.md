# Errores y soluciones

## E1 — La carpeta del proyecto "no es un repositorio git"

```
fatal: no es un repositorio git (ni ningún padre en el punto de montaje /)
```

**Qué pasa:** el entorno decía que era repo, pero no hay `.git`.
**Solución:** ninguna necesaria para el conversor. Se creó igualmente `.gitignore` para cuando se haga `git init`. Deja fuera `output/` (tu historial), `*.zip` (el export) y carpetas de herramientas. `docs/` se ignoraba al principio, pero se decidió publicarla tras revisar que no contiene datos personales.

## E2 — Buscar el formato de backup de Showly en la web no da nada

**Qué pasa:** no hay documentación pública del JSON.
**Causa:** es un formato interno. Además el repo cambió de dueño (`michaldrabik/showly-2.0` → `trakt/showly`).
**Solución:** `gh api repos/michaldrabik/showly-2.0` devolvió `trakt/showly` (redirección) → clonar y leer el código.
**Cómo evitarlo:** con apps open source, ir directo al código; la doc suele no existir.

## E3 — Trakt responde 403 sin clave

```bash
curl ... https://api.trakt.tv/search/imdb/tt0903747   →  403
```

**Causa:** la API de Trakt exige cabecera `trakt-api-key`.
**Solución:** Client ID propio (01_SETUP §3). Se descartó usar la clave embebida en el APK de Showly: no es tuya y viola los términos.

## E4 (prevenido) — `round()` de Python con notas .5

`round(6.5) == 6`. Se usa `floor(x + 0.5)`. Cubierto por test (`to_showly_rating(6.5) == 7`).

## E5 (prevenido) — Showly salta en silencio lo que no encuentra

Si un Trakt ID no existe, el importador hace `continue` sin avisar. Por eso el script genera `report.json` con `no_encontrados_en_trakt` y `episodios_sin_match`: así sabes qué falta sin tener que comparar a mano.

## E6 — "Solo ha hecho las series" (falsa alarma)

**Qué pasó:** al ver el resumen final parecía que faltaban las películas.
**Realidad:** el JSON de salida tiene dos bloques, `"series"` y `"peliculas"`. Las películas estaban en el segundo.
**Cómo comprobarlo:** cuadrar los recuentos con los estados de Playmax. Por ejemplo, películas `cH` = vistas + favoritas, y `cW` = pendientes.

## E7 — Episodios que existen en Playmax pero no en Trakt con el mismo número

**Qué pasa:** algunos episodios vistos no encuentran pareja (`episodios_sin_match` en `report.json`).
**Causa:** cada base de datos numera a su manera. Un caso típico es un telefilm final que una cuenta como S04E23–24 y la otra como especial (temporada 0).
**Solución:** se informa en `report.json` y se marcan a mano en Showly. Automatizarlo (buscar por título del episodio) no compensa por 1 o 2 casos.

## E8 — Títulos con nota pero sin estado

**Qué pasa:** en Playmax pusiste nota a una ficha sin marcarla (`mark` vacío) ni ver episodios.
**Qué hace el script:** exporta la nota, pero no mete la ficha en ninguna colección. Aparece en `solo_nota_sin_coleccion`.
**Por qué:** inventar un estado ("¿vista? ¿pendiente?") sería meter datos falsos.

## E9 — "No sale New Application" en Trakt

**Qué pasa:** la guía (y la primera versión de esta doc) mandaba a `trakt.tv/oauth/applications` → *New Application*, y el botón no aparece.
**Causa:** Trakt movió los ajustes de desarrollador a su web nueva, `app.trakt.tv`. Muchas guías de terceros siguen con la URL antigua.
**Solución:** la documentación oficial (`developer.trakt.tv/docs/authentication-oauth`) enlaza a `https://app.trakt.tv/settings/apps/api/new`.
**Cómo evitarlo:** cuando una guía no cuadra con lo que ves, ve a la documentación oficial del servicio antes de seguir probando.
