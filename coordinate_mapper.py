"""
coordinate_mapper.py
--------------------
Converts LILA BLACK world coordinates (x, z) to minimap pixel coordinates.
"""

import numpy as np
import pandas as pd
from pathlib import Path

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

IMAGE_SIZE = 1024


def _find_image(filename: str) -> Path | None:
    """Search several possible locations for the minimap image."""
    candidates = [
        Path(filename),                          # root of repo
        Path("assets") / "minimaps" / filename, # assets/minimaps/
        Path("assets") / filename,               # assets/
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def world_to_pixel(x, z, map_name: str):
    cfg = MAP_CONFIG[map_name]
    x = np.asarray(x, dtype=float)
    z = np.asarray(z, dtype=float)
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    pixel_x = u * IMAGE_SIZE
    pixel_y = (1 - v) * IMAGE_SIZE
    return pixel_x, pixel_y


def add_pixel_coords(df: pd.DataFrame, map_name: str) -> pd.DataFrame:
    map_df = df[df["map_name"] == map_name].copy()
    px, py = world_to_pixel(map_df["x"].values, map_df["z"].values, map_name)
    map_df["pixel_x"] = px
    map_df["pixel_y"] = py
    return map_df


def get_minimap_path(map_name: str) -> Path | None:
    if map_name not in MAP_CONFIG:
        return None
    return _find_image(MAP_CONFIG[map_name]["image_file"])
