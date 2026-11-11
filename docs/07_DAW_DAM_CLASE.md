# Clase DAW/DAM: migrar datos entre dos apps

## Lección 1 — Toda app guarda datos, y cada una a su manera

Cuando marcas "visto" en una app, eso se guarda en una **base de datos** (en el móvil o en un servidor). Cuando exportas, la app vuelca esa base a un archivo. El formato lo decide quien programó la app. Por eso no puedes meter el export de Playmax en Showly: es como intentar abrir un `.docx` con un lector de PDF.

## Lección 2 — Antes de programar, investiga los dos lados

1. **Origen** (Playmax): abrimos el ZIP y contamos qué hay. Herramienta: REA para el inventario con huellas SHA-256, y Python para contar.
2. **Destino** (Showly): sin documentación → leímos su código fuente, porque es open source. Primero el *modelo* (qué campos hay), después el *importador* (qué hace con ellos).

> Regla de oro: **no adivines el formato de destino**. Si te equivocas en un nombre de campo, la app lo ignora o falla.

## Lección 3 — El problema de los identificadores

Cada base de datos pone su propio número a las cosas. Playmax habla "TMDB", Showly habla "Trakt". Necesitamos un **intérprete**: la API de Trakt, que dado un ID TMDB responde con el ID Trakt.

Una **API** es un camarero: tú pides (`GET /search/tmdb/1396?type=show`), él va a la cocina (servidor) y vuelve con el plato (JSON). Para que te atienda, enseñas tu carné (Client ID).

## Lección 4 — Escribir el traductor

Patrón que vale para cualquier migración:

```python
for registro in origen:
    id_destino = traducir_id(registro)        # API, tabla, lo que sea
    if not id_destino:
        informe.append(registro)               # nunca perder datos en silencio
        continue
    destino[clasificar(registro)].append(transformar(registro))
```

Tres funciones pequeñas y testeables: `traducir`, `clasificar`, `transformar`.

## Lección 5 — Probar sin depender de internet

El test sustituye la API real por una falsa (`FakeTrakt`) que siempre responde lo mismo. Así comprobamos *nuestra* lógica, no la de Trakt. Esto se llama **stub** o **doble de prueba**.

## Ejercicios

1. ¿Qué pasaría si mapeamos `abandoned` a `cW` (watchlist)? ¿Es mejor o peor?
2. Cambia `to_showly_rating` para redondear siempre hacia abajo. ¿Qué test falla?
3. Añade al informe cuántos comentarios se pierden.
