# Siguiente nivel

- **Comentarios → lista de Showly:** Showly no tiene notas, pero sí listas con descripción. Se podría crear una lista "Comentados en Playmax". Poco valor: el texto no se ve por título.
- **Favoritos de películas → lista "Favoritas":** usar `lists.l` del backup para no perder el estado favorito de las 3 pelis.
- **Resolver `report.json` a mano:** para títulos que Trakt no encuentra por TMDB/IMDb, búsqueda por texto (`/search/show?query=`) con confirmación.
- **Sincronizar con Trakt directamente:** en vez del backup, subir historial y notas a tu cuenta Trakt (`/sync/history`, `/sync/ratings`, OAuth). Showly con login Trakt lo bajaría solo, y quedaría también en la web de Trakt.
- **Import incremental:** volver a exportar Playmax y convertir solo lo nuevo (Showly ya salta lo que existe).
