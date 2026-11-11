# Pipeline Playmax → Showly

> Script en Python que convierte el export de datos de Playmax (.zip) en un backup JSON que Showly sabe importar: series, películas, episodios vistos, pendientes, abandonadas, favoritas y notas.

## ¿Qué es esto?

Playmax y Showly son dos apps para llevar el control de lo que ves. Cada una guarda los datos a su manera, así que el export de una no se puede importar tal cual en la otra. Este proyecto es el "traductor": lee el ZIP de Playmax, consulta Trakt para conseguir los identificadores que Showly necesita, y escribe un archivo con el formato exacto de backup de Showly.

## Qué se importa y qué no (resumen)

| | Qué |
|---|---|
| ✅ **Se importa** | Series (siguiendo, vistas, pendientes, abandonadas, favoritas), episodios vistos con fecha, películas (vistas, pendientes, abandonadas), notas de serie, temporada, episodio y película |
| ⚠️ **Adaptado** | Abandonada → Oculta · Favorita → Fijada (series) o Vista (películas) · Notas .5 → hacia arriba |
| ✋ **A mano** | Lo que salga en `report.json`: episodios sin match, títulos no encontrados, fichas con nota pero sin estado · poner series "En pausa" |
| ❌ **Imposible** | Comentarios, favoritos de películas, medios puntos, listas, carpetas, chats y mensajes |

Las tablas completas de equivalencias y el significado de los códigos (`cH`, `cW`, `pEp`…) están en el **README de la raíz del proyecto** y, con su origen en el código de Showly, en [02_ARQUITECTURA.md](02_ARQUITECTURA.md#los-códigos-del-backup-de-showly). Cómo leer la salida del script: [08_COMANDOS_Y_MANUAL.md](08_COMANDOS_Y_MANUAL.md#cómo-leer-la-salida).

## ¿Qué vas a aprender siguiendo esta documentación?

- Cómo investigar el formato de datos de una app (ingeniería inversa con REA + leer su código fuente).
- Qué es un esquema de datos y cómo mapear uno a otro.
- Qué es un identificador externo (TMDB, IMDb, Trakt) y por qué hace falta "traducirlos".
- Cómo consumir una API REST con Python sin librerías externas (solo stdlib).
- Cache, rate limit, redondeo de notas, fechas ISO 8601.

## Stack tecnológico

| Tecnología | Versión | Para qué se usa |
|---|---|---|
| Python | 3.12.3 | Lenguaje del conversor (solo librería estándar) |
| REA (MCP) | rea-agents | Inventario verificado del ZIP de Playmax |
| API de Trakt | v2 | Traducir IDs TMDB/IMDb → Trakt ID |
| Showly (código fuente) | trakt/showly @ e08cb90 | Referencia del formato de backup (scheme v2) |
| ADB | sistema | (Opcional) pasar el archivo al móvil |

## Estructura del proyecto

```
pipeline-.../
├── README.md              ← portada pública (GitHub): uso, equivalencias, códigos
├── playmax_to_showly.py   ← el conversor
├── test_convert.py        ← test sin red (Trakt simulado)
├── output/                ← (generado) backup, informe, cache  [no versionado]
└── docs/                  ← esta documentación (se publica)
```

## Cómo seguir esta documentación

Lee los archivos en este orden: 01 → 02 → 03 → 04 → 05 → 06. `08_COMANDOS_Y_MANUAL.md` es la chuleta para usarlo. `07_DAW_DAM_CLASE.md` es la versión "clase".

## Estado

- [x] Formato de Playmax analizado
- [x] Formato de backup de Showly analizado (código fuente)
- [x] Conversor + test offline (pasa)
- [x] Ejecución real: 0 títulos sin encontrar, 2 episodios sin pareja
- [x] Backup copiado al móvil por ADB
- [ ] Importar en Showly y verificar recuentos
