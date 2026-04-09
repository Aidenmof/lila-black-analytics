# Architecture

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend + Backend | Streamlit | Single-file Python app, no separate frontend needed, fast to iterate, built-in hosting via Community Cloud |
| Data loading | PyArrow + Pandas | PyArrow reads parquet files without a `.parquet` extension; Pandas handles filtering and aggregation cleanly |
| Visualisation | Plotly | Interactive pan/zoom on the minimap out of the box; supports image backgrounds, scatter traces, and heatmap layers in one figure |
| Heatmaps | SciPy (Gaussian KDE) | Kernel density estimation gives smooth, continuous density surfaces from sparse event points — more readable than raw binning |
| Hosting | Streamlit Community Cloud | Free, deploys directly from GitHub, shareable public URL in under 2 minutes |

---

## Data Flow

```
data/
  February_10/ … February_14/
    {user_id}_{match_id}.nakama-0   ← valid parquet, no extension
          │
          ▼
    data_loader.py
    • Walk all date subfolders
    • Read each file with pyarrow.parquet.read_table()
    • Decode event column from bytes → string
    • Derive is_bot from user_id shape (UUID = human, numeric = bot)
    • Add date from folder name
    • Rename columns to internal standard names
    • Cache result with @st.cache_data
          │
          ▼
    filters.py  (sidebar widgets)
    • Filter by map, date range, match ID, player type
          │
          ▼
    coordinate_mapper.py
    • Convert world (x, z) → minimap pixel (px, py)
          │
          ├──▶ journey_plotter.py   → player path lines on minimap
          ├──▶ event_markers.py     → kill / death / loot / storm markers
          ├──▶ heatmap.py           → density overlays
          └──▶ timeline.py          → playback scrubber + live stats
          │
          ▼
    app.py  (Streamlit UI)
    Renders everything into 3 tabs:
      • Player Journeys (per-match, with timeline)
      • Heatmaps (aggregated across all filtered matches)
      • Stats (charts + top players table)
```

---

## Coordinate Mapping

This was the most precise part of the implementation.

The game uses a 3D world coordinate system `(x, y, z)` where `y` is elevation. For 2D minimap plotting, only `x` and `z` are used.

Each map has a known **origin** and **scale** (from the data README):

| Map | Scale | Origin X | Origin Z |
|-----|-------|----------|----------|
| AmbroseValley | 900 | -370 | -473 |
| GrandRift | 581 | -290 | -290 |
| Lockdown | 1000 | -500 | -500 |

The conversion is a two-step normalisation:

```
Step 1 — normalise to UV space (0.0 → 1.0):
  u = (x - origin_x) / scale
  v = (z - origin_z) / scale

Step 2 — scale to image pixels (1024×1024):
  pixel_x = u * 1024
  pixel_y = (1 - v) * 1024    ← Y is flipped: image origin is top-left,
                                  game Z increases upward
```

The Y-flip is the critical detail — without it, all positions appear mirrored vertically on the minimap.

---

## Assumptions

| Ambiguity | Assumption made |
|-----------|----------------|
| Files have no `.parquet` extension | PyArrow reads them by path regardless of extension — confirmed working |
| `event` column stored as bytes | Decoded with `.decode('utf-8')` on load |
| Bot detection | `user_id` matching UUID pattern → human; short numeric string → bot |
| `ts` timestamp meaning | Treated as milliseconds elapsed within the match (not wall-clock). Ordered by `ts` to reconstruct timeline |
| `y` column | Ignored for 2D plotting — represents elevation only |
| February 14 partial day | Included as-is; partial data is labelled in the date filter |

---

## Major Trade-offs

| Decision | Alternative considered | Why this way |
|----------|----------------------|--------------|
| Streamlit over React | React + FastAPI backend | Streamlit lets one person ship a working, hosted tool in hours. React would take days to wire up. |
| Load all data on startup | Query on demand | With ~89k rows the full dataset fits in memory easily. Caching makes repeat visits instant. |
| Plotly over Mapbox/Leaflet | Tile-based map library | Minimaps are static game images, not geo-tiles. Plotly's image background + scatter traces is the right fit. |
| KDE heatmap over hex-bin | Binned density grid | KDE produces smoother, more readable hotspot contours at this data density |
| Per-file loading | Single merged parquet | Data is provided as per-player files — this structure is preserved so individual player journeys are naturally isolated |
