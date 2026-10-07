"""Registro y persistencia del perfil del usuario."""
import json
from pathlib import Path

RUTA_USUARIO = Path(__file__).resolve().parent.parent / "usuario.json"
EDAD_MINIMA = 18


def cargar_usuario(ruta=RUTA_USUARIO):
    if not Path(ruta).exists():
        return None
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(datos, dict) or not datos.get("nombre"):
        return None
    edad = datos.get("edad")
    if not isinstance(edad, int) or edad < EDAD_MINIMA:
        return None
    return datos


def guardar_usuario(usuario, ruta=RUTA_USUARIO):
    Path(ruta).write_text(
        json.dumps(usuario, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return ruta


def eliminar_usuario(ruta=RUTA_USUARIO):
    if Path(ruta).exists():
        Path(ruta).unlink()