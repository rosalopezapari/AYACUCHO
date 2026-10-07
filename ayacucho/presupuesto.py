"""Administración del presupuesto de viaje del usuario."""
import json
from pathlib import Path

RUTA_PRESUPUESTO = Path(__file__).resolve().parent.parent / "presupuesto.json"
CATEGORIAS = ["Alojamiento", "Comida", "Transporte", "Atracciones", "Compras", "Otros"]


def presupuesto_vacio():
    return {"presupuesto_total": 0.0, "gastos": []}


def cargar_presupuesto(ruta=RUTA_PRESUPUESTO):
    if not Path(ruta).exists():
        return presupuesto_vacio()
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except (json.JSONDecodeError, OSError):
        return presupuesto_vacio()
    if not isinstance(datos, dict) or "gastos" not in datos:
        return presupuesto_vacio()
    datos.setdefault("presupuesto_total", 0.0)
    datos["presupuesto_total"] = float(datos.get("presupuesto_total") or 0.0)
    datos["gastos"] = [
        g
        for g in datos["gastos"]
        if isinstance(g, dict)
        and g.get("concepto")
        and g.get("monto") is not None
    ]
    for gasto in datos["gastos"]:
        gasto["monto"] = float(gasto.get("monto") or 0.0)
        gasto.setdefault("categoria", "Otros")
    return datos


def guardar_presupuesto(datos, ruta=RUTA_PRESUPUESTO):
    Path(ruta).write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return ruta


def eliminar_presupuesto(ruta=RUTA_PRESUPUESTO):
    if Path(ruta).exists():
        Path(ruta).unlink()


def total_gastado(datos):
    return round(sum(float(g.get("monto") or 0.0) for g in datos["gastos"]), 2)


def presupuesto_restante(datos):
    return round(float(datos.get("presupuesto_total") or 0.0) - total_gastado(datos), 2)