import json
import tempfile
import unittest
from pathlib import Path

from ayacucho.exporter import compilar_datos, exportar_datos


class TestExporter(unittest.TestCase):
    def test_compilar_incluye_todas_las_secciones(self):
        datos = compilar_datos()
        for seccion in (
            "historias",
            "atracciones",
            "gastronomia",
            "festividades",
            "artesanias",
            "consejos",
            "alojamiento",
            "restaurantes",
            "comercios",
            "eventos_culturales",
            "clima",
            "como_llegar",
            "itinerarios",
            "plaza_huamanga",
            "iglesias",
            "emergencias",
            "quechua",
        ):
            with self.subTest(seccion=seccion):
                self.assertIn(seccion, datos)

    def test_compilar_nuevas_secciones_tienen_contenido(self):
        datos = compilar_datos()
        plaza = datos["plaza_huamanga"]
        self.assertTrue(plaza.get("nombre"))
        self.assertTrue(plaza.get("que_ver"))
        for iglesia in datos["iglesias"]:
            with self.subTest(iglesia=iglesia["nombre"]):
                self.assertTrue(iglesia["nombre"])
                self.assertTrue(iglesia.get("barrio") or iglesia.get("tipo"))
        for servicio in datos["emergencias"]:
            with self.subTest(servicio=servicio["servicio"]):
                self.assertTrue(servicio["servicio"])
                self.assertTrue(servicio["numero"])
        for grupo in datos["quechua"]:
            with self.subTest(grupo=grupo["grupo"]):
                self.assertTrue(grupo["grupo"])
                for frase in grupo["frases"]:
                    self.assertTrue(frase["quechua"])
                    self.assertTrue(frase["espanol"])

    def test_compilar_alojamiento_incluye_ciudad_y_provincia(self):
        datos = compilar_datos()
        alojamientos = datos["alojamiento"]
        self.assertTrue(alojamientos)
        for a in alojamientos:
            with self.subTest(nombre=a["nombre"]):
                self.assertTrue(a["ciudad"])
                self.assertTrue(a["provincia"])

    def test_compilar_restaurantes_incluyen_ciudad_y_provincia(self):
        datos = compilar_datos()
        restaurantes = datos["restaurantes"]
        self.assertTrue(restaurantes)
        for r in restaurantes:
            with self.subTest(nombre=r["nombre"]):
                self.assertTrue(r["ciudad"])
                self.assertTrue(r["provincia"])

    def test_compilar_comercios_incluyen_categoria_ciudad_y_provincia(self):
        datos = compilar_datos()
        comercios = datos["comercios"]
        self.assertTrue(comercios)
        for c in comercios:
            with self.subTest(nombre=c["nombre"]):
                self.assertTrue(c["ciudad"])
                self.assertTrue(c["provincia"])
                self.assertTrue(c["categoria"])

    def test_compilar_eventos_incluyen_gps(self):
        datos = compilar_datos()
        eventos = datos["eventos_culturales"]
        self.assertTrue(eventos)
        for ev in eventos:
            with self.subTest(nombre=ev["nombre"]):
                self.assertIn("lat", ev)
                self.assertIn("lng", ev)
                self.assertTrue(ev["lugar"])
                self.assertTrue(ev["ciudad"])
                self.assertTrue(ev["provincia"])

    def test_compilar_lugares_incluye_gps_resuelto(self):
        datos = compilar_datos()
        for seccion in ("alojamiento", "restaurantes", "comercios"):
            for lugar in datos[seccion]:
                with self.subTest(seccion=seccion, nombre=lugar["nombre"]):
                    self.assertIn("lat", lugar)
                    self.assertIn("lng", lugar)

    def test_compilar_todo_lugar_visit_tiene_gps(self):
        datos = compilar_datos()
        for seccion in ("atracciones", "festividades", "artesanias", "eventos_culturales"):
            for lugar in datos[seccion]:
                with self.subTest(seccion=seccion, nombre=lugar["nombre"]):
                    self.assertIn("lat", lugar)
                    self.assertIn("lng", lugar)

    def test_exportar_escribe_json_valido(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "datos.json"
            exportar_datos(ruta)
            with open(ruta, encoding="utf-8") as f:
                contenido = json.load(f)
        self.assertIn("atracciones", contenido)
        self.assertTrue(contenido["atracciones"])


if __name__ == "__main__":
    unittest.main()