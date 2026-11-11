# Playmax → Showly

<p align="center"><a href="README.md">Español</a> · <b>English</b></p>

Converts your **Playmax** data export (`.zip`) into a **JSON backup that Showly imports** from *Settings → Backup → Import*: shows, movies, watched episodes, watchlist, dropped, favorites and ratings.

Python 3.10+, no dependencies. Requires a **Trakt Client ID** (free).

> Playmax is a Spanish-language movie and TV social network; its UI terms (e.g. *Siguiendo*, *Pendiente*) are kept in Spanish below where they refer to its export.

---

## Quick summary

| | What |
|---|---|
| ✅ **Imported** | Shows you follow or have watched, watchlist, dropped, favorites, every watched episode (with date), watched/watchlist/dropped movies, show, season, episode and movie ratings |
| ⚠️ **Imported, adapted** | Dropped → Hidden · Favorite → Pinned (shows) or Watched (movies) · Half-point ratings → rounded up |
| ✋ **Manual** | Episodes Trakt numbers differently (listed in `report.json`) · Items with a rating but no status · Shows you want "On hold" |
| ❌ **Not possible** | Comments · Movie favorites · Half-point ratings · Playmax lists, folders, chats and messages |

---

## What Playmax exports

The Playmax ZIP (*Profile → Settings → Export data*) contains every table as JSON and as CSV (`data_in_csv/`). The script reads the JSON files:

| File | Contents | Used? |
|---|---|---|
| `fichas.json` | Every show/movie with its status (`mark`), rating, date and TMDB/IMDb IDs | ✅ |
| `episodes.json` | Episodes: watched yes/no, date, rating | ✅ |
| `seasons.json` | Season ratings | ✅ |
| `comments.json` | Your comments on titles | ❌ Showly has no comments |
| `lists.json`, `folders.json`, `following_lists.json`, `rated_lists.json` | Lists and folders | ❌ Not converted (see below) |
| `chats.json`, `privates_messages.json`, `news.json`, `user_data.json`, avatar | Messages, profile | ❌ No equivalent |

## What Showly imports

Showly **does not store a "status"** like Playmax. It organizes items into **collections** and derives the rest from watched episodes:
- A show in "My Shows" with unwatched episodes appears under **Progress**.
- If every episode is watched, Showly treats it as finished.

### Status mapping

**Shows**

