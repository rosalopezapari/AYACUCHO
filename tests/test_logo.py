import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from ayacucho import logo


class TestLogo(unittest.TestCase):
    def test_lineas_incluyen_nombre_y_eslogan(self):
        lineas = logo.lineas_logo()
        self.assertIn(logo.TAGLINE, lineas)
        self.assertIn("CIUDAD DE LAS 33 IGLESIAS", logo.TAGLINE)
        bloque = logo.texto_bloque("AYACUCHO")
        self.assertEqual(len(bloque), len(logo.LETRAS["A"]))
        esperada = "AYACUCHO"
        for fila in bloque:
            self.assertEqual(len(fila), len(esperada) * 5 + (len(esperada) - 1) * 2)

    def test_todas_las_letras_tienen_la_misma_altura(self):
        alturas = {len(filas) for filas in logo.LETRAS.values()}
        self.assertEqual(len(alturas), 1)

    def test_ancho_no_supera_80_columnas(self):
        self.assertLessEqual(logo.ancho_logo(), 80)

    def test_mostrar_logo_no_falla(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            logo.mostrar_logo()
        salida = buf.getvalue()
        lineas = [linea.strip() for linea in salida.splitlines() if linea.strip()]
        self.assertIn(logo.TAGLINE, lineas)
        for fila in logo.texto_bloque("AYACUCHO"):
            self.assertIn(fila.strip(), lineas)
        for linea in logo.MONTAÑAS:
            self.assertIn(linea.strip(), lineas)

    def test_svg_existe_y_es_valido(self):
        import xml.dom.minidom

        self.assertTrue(logo.ARCHIVO_SVG.exists())
        documento = xml.dom.minidom.parse(str(logo.ARCHIVO_SVG))
        self.assertEqual(documento.documentElement.tagName, "svg")
        self.assertIn("AYACUCHO", logo.ARCHIVO_SVG.read_text(encoding="utf-8"))

    def test_logo_personalizado_desde_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "logo.txt"
            archivo.write_text("  /\\/\\\n ( o.o )\n  > ^ <\n", encoding="utf-8")
            lineas = logo.cargar_logo(archivo)
            self.assertEqual(lineas, ["  /\\/\\", " ( o.o )", "  > ^ <"])

    def test_sin_logo_personalizado_usa_el_interno(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(logo.cargar_logo(Path(tmp) / "no_existe.txt"))

    def test_archivo_vacio_se_ignora(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "logo.txt"
            archivo.write_text("\n\n   \n", encoding="utf-8")
            self.assertIsNone(logo.cargar_logo(archivo))

    def test_archivo_con_bom_se_lee_sin_basura(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "logo.txt"
            archivo.write_bytes("\ufeff[ LOGO ]\n".encode("utf-8"))
            self.assertEqual(logo.cargar_logo(archivo), ["[ LOGO ]"])

    def test_mostrar_logo_usa_el_personalizado(self):
        with mock.patch.object(logo, "cargar_logo", return_value=["[ MI LOGO ]", "[ AQUI ]"]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                logo.mostrar_logo()
        salida = buf.getvalue()
        self.assertIn("[ MI LOGO ]", salida)
        self.assertIn("[ AQUI ]", salida)
        self.assertNotIn(logo.TAGLINE, salida)

    def test_ancho_logo_con_personalizado(self):
        with mock.patch.object(logo, "cargar_logo", return_value=["XXXXXXX", "XXX"]):
            self.assertEqual(logo.ancho_logo(), 7)

    def test_svg_y_png_declarados(self):
        self.assertEqual(logo.ARCHIVO_SVG.name, "logo.svg")
        self.assertEqual(logo.ARCHIVO_TEXTO.name, "logo.txt")
        self.assertEqual(logo.ARCHIVO_PNG.name, "logo.png")


if __name__ == "__main__":
    unittest.main()
