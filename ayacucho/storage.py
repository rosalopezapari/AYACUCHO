"""Persistencia de favoritos en un archivo JSON."""
import json
from pathlib import Path

RUTA_FAVORITOS = Path(__file__).resolve().parent.parent / "favoritos.json"


def load_favoritos(ruta=RUTA_FAVORITOS):
    if not Path(ruta).exists():
        return set()
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        return set()
    return set(datos) if isinstance(datos, list) else set()


def save_favoritos(favoritos, ruta=RUTA_FAVORITOS):
    Path(ruta).write_text(
        json.dumps(sorted(favoritos), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )