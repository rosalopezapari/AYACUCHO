import tempfile
import unittest
from pathlib import Path

from ayacucho.usuario import EDAD_MINIMA, cargar_usuario, eliminar_usuario, guardar_usuario


class TestUsuario(unittest.TestCase):
    def test_guardar_y_cargar(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "usuario.json"
            usuario = {"nombre": "Ana Torres", "edad": 30, "pais": "Perú", "ciudad": "Lima"}
            guardar_usuario(usuario, ruta)
            self.assertEqual(cargar_usuario(ruta), usuario)

    def test_cargar_archivo_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "no_existe.json"
            self.assertIsNone(cargar_usuario(ruta))

    def test_cargar_corrupto_devuelve_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "usuario.json"
            ruta.write_text("{corrupto", encoding="utf-8")
            self.assertIsNone(cargar_usuario(ruta))

    def test_cargar_sin_nombre_devuelve_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "usuario.json"
            ruta.write_text('{"edad": 20, "pais": "Perú"}', encoding="utf-8")
            self.assertIsNone(cargar_usuario(ruta))

    def test_cargar_menor_de_edad_devuelve_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "usuario.json"
            ruta.write_text('{"nombre": "Menor", "edad": 15}', encoding="utf-8")
            self.assertIsNone(cargar_usuario(ruta))

    def test_edad_minima(self):
        self.assertEqual(EDAD_MINIMA, 18)

    def test_eliminar_borra_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "usuario.json"
            guardar_usuario({"nombre": "X", "edad": 20}, ruta)
            eliminar_usuario(ruta)
            self.assertFalse(ruta.exists())


if __name__ == "__main__":
    unittest.main()