#!/usr/bin/env python3
"""Convierte el export de Playmax (.zip) en un backup JSON importable por Showly (scheme v2).

Uso:
    TRAKT_CLIENT_ID=xxxx python3 -I playmax_to_showly.py /ruta/playmax-userdata.zip [salida_dir]

Showly identifica todo por Trakt ID; Playmax solo trae TMDB/IMDb. Por eso el script
consulta la API pública de Trakt (necesita un Client ID propio, gratis en
https://trakt.tv/oauth/applications) y guarda las respuestas en cache para no repetir.
"""
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TRAKT = "https://api.trakt.tv"

# Playmax "mark" -> colección Showly. cH=Mis series/Historial, cW=Watchlist, cHid=Oculto
MARK_TO_COLLECTION = {"following": "cH", "viewed": "cH", "favorite": "cH", "pending": "cW", "abandoned": "cHid"}


def iso(unix):
    """Showly espera ISO 8601 UTC: 2021-01-01T00:00:00.000Z"""
    dt = datetime.fromtimestamp(unix or time.time(), tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def to_showly_rating(r):
    """Playmax 0-10 con medios puntos (0 = sin nota). Showly 1-10 entero. Redondeo .5 hacia arriba."""
    if not r:
        return None
    return max(1, min(10, math.floor(r + 0.5)))


def collection_for(mark, has_viewed_episodes):
    """Si hay episodios vistos, la serie va a 'Mis series' salvo que esté abandonada (oculta)."""
    col = MARK_TO_COLLECTION.get(mark)
    if has_viewed_episodes and col != "cHid":
        return "cH"
    return col


class Trakt:
    def __init__(self, client_id, cache_path):
        self.client_id = client_id
        self.cache_path = cache_path
        self.cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    def get(self, path):
        if path in self.cache:
            return self.cache[path]
        req = urllib.request.Request(TRAKT + path, headers={
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
            "User-Agent": "playmax-to-showly/1.0",
        })
        for _ in range(5):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:  # rate limit: esperar lo que diga Trakt
                    time.sleep(int(e.headers.get("Retry-After", "5")) + 1)
                    continue
                if e.code == 404:
                    data = None
                    break
                raise
        else:
            raise RuntimeError(f"Trakt sigue limitando {path}")
        self.cache[path] = data
        self.cache_path.write_text(json.dumps(self.cache))
        time.sleep(0.3)  # ponytail: pausa fija, ~200 req/min < límite de Trakt (1000/5min)
        return data

    def find(self, kind, tmdb, imdb):
        """kind = 'show' | 'movie'. Busca por TMDB y si no, por IMDb. Devuelve dict ids o None."""
        for src, ident in (("tmdb", tmdb), ("imdb", imdb)):
            if not ident:
                continue
            for hit in self.get(f"/search/{src}/{ident}?type={kind}") or []:
                if hit.get("type") == kind:
                    return hit[kind]
        return None


def load_zip(path):
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            base = name.rsplit("/", 1)[-1]
            if "/data_in_csv/" not in name and base.endswith(".json"):
                out[base[:-5]] = json.loads(z.read(name))
    return out


def convert(data, trakt):
    fichas = data["fichas"]
    episodes = data["episodes"]
    seasons = data["seasons"]
    by_ficha = {}
    for ep in episodes:
        by_ficha.setdefault(ep["fichaId"], []).append(ep)
    season_ratings = {}
    for s in seasons:
        season_ratings.setdefault(s["fichaId"], []).append(s)

    shows = {k: [] for k in ("cH", "cW", "cHid", "pEp", "pSe", "pP", "pOH", "rS", "rSe", "rEp")}
    movies = {k: [] for k in ("cH", "cW", "cHid", "pP", "rM")}
    report = {"no_encontrados_en_trakt": [], "episodios_sin_match": [], "solo_nota_sin_coleccion": [],
              "importados": {}}

    for i, f in enumerate(fichas, 1):
        kind_raw, _, tmdb = f["idTheMovieDB"].partition("/")
        kind = "show" if kind_raw == "tv" else "movie"
        print(f"[{i}/{len(fichas)}] {f['title']} ({kind})", file=sys.stderr)
        ids = trakt.find(kind, tmdb, f["idImdb"])
        if not ids:
            report["no_encontrados_en_trakt"].append(f"{f['title']} ({f['year']}) {f['idImdb']}")
            continue
        tid = ids["ids"]["trakt"]
        tmid = ids["ids"].get("tmdb") or int(tmdb or 0)
        rating = to_showly_rating(f["rating"])
        added = iso(f["markDateUnix"])

        if kind == "movie":
            col = collection_for(f["mark"], False)
            if col:
                movies[col].append({"id": tid, "tmId": tmid, "t": f["title"], "a": added})
            elif rating:
                report["solo_nota_sin_coleccion"].append(f["title"])
            if rating:
                movies["rM"].append({"id": tid, "tmId": tmid, "r": rating, "rA": iso(f["ratingDateUnix"])})
            continue

        eps = by_ficha.get(f["id"], [])
        viewed = [e for e in eps if e["viewed"]]
        col = collection_for(f["mark"], bool(viewed))
        rated_eps = [e for e in eps if e["rating"]]
        srat = season_ratings.get(f["id"], [])

        # Solo pedimos temporadas/episodios a Trakt si hay algo que mapear
        ep_ids, season_ids = {}, {}
        if viewed or rated_eps or srat:
            for s in trakt.get(f"/shows/{tid}/seasons?extended=episodes") or []:
                season_ids[s["number"]] = s["ids"]["trakt"]
                for e in s.get("episodes") or []:
                    ep_ids[(e["season"], e["number"])] = e["ids"]["trakt"]

        if col:
            last_watch = max((e["viewedDateUnix"] for e in viewed), default=f["markDateUnix"])
            shows[col].append({"id": tid, "tmId": tmid, "t": f["title"], "a": added, "u": iso(last_watch)})
            if f["mark"] == "favorite":
                shows["pP"].append(tid)  # favorito -> fijado arriba en Progreso
        elif rating or rated_eps:
            report["solo_nota_sin_coleccion"].append(f["title"])

        if col == "cH":
            watched_seasons = set()
            for e in viewed:
                key = (e["season"], e["episode"])
                if key not in ep_ids:
                    report["episodios_sin_match"].append(f"{f['title']} S{key[0]:02d}E{key[1]:02d} (visto)")
                    continue
                watched_seasons.add(e["season"])
                shows["pEp"].append({"id": ep_ids[key], "sId": tid, "stmId": tmid, "eN": e["episode"],
                                     "sN": e["season"], "a": iso(e["viewedDateUnix"])})
            for sn in sorted(watched_seasons):
                if sn in season_ids:  # Showly solo la marca vista si cuadra el nº de episodios
                    shows["pSe"].append({"id": season_ids[sn], "sId": tid, "stmId": tmid, "sN": sn})

        if rating:
            shows["rS"].append({"id": tid, "tmId": tmid, "r": rating, "rA": iso(f["ratingDateUnix"])})
        for s in srat:
            r = to_showly_rating(s["rating"])
            if r and s["season"] in season_ids:
                shows["rSe"].append({"id": season_ids[s["season"]], "sId": tid, "stmId": tmid,
                                     "sN": s["season"], "r": r, "rA": iso(s["ratingDateUnix"])})
        for e in rated_eps:
            key = (e["season"], e["episode"])
            if key not in ep_ids:
                report["episodios_sin_match"].append(f"{f['title']} S{key[0]:02d}E{key[1]:02d} (nota)")
                continue
            shows["rEp"].append({"id": ep_ids[key], "sId": tid, "stmId": tmid, "sN": e["season"],
                                 "eN": e["episode"], "r": to_showly_rating(e["rating"]),
                                 "rA": iso(e["ratingDateUnix"])})

    report["importados"] = {"series": {k: len(v) for k, v in shows.items()},
                            "peliculas": {k: len(v) for k, v in movies.items()}}
    backup = {"version": 2, "platform": "android", "createdAt": iso(None),
              "shows": shows, "movies": movies, "lists": {"l": []}}
    return backup, report


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    client_id = os.environ.get("TRAKT_CLIENT_ID")
    if not client_id:
        sys.exit("Falta TRAKT_CLIENT_ID (crea una app gratis en https://trakt.tv/oauth/applications)")
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "output")
    out_dir.mkdir(parents=True, exist_ok=True)
    backup, report = convert(load_zip(sys.argv[1]), Trakt(client_id, out_dir / "trakt_cache.json"))
    (out_dir / "showly_backup_from_playmax.json").write_text(json.dumps(backup, ensure_ascii=False))
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report["importados"], indent=2))
    print(f"No encontrados: {len(report['no_encontrados_en_trakt'])} | "
          f"episodios sin match: {len(report['episodios_sin_match'])}")


if __name__ == "__main__":
    main()
