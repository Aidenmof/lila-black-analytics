"""
coordinate_mapper.py
--------------------
Converts LILA BLACK world coordinates (x, z) to minimap pixel coordinates.

The formula (from the README):
  u = (x - origin_x) / scale
  v = (z - origin_z) / scale
  pixel_x = u * 1024
  pixel_y = (1 - v) * 1024     ← Y is flipped because image origin is top-left

NOTE: We use x and z from your data. The y column is elevation (height in 3D)
and is ignored for 2D minimap plotting.

All three map configs are already filled in from the README — no editing needed.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ── Map configuration (pre-filled from your README) ─────────────────────────
MAP_CONFIG = {
    "AmbroseValley": {
        "scale":    900,
        "origin_x": -370,
        "origin_z": -473,
        "image_file": "AmbroseValley_Minimap.png",
    },
    "GrandRift": {
        "scale":    581,
        "origin_x": -290,
        "origin_z": -290,
        "image_file": "GrandRift_Minimap.png",
    },
    "Lockdown": {
        "scale":    1000,
        "origin_x": -500,
        "origin_z": -500,
        "image_file": "Lockdown_Minimap.jpg",
    },
}

IMAGE_SIZE = 1024   # all minimaps are 1024×1024

ASSETS_DIR = Path("assets") / "minimaps"


def world_to_pixel(
    x: float | np.ndarray,
    z: float | np.ndarray,
    map_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert world (x, z) coordinates to pixel (px, py) on the 1024×1024 minimap.

    Formula from the LILA BLACK README:
      u = (x - origin_x) / scale
      v = (z - origin_z) / scale
      pixel_x = u * 1024
      pixel_y = (1 - v) * 1024
    """
    cfg = MAP_CONFIG[map_name]
    x = np.asarray(x, dtype=float)
    z = np.asarray(z, dtype=float)

    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]

    pixel_x = u * IMAGE_SIZE
    pixel_y = (1 - v) * IMAGE_SIZE

    return pixel_x, pixel_y


def add_pixel_coords(df: pd.DataFrame, map_name: str) -> pd.DataFrame:
    """
    Filter df to the given map and add pixel_x, pixel_y columns.
    Returns the filtered + augmented DataFrame.
    """
    map_df = df[df["map_name"] == map_name].copy()
    px, py = world_to_pixel(map_df["x"].values, map_df["z"].values, map_name)
    map_df["pixel_x"] = px
    map_df["pixel_y"] = py
    return map_df


def get_minimap_path(map_name: str) -> Path | None:
    """Return path to the minimap image, or None if not found."""
    if map_name not in MAP_CONFIG:
        return None
    p = ASSETS_DIR / MAP_CONFIG[map_name]["image_file"]
    return p if p.exists() else None
