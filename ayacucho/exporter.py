"""Exportación de la base de datos a JSON."""
import json
from pathlib import Path

from ayacucho.datos import (
    ARTESANIAS,
    ATRACCIONES,
    CLIMA,
    COMO_LLEGAR,
    CONSEJOS,
    EMERGENCIAS,
    EVENTOS_CULTURALES,
    FESTIVIDADES,
    GASTRONOMIA,
    IGLESIAS,
    ITINERARIOS,
    PLAZA_HUAMANGA,
    QUECHUA,
    todos_alojamientos,
    todos_comercios,
    todos_restaurantes,
)
from ayacucho.historias import HISTORIAS


def compilar_datos():
    return {
        "historias": HISTORIAS,
        "atracciones": ATRACCIONES,
        "gastronomia": GASTRONOMIA,
        "festividades": FESTIVIDADES,
        "artesanias": ARTESANIAS,
        "consejos": CONSEJOS,
        "alojamiento": todos_alojamientos(),
        "restaurantes": todos_restaurantes(),
        "comercios": todos_comercios(),
        "eventos_culturales": EVENTOS_CULTURALES,
        "clima": CLIMA,
        "como_llegar": COMO_LLEGAR,
        "itinerarios": ITINERARIOS,
        "plaza_huamanga": PLAZA_HUAMANGA,
        "iglesias": IGLESIAS,
        "emergencias": EMERGENCIAS,
        "quechua": QUECHUA,
    }


def exportar_datos(ruta="datos_ayacucho.json"):
    Path(ruta).write_text(
        json.dumps(compilar_datos(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return ruta