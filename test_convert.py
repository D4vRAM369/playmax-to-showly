"""Test mínimo sin red: Trakt simulado. Ejecutar: python3 -I test_convert.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from playmax_to_showly import collection_for, convert, iso, to_showly_rating  # noqa: E402


class FakeTrakt:
    def find(self, kind, tmdb, imdb):
        return None if imdb == "tt404" else {"ids": {"trakt": int(tmdb) + 1000, "tmdb": int(tmdb)}}

    def get(self, path):  # 1 temporada con 2 episodios
        return [{"number": 1, "ids": {"trakt": 77}, "episodes": [
            {"season": 1, "number": 1, "ids": {"trakt": 701}},
            {"season": 1, "number": 2, "ids": {"trakt": 702}}]}]


def ficha(id_, kind, mark, rating=0, imdb="tt1"):
    return {"id": id_, "title": f"T{id_}", "year": 2000, "idImdb": imdb, "idTheMovieDB": f"{kind}/{id_}",
            "mark": mark, "markDateUnix": 1679171524, "rating": rating, "ratingDateUnix": 1679171524}


assert to_showly_rating(0) is None and to_showly_rating(7.5) == 8 and to_showly_rating(0.5) == 1
assert to_showly_rating(10) == 10 and to_showly_rating(6.5) == 7
assert collection_for("pending", True) == "cH" and collection_for("abandoned", True) == "cHid"
assert collection_for("", False) is None and collection_for("pending", False) == "cW"
assert iso(0).endswith("Z") and iso(1679171524) == "2023-03-18T20:32:04.000Z"

data = {
    "fichas": [ficha(1, "tv", "following", 9.5), ficha(2, "movie", "viewed", 7.5), ficha(3, "movie", "pending"),
               ficha(4, "tv", "favorite"), ficha(5, "tv", "pending", imdb="tt404"), ficha(6, "movie", "", 6)],
    "episodes": [{"fichaId": 1, "season": 1, "episode": 1, "viewed": True, "viewedDateUnix": 1700000000,
                  "rating": 8, "ratingDateUnix": 1700000000},
                 {"fichaId": 1, "season": 1, "episode": 9, "viewed": True, "viewedDateUnix": 1700000000,
                  "rating": 0, "ratingDateUnix": 0}],
    "seasons": [{"fichaId": 1, "season": 1, "rating": 10, "ratingDateUnix": 1700000000}],
}
b, rep = convert(data, FakeTrakt())
s, m = b["shows"], b["movies"]
assert b["version"] == 2 and b["platform"] == "android"
assert [x["id"] for x in s["cH"]] == [1001, 1004] and s["pP"] == [1004]
assert s["pEp"] == [{"id": 701, "sId": 1001, "stmId": 1, "eN": 1, "sN": 1, "a": iso(1700000000)}]
assert s["rS"][0]["r"] == 10 and s["rSe"][0]["id"] == 77 and s["rEp"][0]["id"] == 701
assert [x["id"] for x in m["cH"]] == [1002] and [x["id"] for x in m["cW"]] == [1003]
assert [x["r"] for x in m["rM"]] == [8, 6] and rep["solo_nota_sin_coleccion"] == ["T6"]
assert len(rep["no_encontrados_en_trakt"]) == 1 and rep["episodios_sin_match"] == ["T1 S01E09 (visto)"]
print("OK")
