# AURELIA TERMINUS — The Poster for a Place That Isn't There

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/butterscotchcode/aurelia-terminus-poster/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/butterscotchcode/aurelia-terminus-poster/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

Entry for the [make.fun](https://make.fun) competition
**The Poster for a Place That Isn't There**
(`the-poster-for-a-place-that-i-2-20261121-0539`).

## The place

**Aurelia Terminus** — the last station on Earth, where the aurora comes
down out of the sky and rests on the platform. One landmark (the art-deco
clock-tower station, ten past ten, every window lit), one promise (a warm
night under the aurora), one traveller with a suitcase walking up the
snow path to the door.

## How it works

`main.py` (Python 3.13, standard library + Pillow) renders the poster
fully procedurally — sky gradient, stars, moon, aurora ribbons, mountains,
pines, station, train, lamps, snow path and traveller — with no network
and no downloaded assets. The fonts ship in the repo (`fonts/`, DejaVu,
freely licensed). Output is deterministic: two runs produce a
byte-identical file.

```bash
python3 main.py   # writes /output/entry.png (768x1024, ~273 KB)
```

## Layout

- `main.py` — the poster program (entrypoint)
- `fonts/` — DejaVu Serif Bold + DejaVu Sans (bundled so the sandbox
  render matches the local one)
- `LICENSE` — MIT

## Verification

- Two runs: byte-identical PNG (`md5` match)
- Size 272,971 bytes (limit 1,048,576), 768×1024 px (limit 1024×1024)
- Runtime ~2 s (limit 60 s), no network
