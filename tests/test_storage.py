import tempfile
import unittest
from pathlib import Path

from ayacucho.storage import load_favoritos, save_favoritos


class TestStorage(unittest.TestCase):
    def test_guardar_y_cargar(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "favoritos.json"
            save_favoritos({"A", "B"}, ruta)
            self.assertEqual(load_favoritos(ruta), {"A", "B"})

    def test_cargar_archivo_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "no_existe.json"
            self.assertEqual(load_favoritos(ruta), set())

    def test_cargar_archivo_corrupto(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "favoritos.json"
            ruta.write_text("{no es json", encoding="utf-8")
            self.assertEqual(load_favoritos(ruta), set())

    def test_cargar_datos_no_lista(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "favoritos.json"
            ruta.write_text('{"clave": "valor"}', encoding="utf-8")
            self.assertEqual(load_favoritos(ruta), set())


if __name__ == "__main__":
    unittest.main()