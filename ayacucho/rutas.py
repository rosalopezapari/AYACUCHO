"""Persistencia de itinerarios y rutas guardadas por el usuario."""
import json
from datetime import date
from pathlib import Path

from ayacucho.gps import distancia, url_ruta

RUTA_RUTAS = Path(__file__).resolve().parent.parent / "rutas.json"


def parada_valida(parada):
    if not isinstance(parada, dict):
        return False
    if not parada.get("lugar"):
        return False
    try:
        float(parada.get("lat")), float(parada.get("lng"))
    except (TypeError, ValueError):
        return False
    return True


def normalizar(ruta):
    """Devuelve una ruta válida y normalizada, o None si no sirve."""
    if not isinstance(ruta, dict) or not ruta.get("titulo"):
        return None
    paradas = [dict(p) for p in ruta.get("paradas", []) if parada_valida(p)]
    if len(paradas) < 2:
        return None
    return {
        "titulo": str(ruta["titulo"]),
        "descripcion": str(ruta.get("descripcion", "")),
        "paradas": paradas,
        "creado": ruta.get("creado") or date.today().isoformat(),
    }


def ruta_desde_itinerario(itinerario):
    """Convierte un itinerario de datos.py en una ruta guardable."""
    return normalizar(
        {
            "titulo": itinerario["titulo"],
            "descripcion": itinerario.get("descripcion", ""),
            "paradas": itinerario.get("paradas_gps", []),
        }
    )


def cargar_rutas(ruta=RUTA_RUTAS):
    if not Path(ruta).exists():
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(datos, list):
        return []
    return [r for r in (normalizar(item) for item in datos) if r]


def guardar_rutas(rutas, ruta=RUTA_RUTAS):
    Path(ruta).write_text(
        json.dumps(list(rutas), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return ruta


def agregar_ruta(nueva, rutas=None, ruta=RUTA_RUTAS):
    """Agrega o reemplaza una ruta por titulo y devuelve la lista actualizada."""
    preparada = normalizar(nueva)
    if not preparada:
        return None
    if rutas is None:
        rutas = cargar_rutas(ruta)
    actualizadas = [r for r in rutas if r["titulo"] != preparada["titulo"]]
    actualizadas.append(preparada)
    guardar_rutas(actualizadas, ruta)
    return actualizadas


def eliminar_ruta(titulo, rutas=None, ruta=RUTA_RUTAS):
    if rutas is None:
        rutas = cargar_rutas(ruta)
    restantes = [r for r in rutas if r["titulo"] != titulo]
    guardar_rutas(restantes, ruta)
    return restantes


def url_de_ruta(ruta):
    """Enlace de Google Maps con todas las paradas de la ruta guardada."""
    return url_ruta(ruta.get("paradas", []))


def distancia_total(ruta):
    """Recorrido aproximado en km sumando el tramo entre paradas consecutivas."""
    paradas = ruta.get("paradas", [])
    total = 0.0
    for anterior, siguiente in zip(paradas, paradas[1:]):
        total += distancia(
            anterior["lat"], anterior["lng"], siguiente["lat"], siguiente["lng"]
        )
    return round(total, 1)