| Playmax status | In Showly | Backup code |
|---|---|---|
| *Siguiendo* (following) | My Shows + Progress | `cH` + `pEp` |
| *Vista* (watched) | My Shows (finished, because every episode is watched) | `cH` + `pEp` |
| *Pendiente* (watchlist) | Watchlist | `cW` |
| *Abandonada* (dropped) | Hidden (there's no "dropped") | `cHid` |
| *Favorita* (favorite) | My Shows + pinned at the top of Progress (there's no "favorite") | `cH` + `pP` |
| No status, with watched episodes | My Shows, so progress isn't lost | `cH` + `pEp` |
| Watchlist, with watched episodes | My Shows (the Watchlist doesn't keep progress) | `cH` + `pEp` |
| No status and no episodes | Only the rating is imported, if any | `rS` |
| — (doesn't exist in Playmax) | On hold | `pOH` (empty) |

**Movies**

| Playmax status | In Showly | Backup code |
|---|---|---|
| *Vista* (watched) | My Movies / history | `cH` |
| *Pendiente* (watchlist) | Watchlist | `cW` |
| *Abandonada* (dropped) | Hidden | `cHid` |
| *Favorita* (favorite) | Watched (there are no movie favorites) | `cH` |
| No status | Only the rating, if any | `rM` |

### Ratings

| Playmax | Showly | Conversion |
|---|---|---|
| 0–10 with half points, 0 = unrated | Integers 1–10 | Half point rounds up: 7.5 → 8 · 0.5 → 1 · 0 → not exported |

---

## The codes at the end (what each one means)

When it finishes, the script prints a count like this:

```json
{
  "series":    { "cH": …, "cW": …, "cHid": …, "pEp": …, "pSe": …, "pP": …, "pOH": …, "rS": …, "rSe": …, "rEp": … },
  "peliculas": { "cH": …, "cW": …, "cHid": …, "pP": …, "rM": … }
}
No encontrados: N | episodios sin match: N
```

(`series` = shows, `peliculas` = movies, `No encontrados` = not found, `episodios sin match` = unmatched episodes.)

These are the **short keys Showly uses in its backup file**. The script doesn't invent them: they come from Showly's source code (`ui-backup/.../model/BackupShows.kt` and `BackupMovies.kt`). Each number is how many items go into that section.

The first letter is the kind of data: **c** = collection, **p** = progress, **r** = rating.

| Code | Name in Showly's code | What it is in the app | Shows | Movies |
|---|---|---|---|---|
| `cH` | `collectionHistory` | **My Shows / My Movies** (what you follow or have watched) | ✅ | ✅ |
| `cW` | `collectionWatchlist` | **Watchlist** | ✅ | ✅ |
| `cHid` | `collectionHidden` | **Hidden** (dropped items go here) | ✅ | ✅ |
| `pEp` | `progressEpisodes` | **Watched episodes**, with date | ✅ | — |
| `pSe` | `progressSeasons` | **Watched seasons**. Showly only marks one if all its episodes match | ✅ | — |
| `pP` | `progressPinned` | **Pinned** at the top of Progress (favorites go here) | ✅ | ✅ (empty) |
| `pOH` | `progressOnHold` | **On hold** (Playmax has no equivalent, left empty) | ✅ | — |
| `rS` | `ratingsShows` | **Show** ratings | ✅ | — |
| `rSe` | `ratingsSeasons` | **Season** ratings | ✅ | — |
| `rEp` | `ratingsEpisodes` | **Episode** ratings | ✅ | — |
| `rM` | `ratingsMovies` | **Movie** ratings | — | ✅ |

The two last lines:
- **Not found** (`No encontrados`): titles Trakt returned no ID for. Showly couldn't download them, so they're left out of the backup.
- **Unmatched episodes** (`episodios sin match`): watched or rated episodes whose number (season × episode) doesn't exist on Trakt. Usually specials and TV movies numbered differently.

Details for both are in `output/report.json`:

| Key in `report.json` | Meaning | What to do |
|---|---|---|
| `no_encontrados_en_trakt` | Titles without a Trakt ID | Add them manually in Showly |
| `episodios_sin_match` | Episodes with no match on Trakt (`(visto)` = watched, `(nota)` = rated) | Mark them manually. They're usually under "Specials" |
| `solo_nota_sin_coleccion` | Titles with a rating but no status in Playmax | Optional: add them to whichever collection you want |
| `importados` | The same code count as above | Compare with what Showly shows after importing |

---

## ✋ What you have to do manually

1. **Episodes in `episodios_sin_match`:** mark them as watched in Showly. If they're not in their season, look under *Specials* (season 0).
2. **Titles in `no_encontrados_en_trakt`:** search for them and add them in Showly.
3. **Items in `solo_nota_sin_coleccion`:** the rating is imported, but they don't go into any collection. Add them if you want to see them.
4. **"On hold":** if a show you were following is actually paused, put it on hold in Showly.

## ❌ What isn't possible (and why)

| Data | Why not |
|---|---|
| Comments | Showly's backup has no text or comment field |
| Movie favorites | Showly has no "favorite", and "pinned" makes no sense for watched movies |
| Telling "following" from "watched" apart | Showly doesn't store the label, it derives it from episodes (the result is the same) |
| Half-point ratings | Showly only accepts integers 1–10 |
| Playmax lists and folders | Showly lists are Trakt lists and the script doesn't create them. See *Possible improvements* |
| Chats, messages, news, profile | They don't exist in Showly |
| Date you marked "watchlist" vs. "following" | Showly keeps a single "added" date |

---

## Usage

### 1. Trakt Client ID

Showly identifies everything by **Trakt ID**, and Playmax only exports TMDB and IMDb IDs, so the script asks the Trakt API.

1. Go to https://app.trakt.tv/settings/apps/api/new with your Trakt account.
2. **App name:** anything · **App type:** Development · **Redirect URIs:** `http://localhost` · leave the rest empty.
3. Create the app and copy the **Client ID**. You don't need the *Client Secret*: don't share it.

### 2. Convert

```bash
read -s -p "Trakt Client ID: " TRAKT_CLIENT_ID && export TRAKT_CLIENT_ID && echo
```

```bash
python3 -I playmax_to_showly.py /path/to/playmax-userdata-XX.zip output
```

It takes a few minutes. If it stops, run it again: `output/trakt_cache.json` avoids repeating requests.

It creates in `output/`:
- `showly_backup_from_playmax.json`: the file to import.
- `report.json`: what couldn't be mapped, plus the counts.
- `trakt_cache.json`: Trakt cache, safe to delete.

> ⚠️ `output/` contains your whole viewing history. It's in `.gitignore`: don't upload it.

### 3. Copy it to your phone

Put it in your phone's *Downloads* folder (cable, cloud, etc.). With ADB:

```bash
adb push output/showly_backup_from_playmax.json /sdcard/Download/
```

### 4. Import in Showly

*Settings → Backup → Import* → pick the file. Showly downloads every title from Trakt, so it takes a while. When it's done, compare with `importados` in `report.json`.

## Test

```bash
python3 -I test_convert.py
```

No network: it replaces Trakt with a fake and checks rating rounding, status mapping, dates and the report.

## How the format was worked out

- **Playmax:** ZIP inventory with [REA](https://github.com/morluto/rea) and reading the JSON files.
- **Showly:** its backup has no documentation. Its source code was read ([trakt/showly](https://github.com/trakt/showly), formerly `michaldrabik/showly-2.0`): the models (`BackupScheme`, `BackupShows`, `BackupMovies`) and, above all, the importers (`BackupImportShowsRunner`, `BackupImportMoviesRunner`), which show what the app does with each field.

## Possible improvements

- Create a "Favorites" list in the backup (`lists.l`) so movie favorites aren't lost.
- Search unmatched episodes by title.
- Upload the history straight to Trakt (`/sync/history`) instead of generating a backup.

## Documentation

The step-by-step learning docs in [`docs/`](docs/) are in Spanish.
