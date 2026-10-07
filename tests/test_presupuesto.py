import json
import os
import tempfile
import unittest
from pathlib import Path

from ayacucho.presupuesto import (
    CATEGORIAS,
    cargar_presupuesto,
    eliminar_presupuesto,
    guardar_presupuesto,
    presupuesto_restante,
    presupuesto_vacio,
    total_gastado,
)


class TestPresupuesto(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self._tmp.name, "presupuesto.json")

    def tearDown(self):
        self._tmp.cleanup()

    def test_vacio_sin_archivo(self):
        datos = cargar_presupuesto(self.ruta)
        self.assertEqual(datos, {"presupuesto_total": 0.0, "gastos": []})

    def test_guardar_y_cargar(self):
        datos = {
            "presupuesto_total": 500.0,
            "gastos": [{"concepto": "Hotel", "categoria": "Alojamiento", "monto": 120.0}],
        }
        guardar_presupuesto(datos, self.ruta)
        cargado = cargar_presupuesto(self.ruta)
        self.assertEqual(cargado["presupuesto_total"], 500.0)
        self.assertEqual(cargado["gastos"][0]["concepto"], "Hotel")

    def test_archivo_corrupto_devuelve_vacio(self):
        Path(self.ruta).write_text("no json", encoding="utf-8")
        self.assertEqual(cargar_presupuesto(self.ruta), presupuesto_vacio())

    def test_gastos_invalidos_se_descartan(self):
        datos = {
            "presupuesto_total": 100.0,
            "gastos": [
                {"concepto": "Bus", "monto": 20.0},
                {},
                {"concepto": "", "monto": 5.0},
                {"monto": 10.0},
            ],
        }
        guardar_presupuesto(datos, self.ruta)
        cargado = cargar_presupuesto(self.ruta)
        self.assertEqual(len(cargado["gastos"]), 1)
        self.assertEqual(cargado["gastos"][0]["categoria"], "Otros")

    def test_total_gastado_y_restante(self):
        datos = {
            "presupuesto_total": 500.0,
            "gastos": [
                {"concepto": "Hotel", "categoria": "Alojamiento", "monto": 120.5},
                {"concepto": "Comida", "categoria": "Comida", "monto": 30.0},
            ],
        }
        self.assertEqual(total_gastado(datos), 150.5)
        self.assertEqual(presupuesto_restante(datos), 349.5)

    def test_excedido(self):
        datos = {
            "presupuesto_total": 100.0,
            "gastos": [{"concepto": "Tour", "categoria": "Atracciones", "monto": 150.0}],
        }
        self.assertEqual(presupuesto_restante(datos), -50.0)

    def test_eliminar_presupuesto(self):
        guardar_presupuesto(presupuesto_vacio(), self.ruta)
        eliminar_presupuesto(self.ruta)
        self.assertFalse(Path(self.ruta).exists())

    def test_categorias_disponibles(self):
        self.assertEqual(
            CATEGORIAS, ["Alojamiento", "Comida", "Transporte", "Atracciones", "Compras", "Otros"]
        )


if __name__ == "__main__":
    unittest.main()