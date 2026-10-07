import json
import tempfile
import unittest
from pathlib import Path

from ayacucho import rutas


class TestRutas(unittest.TestCase):
    def test_normalizar_exige_dos_paradas_con_gps(self):
        valida = {
            "titulo": "Ruta 1",
            "paradas": [
                {"lugar": "A", "lat": -13.1, "lng": -74.2},
                {"lugar": "B", "lat": -13.2, "lng": -74.3},
            ],
        }
        self.assertIsNotNone(rutas.normalizar(valida))
        self.assertIsNone(rutas.normalizar({"titulo": "R", "paradas": valida["paradas"][:1]}))
        self.assertIsNone(rutas.normalizar({"paradas": valida["paradas"]}))
        self.assertIsNone(rutas.normalizar({"titulo": "R", "paradas": [{"lugar": "A"}]}))

    def test_ruta_desde_itinerario(self):
        from ayacucho.datos import ITINERARIOS

        for itinerario in ITINERARIOS:
            with self.subTest(titulo=itinerario["titulo"]):
                ruta = rutas.ruta_desde_itinerario(itinerario)
                self.assertEqual(ruta["titulo"], itinerario["titulo"])
                self.assertGreaterEqual(len(ruta["paradas"]), 2)
                self.assertTrue(ruta["creado"])

    def test_guardar_cargar_y_reemplazar(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "rutas.json"
            nueva = {
                "titulo": "Ruta Express",
                "paradas": [
                    {"lugar": "A", "lat": -13.1, "lng": -74.2},
                    {"lugar": "B", "lat": -13.2, "lng": -74.3},
                ],
            }
            guardadas = rutas.agregar_ruta(nueva, ruta=archivo)
            self.assertEqual(len(guardadas), 1)
            self.assertEqual(len(rutas.cargar_rutas(archivo)), 1)
            rutas.agregar_ruta(nueva, ruta=archivo)
            self.assertEqual(len(rutas.cargar_rutas(archivo)), 1)
            otra = dict(nueva, titulo="Ruta Cultural")
            rutas.agregar_ruta(otra, ruta=archivo)
            self.assertEqual(len(rutas.cargar_rutas(archivo)), 2)
            self.assertEqual(len(rutas.eliminar_ruta("Ruta Express", ruta=archivo)), 1)

    def test_ignora_rutas_invalidas_al_cargar(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "rutas.json"
            archivo.write_text(
                json.dumps(
                    [
                        {"titulo": "Sin paradas", "paradas": []},
                        {
                            "titulo": "Buena",
                            "paradas": [
                                {"lugar": "A", "lat": -13.1, "lng": -74.2},
                                {"lugar": "B", "lat": -13.2, "lng": -74.3},
                            ],
                        },
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(len(rutas.cargar_rutas(archivo)), 1)

    def test_cargar_archivo_inexistente_o_corrupto(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rutas.cargar_rutas(Path(tmp) / "no.json"), [])
            roto = Path(tmp) / "rotas.json"
            roto.write_text("{no es json", encoding="utf-8")
            self.assertEqual(rutas.cargar_rutas(roto), [])
            otro = Path(tmp) / "dic.json"
            otro.write_text('{"titulo": "x"}', encoding="utf-8")
            self.assertEqual(rutas.cargar_rutas(otro), [])

    def test_distancia_total_y_url(self):
        ruta = {
            "titulo": "R",
            "paradas": [
                {"lugar": "A", "lat": -13.158786, "lng": -74.223974},
                {"lugar": "B", "lat": -13.652700, "lng": -73.913700},
            ],
        }
        self.assertGreater(rutas.distancia_total(ruta), 50)
        self.assertIn("maps/dir/", rutas.url_de_ruta(ruta))


if __name__ == "__main__":
    unittest.main()
