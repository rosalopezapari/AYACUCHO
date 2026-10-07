import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import ayacucho.cli as cli


class TestPresentacion(unittest.TestCase):
    """La consola de Windows puede venir en cp1252: nada fuera de Latin-1."""

    MODULOS = [
        "cli.py",
        "datos.py",
        "gps.py",
        "logo.py",
        "rutas.py",
    ]

    def test_modulos_solo_usan_caracteres_imprimibles_en_cp1252(self):
        for nombre in self.MODULOS:
            ruta = Path(cli.__file__).parent / nombre
            with self.subTest(modulo=nombre):
                fuera = {
                    c
                    for c in ruta.read_text(encoding="utf-8")
                    if ord(c) > 0xFF
                }
                self.assertEqual(fuera, set(), f"{nombre} usa {fuera}")

    def test_encabezado_no_supera_80_columnas(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.print_header("ITINERARIOS SUGERIDOS")
            cli.print_seccion("Detalle de la ruta")
        import re

        for linea in buf.getvalue().splitlines():
            limpio = re.sub(r"\033\[[0-9;]*m", "", linea)
            self.assertLessEqual(len(limpio), 80)

    def test_texto_largo_se_ajusta_al_ancho(self):
        import re

        largo = "palabra " * 40
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.print_texto(largo)
            cli.print_dato("Descripción", largo)
        for linea in buf.getvalue().splitlines():
            limpio = re.sub(r"\033\[[0-9;]*m", "", linea)
            self.assertLessEqual(len(limpio.strip("\n")), 80)

    def test_plural_acepta_singular_y_plural(self):
        self.assertEqual(cli.plural(1, "opción", "opciones"), "1 opción")
        self.assertEqual(cli.plural(3, "opción", "opciones"), "3 opciones")
        self.assertEqual(cli.plural(0, "provincia", "provincias"), "0 provincias")


class TestMenuOrdenado(unittest.TestCase):
    def test_opciones_salen_del_1_al_25_y_luego_salir(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_main_menu()
        import re

        limpio = re.sub(r"\033\[[0-9;]*m", "", buf.getvalue())
        numeros = [int(n) for n in re.findall(r"^\s+(\d+)\. ", limpio, re.M)]
        self.assertEqual(numeros, list(range(1, 26)) + [0])

    def test_el_despacho_cubre_todas_las_opciones_del_menu(self):
        opciones = [op for _g, ops in cli.menu_principal() for op in ops]
        claves = [clave for clave, _e, _f in opciones]
        self.assertEqual(claves, [str(i) for i in range(1, 26)])
        despacho = {clave: funcion for clave, _e, funcion in opciones if funcion}
        self.assertEqual(len(despacho), len(claves))
        for clave, _etiqueta, funcion in opciones:
            self.assertIs(despacho[clave], funcion)
            self.assertTrue(callable(funcion))

    def test_el_menu_agrupa_las_opciones(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_main_menu()
        import re

        limpio = re.sub(r"\033\[[0-9;]*m", "", buf.getvalue())
        for grupo in ("DESCUBRE AYACUCHO", "EN LA CIUDAD", "SERVICIOS Y PLANES",
                      "ORGANIZA TU VIAJE"):
            self.assertIn(grupo, limpio)


class TestPantallasNuevas(unittest.TestCase):
    """Plaza, iglesias, emergencias y quechua: contenido, ancho y Latin-1."""

    def _salida(self, funcion, entrada=""):
        import re

        patch_limpio = mock.patch.object(cli, "clear_screen")
        patch_input = mock.patch.object(cli, "safe_input", return_value=entrada)
        patch_limpio.start()
        self.addCleanup(patch_limpio.stop)
        with patch_input:
            buf = io.StringIO()
            with redirect_stdout(buf):
                funcion()
        return re.sub(r"\033\[[0-9;]*m", "", buf.getvalue())

    def test_plaza_muestra_descripcion_gps_y_consejos(self):
        salida = self._salida(cli.show_plaza)
        self.assertIn("PLAZA DE HUAMANGA", salida)
        self.assertIn("Qué ver alrededor", salida)
        self.assertIn("GPS:", salida)
        self.assertIn("Google Maps:", salida)
        self.assertIn("-13.158786", salida)
        self.assertIn("Consejos", salida)

    def test_iglesias_lista_templos_con_barrio(self):
        from ayacucho.datos import IGLESIAS

        salida = self._salida(cli.show_iglesias)
        self.assertIn("LAS 33 IGLESIAS", salida)
        self.assertIn("Templos para visitar", salida)
        for iglesia in IGLESIAS:
            self.assertIn(iglesia["nombre"], salida)
            self.assertIn(iglesia["barrio"], salida)

    def test_emergencias_muestra_los_cuatro_numeros(self):
        salida = self._salida(cli.show_emergencias)
        self.assertIn("EMERGENCIAS Y SERVICIOS", salida)
        for numero in ("105", "106", "115", "116"):
            self.assertIn(numero, salida)
        self.assertIn("Almenara", salida)

    def test_quechua_muestra_frases_y_traduccion(self):
        from ayacucho.datos import QUECHUA

        salida = self._salida(cli.show_quechua)
        self.assertIn("FRASES EN QUECHUA", salida)
        for bloque in QUECHUA:
            self.assertIn(bloque["grupo"], salida)
            for frase in bloque["frases"]:
                self.assertIn(frase["quechua"], salida)
                self.assertIn(frase["espanol"], salida)
        self.assertIn("->", salida)

    def test_las_cuatro_pantallas_caben_en_80_columnas(self):
        for funcion in (cli.show_plaza, cli.show_iglesias, cli.show_emergencias,
                        cli.show_quechua):
            for linea in self._salida(funcion).splitlines():
                if "http" in linea:
                    continue  # la URL de Maps se imprime de corrido para poder copiarla
                self.assertLessEqual(len(linea), 80, f"{funcion.__name__}: {linea}")
                linea.encode("latin-1")


class TestMapaCentro(unittest.TestCase):
    """Mapa del centro histórico: puntos proyectados, ancho y Latin-1."""

    def _salida(self, funcion, entrada=""):
        import re

        patch_limpio = mock.patch.object(cli, "clear_screen")
        patch_input = mock.patch.object(cli, "safe_input", return_value=entrada)
        patch_limpio.start()
        self.addCleanup(patch_limpio.stop)
        with patch_input:
            buf = io.StringIO()
            with redirect_stdout(buf):
                funcion()
        return re.sub(r"\033\[[0-9;]*m", "", buf.getvalue())

    def test_mapa_numera_cada_punto_con_gps(self):
        from ayacucho.datos import puntos_del_mapa_centro

        puntos = puntos_del_mapa_centro()
        self.assertGreaterEqual(len(puntos), 5)
        salida = self._salida(cli.show_mapa)
        self.assertIn("MAPA DEL CENTRO HISTÓRICO", salida)
        self.assertIn("Puntos del mapa", salida)
        for i, punto in enumerate(puntos, 1):
            self.assertIn(punto["nombre"], salida)
        filas = [
            l for l in salida.splitlines()
            if l.strip().startswith("|") and l.strip().endswith("|")
        ]
        self.assertGreaterEqual(len(filas), 10)
        rejilla = "\n".join(filas)
        for i in range(1, len(puntos) + 1):
            self.assertIn(str(i), rejilla, f"el punto {i} no aparece en la rejilla")

    def test_mapa_sin_coordenadas_falsas(self):
        from ayacucho.datos import IGLESIAS, puntos_del_mapa_centro

        sin_gps = [i["nombre"] for i in IGLESIAS if "lat" not in i]
        self.assertTrue(sin_gps)
        nombres_mapa = {p["nombre"] for p in puntos_del_mapa_centro()}
        for nombre in sin_gps:
            self.assertNotIn(nombre, nombres_mapa)

    def test_mapa_cabe_en_80_columnas_y_en_latin1(self):
        for linea in self._salida(cli.show_mapa).splitlines():
            if "http" in linea:
                continue
            self.assertLessEqual(len(linea), 80, linea)
            linea.encode("latin-1")


class TestHelpersGeo(unittest.TestCase):
    """Los catálogos usan {provincia: [entradas]} o {categoria: {provincia: [entradas]}}."""

    def test_categorias_geo_cuenta_entradas_en_ambos_formatos(self):
        plano = {"Huamanga": [{"nombre": "A"}, {"nombre": "B"}]}
        anidado = {"Cafeterías": {"Huamanga": [{"nombre": "C"}]}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.mostrar_categorias_geo("Prueba", plano)
            cli.mostrar_categorias_geo("Prueba", anidado)
        salida = buf.getvalue()
        self.assertIn("Huamanga (2 opciones)", salida)
        self.assertIn("Cafeterías (1 opción)", salida)

    def test_fichas_devuelve_todas_las_entradas(self):
        plano = {"Huamanga": [{"nombre": "A", "descripcion": "d"}]}
        anidado = {"Cafeterías": {"Huamanga": [{"nombre": "B", "descripcion": "d"}]}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(
                [e["nombre"] for e in cli.mostrar_geo_por_categoria(plano)], ["A"]
            )
            self.assertEqual(
                [e["nombre"] for e in cli.mostrar_geo_por_categoria(anidado)], ["B"]
            )
        import re

        salida = re.sub(r"\033\[[0-9;]*m", "", buf.getvalue())
        self.assertIn("-- Huamanga", salida)
        self.assertIn("-- Cafeterías", salida)
        self.assertIn("(Huamanga)", salida)

    def test_print_dato_alinea_las_columnas(self):
        import re

        buf = io.StringIO()
        with redirect_stdout(buf):
            cli.print_dato("Tipo", "Religioso")
            cli.print_dato("Horario", "07:00 - 18:00")
        lineas = [
            re.sub(r"\033\[[0-9;]*m", "", l) for l in buf.getvalue().splitlines()
        ]
        valores = [l.index("R") if "Religioso" in l else l.index("0") for l in lineas]
        self.assertEqual(valores[0], valores[1])


class TestFavoritos(unittest.TestCase):
    def setUp(self):
        cli.favoritos_atracciones.clear()

    def test_toggle_agrega_favorito(self):
        with mock.patch.object(cli, "save_favoritos"):
            cli.toggle_favorito("Plaza Mayor de Ayacucho")
        self.assertIn("Plaza Mayor de Ayacucho", cli.favoritos_atracciones)

    def test_toggle_elimina_favorito(self):
        with mock.patch.object(cli, "save_favoritos"):
            cli.toggle_favorito("Plaza Mayor de Ayacucho")
            cli.toggle_favorito("Plaza Mayor de Ayacucho")
        self.assertNotIn("Plaza Mayor de Ayacucho", cli.favoritos_atracciones)

    def test_toggle_guarda_archivo(self):
        with mock.patch.object(cli, "save_favoritos") as guardar:
            cli.toggle_favorito("Catedral de Ayacucho")
        guardar.assert_called_once_with({"Catedral de Ayacucho"})


class TestBuscarGeneral(unittest.TestCase):
    def test_buscar_cruza_categorias(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["cuy", ""])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.buscar_general()
        self.assertIn("Cuy Chactado", buf.getvalue())
        self.assertIn("Gastronomía", buf.getvalue())

    def test_buscar_sin_resultados(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            cli.safe_input = lambda prompt: "xzz123"
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.buscar_general()
        self.assertIn("No se encontraron resultados", buf.getvalue())


class TestShowFavoritos(unittest.TestCase):
    def test_favoritos_vacio(self):
        cli.favoritos_atracciones.clear()
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_favoritos()
        self.assertIn("Aún no tienes favoritos", buf.getvalue())

    def test_favoritos_con_resultados(self):
        cli.favoritos_atracciones.add("Catedral de Ayacucho")
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_favoritos()
        self.assertIn("Catedral de Ayacucho", buf.getvalue())


class TestHistoria(unittest.TestCase):
    def test_lista_historias(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["2", ""])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_historia()
        self.assertIn("La Batalla de Ayacucho", buf.getvalue())


class TestAcercaDe(unittest.TestCase):
    def test_muestra_version_y_url(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_acerca_de()
        self.assertIn(cli.__version__, buf.getvalue())
        self.assertIn(cli.INFO_URL, buf.getvalue())


class TestComoLlegar(unittest.TestCase):
    def test_muestra_opciones_de_llegada(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_como_llegar()
        self.assertIn("Avión", buf.getvalue())
        self.assertIn("Bus de larga distancia", buf.getvalue())
        self.assertIn("Moverse dentro de la ciudad", buf.getvalue())

    def test_muestra_puntos_de_llegada_con_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_como_llegar()
        value = buf.getvalue()
        self.assertIn("Puntos de llegada (GPS)", value)
        self.assertIn("Aeropuerto", value)
        self.assertIn("Terminal Terrestre", value)
        self.assertIn("GPS:", value)

    def test_abre_punto_de_llegada_en_maps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "safe_input", return_value="1"), \
                mock.patch.object(cli.gps, "abrir_maps", return_value=True):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_como_llegar()
        self.assertIn("Abriendo Google Maps", buf.getvalue())


class TestDormir(unittest.TestCase):
    def test_muestra_provincias_y_selecciona_una(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        self.assertIn("DÓNDE DORMIR", buf.getvalue())
        self.assertIn("Huamanga", buf.getvalue())
        self.assertIn("Hotel Santa Rosa", buf.getvalue())
        self.assertIn("Ciudad:", buf.getvalue())

    def test_ver_todas_las_provincias(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["t", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        self.assertIn("TODOS LOS HOSPEDAJES", buf.getvalue())
        self.assertIn("Vilcashuamán", buf.getvalue())
        self.assertIn("Páucar del Sara Sara", buf.getvalue())

    def test_filtrar_por_estilo(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["e", "1", "0", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        value = buf.getvalue()
        self.assertIn("FILTRAR HOSPEDAJES POR ESTILO", value)
        self.assertIn("HOSPEDAJES - ESTILO COLONIAL", value)
        self.assertIn("Hotel Santa Rosa", value)
        self.assertIn("Estilo: Colonial", value)

    def test_filtrar_por_precio(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["p", "1", "0", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        value = buf.getvalue()
        self.assertIn("FILTRAR HOSPEDAJES POR PRECIO", value)
        self.assertIn("promedio hasta S/ 60 por noche", value)
        self.assertIn("HOSPEDAJES - PRECIO ECONÓMICO", value)

    def test_filtro_con_opcion_invalida(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["e", "x", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        self.assertIn("Opción no válida", buf.getvalue())


class TestComer(unittest.TestCase):
    def test_muestra_provincias_y_selecciona_una(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_restaurantes()
        self.assertIn("DÓNDE COMER", buf.getvalue())
        self.assertIn("Huamanga", buf.getvalue())
        self.assertIn("ViaVia Café Ayacucho", buf.getvalue())
        self.assertIn("Ciudad:", buf.getvalue())

    def test_ver_todos_los_restaurantes(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["t", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_restaurantes()
        self.assertIn("TODOS LOS RESTAURANTES", buf.getvalue())
        self.assertIn("Parinacochas", buf.getvalue())
        self.assertIn("Páucar del Sara Sara", buf.getvalue())


class TestComercios(unittest.TestCase):
    def test_muestra_categorias_y_elegir_cafeteria(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "1", "0", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_comercios()
        self.assertIn("CAFETERÍAS, PEÑAS", buf.getvalue())
        self.assertIn("Huamanga", buf.getvalue())
        self.assertIn("Antaqa Café", buf.getvalue())
        self.assertIn("Ciudad:", buf.getvalue())

    def test_ver_todos_los_comercios(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["t", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_comercios()
        self.assertIn("TODOS LOS COMERCIOS", buf.getvalue())
        self.assertIn("Peñas y Música", buf.getvalue())
        self.assertIn("Shosaku Nagase", buf.getvalue())

    def test_ver_todas_las_provincias_de_una_categoria(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["4", "t", "0", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_comercios()
        self.assertIn("TIENDAS Y MERCADOS - TODAS LAS PROVINCIAS", buf.getvalue())
        self.assertIn("Talleres de tablas de Sarhua", buf.getvalue())
        self.assertIn("Parinacochas", buf.getvalue())


class TestListasConGPS(unittest.TestCase):
    def test_festividades_muestra_lugar_y_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_festividades()
        value = buf.getvalue()
        self.assertIn("Lugar:", value)
        self.assertIn("GPS:", value)

    def test_artesanias_muestra_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_artesanias()
        value = buf.getvalue()
        self.assertIn("Piedra Huamanga", value)
        self.assertIn("GPS:", value)

    def test_abre_lugar_de_listado_en_maps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.gps, "abrir_maps", return_value=True) as abrir:
            inputs = iter(["1", "1", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        value = buf.getvalue()
        self.assertIn("Abriendo Google Maps", value)
        abrir.assert_called_once()

    def test_numero_fuera_de_rango_en_mapa(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "999", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_restaurantes()
        self.assertIn("Número fuera de rango", buf.getvalue())

    def test_alojamiento_muestra_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_alojamiento()
        value = buf.getvalue()
        self.assertIn("Hotel Santa Rosa", value)
        self.assertIn("GPS:", value)
        self.assertIn("Google Maps:", value)

    def test_restaurantes_muestra_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_restaurantes()
        value = buf.getvalue()
        self.assertIn("ViaVia Café Ayacucho", value)
        self.assertIn("GPS:", value)

    def test_comercios_muestra_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "1", "", "0", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_comercios()
        value = buf.getvalue()
        self.assertIn("Antaqa Café", value)
        self.assertIn("GPS:", value)


class TestEventosCulturales(unittest.TestCase):
    def test_muestra_lista_y_detalle_con_gps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_eventos_culturales()
        value = buf.getvalue()
        self.assertIn("EVENTOS CULTURALES", value)
        self.assertIn("Feria Internacional del Libro", value)
        self.assertIn("GPS:", value)
        self.assertIn("Google Maps:", value)

    def test_abrir_maps_en_navegador(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.gps, "abrir_maps", return_value=True) as abrir:
            inputs = iter(["1", "m", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_eventos_culturales()
        self.assertIn("Abriendo Google Maps", buf.getvalue())
        abrir.assert_called_once()
        url = abrir.call_args[0][0]
        self.assertTrue(url.startswith("https://www.google.com/maps/search/?api=1&query="))


class TestAtraccionesGPS(unittest.TestCase):
    def test_detalle_atraccion_muestra_gps(self):
        from ayacucho.datos import ATRACCIONES

        con_gps = next(a for a in ATRACCIONES if "lat" in a)
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_detalle_atraccion(con_gps)
        value = buf.getvalue()
        self.assertIn("GPS:", value)
        self.assertIn("Google Maps:", value)

    def test_detalle_atraccion_sin_gps_no_falla(self):
        sin_gps = {
            "nombre": "Lugar de prueba",
            "tipo": "Prueba",
            "descripcion": "Sin coordenadas.",
            "horario": "24 horas",
            "costo": "Gratuito",
        }
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_detalle_atraccion(sin_gps)
        self.assertNotIn("GPS:", buf.getvalue())


class TestClima(unittest.TestCase):
    def test_muestra_meses_y_tips(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_clima()
        self.assertIn("CLIMA MENSUAL", buf.getvalue())
        self.assertIn("Enero", buf.getvalue())
        self.assertIn("Mejor época para visitar", buf.getvalue())


class TestItinerarios(unittest.TestCase):
    def tearDown(self):
        cli.rutas_guardadas = []

    def test_muestra_rutas(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "safe_input", return_value="0"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_itinerarios()
        value = buf.getvalue()
        self.assertIn("ITINERARIOS SUGERIDOS", value)
        self.assertIn("Ruta Cultural", value)
        self.assertIn("Paradas con GPS:", value)
        self.assertIn("Recorrido aprox:", value)
        self.assertIn("Ruta en Google Maps:", value)

    def test_guarda_itinerario(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.rutas, "agregar_ruta") as agregar:
            agregar.side_effect = lambda nueva, **kw: [nueva]
            inputs = iter(["1", "g", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_itinerarios()
        agregar.assert_called_once()
        self.assertEqual(agregar.call_args[0][0]["titulo"], "Ruta Express (1 día)")
        self.assertEqual(len(cli.rutas_guardadas), 1)
        self.assertIn("Ruta guardada", buf.getvalue())

    def test_mis_rutas_lista_y_vuelve(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            with mock.patch.object(cli.rutas, "cargar_rutas", return_value=[
                {
                    "titulo": "Ruta Express",
                    "descripcion": "d",
                    "paradas": [
                        {"lugar": "A", "lat": -13.1, "lng": -74.2},
                        {"lugar": "B", "lat": -13.2, "lng": -74.3},
                    ],
                    "creado": "2026-01-01",
                }
            ]):
                inputs = iter(["g", "0", "0"])
                cli.safe_input = lambda prompt: next(inputs)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    cli.show_itinerarios()
        value = buf.getvalue()
        self.assertIn("MIS RUTAS GUARDADAS", value)
        self.assertIn("Ruta Express", value)
        self.assertIn("2 paradas", value)

    def test_mis_rutas_vacia(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.rutas, "cargar_rutas", return_value=[]):
            inputs = iter(["g", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_itinerarios()
        self.assertIn("Aún no tienes rutas guardadas", buf.getvalue())

    def test_borra_ruta_guardada(self):
        guardada = {
            "titulo": "Ruta Express",
            "descripcion": "d",
            "paradas": [
                {"lugar": "A", "lat": -13.1, "lng": -74.2},
                {"lugar": "B", "lat": -13.2, "lng": -74.3},
            ],
            "creado": "2026-01-01",
        }
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.rutas, "cargar_rutas", return_value=[guardada]), \
                mock.patch.object(cli.rutas, "eliminar_ruta", return_value=[]):
            inputs = iter(["g", "x", "1", "g", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_itinerarios()
        value = buf.getvalue()
        self.assertIn("Ruta borrada", value)
        self.assertEqual(cli.rutas_guardadas, [])

    def test_abre_ruta_guardada_en_maps(self):
        guardada = {
            "titulo": "Ruta Express",
            "descripcion": "d",
            "paradas": [
                {"lugar": "A", "lat": -13.1, "lng": -74.2},
                {"lugar": "B", "lat": -13.2, "lng": -74.3},
            ],
            "creado": "2026-01-01",
        }
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.rutas, "cargar_rutas", return_value=[guardada]), \
                mock.patch.object(cli.gps, "abrir_maps", return_value=True) as abrir:
            inputs = iter(["g", "1", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_itinerarios()
        self.assertIn("Abriendo la ruta en Google Maps", buf.getvalue())
        abrir.assert_called_once()


class TestLugaresCercanos(unittest.TestCase):
    def test_ordena_por_distancia_desde_una_ciudad(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["1", "1", "5", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_lugares_cercanos()
        value = buf.getvalue()
        self.assertIn("LUGARES MÁS CERCANOS", value)
        self.assertIn("Distancia:", value)
        self.assertIn("Plaza Mayor de Ayacucho", value)
        self.assertIn("GPS:", value)

    def test_acepta_coordenadas_manuales(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["2", "-13,1588", "-74,2240", "3", "0", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_lugares_cercanos()
        value = buf.getvalue()
        self.assertIn("Origen:", value)
        self.assertIn("-13.158800, -74.224000", value)

    def test_abre_lugar_cercano_en_maps(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli.gps, "abrir_maps", return_value=True) as abrir:
            inputs = iter(["1", "1", "2", "1", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_lugares_cercanos()
        self.assertIn("Abriendo Google Maps", buf.getvalue())
        abrir.assert_called_once()

    def test_opcion_invalida_vuelve(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            inputs = iter(["9"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_lugares_cercanos()
        self.assertIn("LUGARES CERCANOS", buf.getvalue())


class TestAcceso(unittest.TestCase):
    def tearDown(self):
        cli.usuario_actual = None

    def test_usuario_registrado_entra_sin_preguntar(self):
        cli.usuario_actual = {"nombre": "Carla", "edad": 30}
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli.sys, "exit") as salir:
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.verificar_acceso()
        salir.assert_not_called()
        self.assertIn("Carla", buf.getvalue())

    def test_menor_de_edad_es_rechazado(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli.sys, "exit") as salir:
            inputs = iter(["15"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.verificar_acceso()
        salir.assert_called_once_with(0)
        self.assertIn("Acceso denegado", buf.getvalue())

    def test_adulto_sin_registrar_entra(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli.sys, "exit") as salir:
            inputs = iter(["30"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.verificar_acceso()
        salir.assert_not_called()
        self.assertIn("Acceso permitido", buf.getvalue())


class TestExportar(unittest.TestCase):
    def test_exporta_con_archivo_predeterminado(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "exportar_datos") as exportar:
            cli.safe_input = lambda prompt: ""
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_exportar()
        exportar.assert_called_once_with("datos_ayacucho.json")
        self.assertIn("Datos exportados", buf.getvalue())

    def test_exporta_con_ruta_personalizada(self):
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "exportar_datos") as exportar:
            cli.safe_input = lambda prompt: "mi_archivo.json"
            cli.show_exportar()
        exportar.assert_called_once_with("mi_archivo.json")


class TestPerfil(unittest.TestCase):
    def tearDown(self):
        cli.usuario_actual = None

    def test_perfil_sin_usuario(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            cli.safe_input = lambda prompt: "0"
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_perfil()
        self.assertIn("No tienes perfil registrado", buf.getvalue())

    def test_perfil_muestra_datos(self):
        cli.usuario_actual = {"nombre": "Ana Torres", "pais": "Perú", "ciudad": "Lima", "email": "", "motivo": "turismo"}
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"):
            cli.safe_input = lambda prompt: "0"
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.show_perfil()
        self.assertIn("Ana Torres", buf.getvalue())

    def test_registrar_guarda_usuario(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_usuario") as guardar:
            inputs = iter(["Ana Torres", "25", "Perú", "Lima", "ana@mail.com", ""])
            cli.safe_input = lambda prompt: next(inputs)
            cli.registrar_usuario()
        self.assertEqual(cli.usuario_actual["nombre"], "Ana Torres")
        self.assertEqual(cli.usuario_actual["edad"], 25)
        self.assertEqual(cli.usuario_actual["motivo"], "turismo")
        guardar.assert_called_once()

    def test_registrar_sin_nombre_no_guarda(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_usuario") as guardar:
            cli.safe_input = lambda prompt: ""
            cli.registrar_usuario()
        self.assertIsNone(cli.usuario_actual)
        guardar.assert_not_called()

    def test_registrar_menor_de_edad_no_guarda(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_usuario") as guardar:
            inputs = iter(["Juan Menor", "15"])
            cli.safe_input = lambda prompt: next(inputs)
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli.registrar_usuario()
        self.assertIsNone(cli.usuario_actual)
        guardar.assert_not_called()
        self.assertIn("mayores de 18", buf.getvalue())

    def test_registrar_edad_justo_18_permite(self):
        cli.usuario_actual = None
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_usuario"):
            inputs = iter(["Ana Joven", "18", "Perú", "Lima", "", "estudio"])
            cli.safe_input = lambda prompt: next(inputs)
            cli.registrar_usuario()
        self.assertEqual(cli.usuario_actual["edad"], 18)
        self.assertEqual(cli.usuario_actual["motivo"], "estudio")

    def test_pedir_edad_valida_entero(self):
        with mock.patch.object(cli, "clear_screen"):
            inputs = iter(["abc", "20"])
            cli.safe_input = lambda prompt: next(inputs)
            self.assertEqual(cli.pedir_edad(), 20)


class TestPresupuestoCLI(unittest.TestCase):
    def tearDown(self):
        cli.presupuesto_actual = {"presupuesto_total": 0.0, "gastos": []}

    def test_pedir_monto_valida_numerico(self):
        inputs = iter(["abc", "0", "-5", "12,50"])
        cli.safe_input = lambda prompt: next(inputs)
        self.assertEqual(cli.pedir_monto("Monto: "), 12.5)

    def test_pedir_categoria_valida_rango(self):
        inputs = iter(["0", "9", "z", "3"])
        cli.safe_input = lambda prompt: next(inputs)
        self.assertEqual(cli.pedir_categoria(), "Transporte")

    def test_establecer_total_y_guardar(self):
        cli.presupuesto_actual = {"presupuesto_total": 0.0, "gastos": []}
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_presupuesto") as guardar:
            inputs = iter(["t", "500", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            cli.show_presupuesto()
        guardar.assert_called_once()
        self.assertEqual(cli.presupuesto_actual["presupuesto_total"], 500.0)

    def test_agregar_y_eliminar_gasto(self):
        cli.presupuesto_actual = {"presupuesto_total": 500.0, "gastos": []}
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_presupuesto"):
            inputs = iter(["a", "Hotel", "1", "120.5", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            cli.show_presupuesto()
        self.assertEqual(len(cli.presupuesto_actual["gastos"]), 1)
        gasto = cli.presupuesto_actual["gastos"][0]
        self.assertEqual(gasto["concepto"], "Hotel")
        self.assertEqual(gasto["categoria"], "Alojamiento")
        self.assertEqual(gasto["monto"], 120.5)
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "guardar_presupuesto"):
            inputs = iter(["e", "1", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            cli.show_presupuesto()
        self.assertEqual(cli.presupuesto_actual["gastos"], [])

    def test_reiniciar_presupuesto(self):
        cli.presupuesto_actual = {
            "presupuesto_total": 300.0,
            "gastos": [{"concepto": "Tour", "categoria": "Atracciones", "monto": 50.0}],
        }
        with mock.patch.object(cli, "clear_screen"), \
                mock.patch.object(cli, "pause"), \
                mock.patch.object(cli, "eliminar_presupuesto"):
            inputs = iter(["n", "0"])
            cli.safe_input = lambda prompt: next(inputs)
            cli.show_presupuesto()
        self.assertEqual(cli.presupuesto_actual["gastos"], [])
        self.assertEqual(cli.presupuesto_actual["presupuesto_total"], 0.0)


if __name__ == "__main__":
    unittest.main()
