import unittest

from ayacucho.datos import (
    ALOJAMIENTO,
    ARTESANIAS,
    ATRACCIONES,
    CLIMA,
    COMO_LLEGAR,
    COMERCIOS,
    CONSEJOS,
    EVENTOS_CULTURALES,
    FESTIVIDADES,
    todos_alojamientos,
    todos_comercios,
    todos_los_lugares,
    GASTRONOMIA,
    INFO_URL,
    ITINERARIOS,
    RESTAURANTES,
    todos_restaurantes,
)


class TestDatos(unittest.TestCase):
    def test_atracciones(self):
        self.assertTrue(ATRACCIONES)
        for a in ATRACCIONES:
            for key in ("nombre", "tipo", "descripcion", "horario", "costo"):
                self.assertIn(key, a)

    def test_gastronomia(self):
        self.assertTrue(GASTRONOMIA)
        for g in GASTRONOMIA:
            for key in ("nombre", "tipo", "descripcion", "precio"):
                self.assertIn(key, g)

    def test_festividades(self):
        self.assertTrue(FESTIVIDADES)
        for f in FESTIVIDADES:
            for key in ("nombre", "fechas", "descripcion", "lugar", "ciudad", "lat", "lng"):
                self.assertIn(key, f)

    def test_festividades_gps_validas(self):
        for f in FESTIVIDADES:
            with self.subTest(nombre=f["nombre"]):
                self.assertGreaterEqual(f["lat"], -19)
                self.assertLessEqual(f["lat"], -10)
                self.assertGreaterEqual(f["lng"], -78)
                self.assertLessEqual(f["lng"], -70)

    def test_eventos_culturales(self):
        self.assertTrue(EVENTOS_CULTURALES)
        self.assertGreaterEqual(len(EVENTOS_CULTURALES), 5)
        for ev in EVENTOS_CULTURALES:
            for key in (
                "nombre",
                "tipo",
                "fechas",
                "lugar",
                "ciudad",
                "provincia",
                "descripcion",
                "costo",
                "lat",
                "lng",
            ):
                self.assertIn(key, ev)
            self.assertTrue(ev["ciudad"])
            self.assertTrue(ev["lugar"])
            self.assertGreaterEqual(ev["lat"], -19)
            self.assertLessEqual(ev["lat"], -10)
            self.assertGreaterEqual(ev["lng"], -78)
            self.assertLessEqual(ev["lng"], -70)
        provincias = {ev["provincia"] for ev in EVENTOS_CULTURALES}
        self.assertIn("Huamanga", provincias)
        self.assertGreater(len(provincias), 1)

    def test_atracciones_gps_validas(self):
        for a in ATRACCIONES:
            with self.subTest(nombre=a["nombre"]):
                self.assertIn("lat", a)
                self.assertIn("lng", a)
                self.assertGreaterEqual(a["lat"], -19)
                self.assertLessEqual(a["lat"], -10)
                self.assertGreaterEqual(a["lng"], -78)
                self.assertLessEqual(a["lng"], -70)

    def test_atracciones_tienen_ciudad_para_llegar(self):
        for a in ATRACCIONES:
            with self.subTest(nombre=a["nombre"]):
                self.assertIn("ciudad", a)
                self.assertTrue(a["ciudad"])

    def test_gps_url_maps(self):
        from ayacucho.gps import coordenadas_de, dms, url_maps

        coord = coordenadas_de(ATRACCIONES[0])
        self.assertIsNotNone(coord)
        lat, lng = coord
        url = url_maps(lat, lng, "Plaza Mayor")
        self.assertTrue(url.startswith("https://www.google.com/maps/search/?api=1&query="))
        textual = dms(lat, lng)
        self.assertIn("S", textual)
        self.assertIn("O", textual)
        self.assertIn("°", textual)
        self.assertNotIn('60.0"', textual)
        self.assertNotIn("60'", textual)

    def test_gps_por_ciudad_cubre_todas_las_ciudades(self):
        from ayacucho.datos import gps_de

        ciudades = set()
        for coleccion in (ALOJAMIENTO, RESTAURANTES):
            for provincia, opciones in coleccion.items():
                for item in opciones:
                    ciudades.add(item["ciudad"])
        for categoria, provincias in COMERCIOS.items():
            for provincia, opciones in provincias.items():
                for item in opciones:
                    ciudades.add(item["ciudad"])
        for ciudad in sorted(ciudades):
            with self.subTest(ciudad=ciudad):
                self.assertIsNotNone(gps_de({"ciudad": ciudad}))

    def test_todos_los_lugares_tienen_gps_valido(self):
        from ayacucho.datos import gps_de, todos_alojamientos, todos_comercios, todos_restaurantes

        lugares = todos_alojamientos() + todos_restaurantes() + todos_comercios()
        for lugar in lugares:
            with self.subTest(nombre=lugar["nombre"]):
                coord = gps_de(lugar)
                self.assertIsNotNone(coord, f"sin GPS: {lugar['nombre']}")
                lat, lng = coord
                self.assertGreaterEqual(lat, -19)
                self.assertLessEqual(lat, -10)
                self.assertGreaterEqual(lng, -78)
                self.assertLessEqual(lng, -70)

    def test_indice_unificado_tiene_todos_los_gps(self):
        for lugar in todos_los_lugares():
            with self.subTest(nombre=lugar.get("nombre")):
                self.assertIn("lat", lugar)
                self.assertIn("lng", lugar)
                self.assertGreaterEqual(lugar["lat"], -19)
                self.assertLessEqual(lugar["lat"], -10)
                self.assertGreaterEqual(lugar["lng"], -78)
                self.assertLessEqual(lugar["lng"], -70)

    def test_artesanias(self):
        self.assertTrue(ARTESANIAS)
        for art in ARTESANIAS:
            for key in ("nombre", "descripcion", "donde_comprar", "precio", "ciudad", "lat", "lng"):
                self.assertIn(key, art)

    def test_consejos(self):
        self.assertTrue(CONSEJOS)
        self.assertTrue(all(isinstance(c, str) for c in CONSEJOS))

    def test_info_url(self):
        self.assertTrue(INFO_URL.startswith("https://"))

    def test_como_llegar(self):
        self.assertIn("titulo", COMO_LLEGAR)
        self.assertTrue(COMO_LLEGAR["llegada"])
        self.assertTrue(COMO_LLEGAR["desplazamiento"])
        for o in COMO_LLEGAR["llegada"]:
            for key in ("medio", "descripcion", "tiempo", "costo"):
                self.assertIn(key, o)

    def test_alojamiento(self):
        self.assertTrue(ALOJAMIENTO)
        total = 0
        for provincia, opciones in ALOJAMIENTO.items():
            self.assertTrue(provincia)
            self.assertTrue(opciones)
            for a in opciones:
                for key in ("nombre", "tipo", "descripcion", "ciudad", "zona", "rango_precio"):
                    self.assertIn(key, a)
                self.assertTrue(a["ciudad"])
                total += 1
        self.assertGreaterEqual(total, 20)

    def test_alojamiento_ciudades_principales(self):
        ciudades = {a["ciudad"] for a in todos_alojamientos()}
        self.assertEqual(
            ciudades,
            {
                "Pampa Cangallo",
                "Cangallo",
                "Ayacucho",
                "Quinua",
                "Huanta",
                "San Miguel",
                "Huanca Sancos",
                "Huancapi",
                "Vilcashuamán",
                "Querobamba",
                "Puquio",
                "Coracora",
                "Pausa",
                "Pausa (Mirmaca)",
            },
        )

    def test_alojamiento_plano_incluye_provincia(self):
        from ayacucho.datos import todos_alojamientos
        plano = todos_alojamientos()
        self.assertGreaterEqual(len(plano), 20)
        for a in plano:
            self.assertIn("provincia", a)
        # Buscar una opción de cada provincia.
        provincias = {a["provincia"] for a in plano}
        self.assertEqual(
            provincias,
            {
                "Huamanga",
                "Huanta",
                "La Mar",
                "Cangallo",
                "Huanca Sancos",
                "Víctor Fajardo",
                "Vilcashuamán",
                "Sucre",
                "Lucanas",
                "Parinacochas",
                "Páucar del Sara Sara",
            },
        )

    def test_alojamiento_tipos_estilos_y_franjas(self):
        from ayacucho.datos import ALOJAMIENTO, FRANJAS_ALOJAMIENTO, franja_de

        entradas = [a for opciones in ALOJAMIENTO.values() for a in opciones]
        self.assertGreaterEqual(len({a["tipo"] for a in entradas}), 8)
        self.assertGreaterEqual(len({a["estilo"] for a in entradas}), 5)
        self.assertEqual(
            {a["franja"] for a in entradas},
            {franja for franja, _ in FRANJAS_ALOJAMIENTO},
        )
        self.assertEqual(franja_de("S/ 250 - 480"), "premium")
        self.assertEqual(franja_de("S/ 40 - 90"), "medio")
        self.assertEqual(franja_de("S/ 20 - 45"), "económico")

    def test_alojamiento_detalle_completo(self):
        from ayacucho.datos import ALOJAMIENTO, DETALLE_ALOJAMIENTO, FRANJAS_ALOJAMIENTO

        entradas = [a for opciones in ALOJAMIENTO.values() for a in opciones]
        self.assertEqual({a["nombre"] for a in entradas}, set(DETALLE_ALOJAMIENTO))
        for a in entradas:
            with self.subTest(nombre=a["nombre"]):
                self.assertTrue(a["estilo"])
                self.assertIn(a["franja"], {f for f, _ in FRANJAS_ALOJAMIENTO})
                self.assertIsInstance(a["servicios"], str)
                if a["estrellas"] is not None:
                    self.assertGreaterEqual(a["estrellas"], 1)
                    self.assertLessEqual(a["estrellas"], 5)

    def test_alojamiento_variedad_por_provincia(self):
        from ayacucho.datos import todos_alojamientos

        provincias = {}
        for a in todos_alojamientos():
            provincias.setdefault(a["provincia"], set()).add(a["tipo"])
        con_variedad = [p for p, tipos in provincias.items() if len(tipos) >= 3]
        self.assertGreaterEqual(len(con_variedad), 3)

    def test_restaurantes(self):
        self.assertTrue(RESTAURANTES)
        total = 0
        for provincia, opciones in RESTAURANTES.items():
            self.assertTrue(provincia)
            self.assertTrue(opciones)
            for r in opciones:
                for key in ("nombre", "tipo", "descripcion", "ciudad", "zona", "rango_precio"):
                    self.assertIn(key, r)
                self.assertTrue(r["ciudad"])
                total += 1
        self.assertGreaterEqual(total, 20)

    def test_restaurantes_cubren_las_11_provincias(self):
        provincias = set(RESTAURANTES.keys())
        self.assertEqual(
            provincias,
            {
                "Huamanga",
                "Huanta",
                "La Mar",
                "Cangallo",
                "Huanca Sancos",
                "Víctor Fajardo",
                "Vilcashuamán",
                "Sucre",
                "Lucanas",
                "Parinacochas",
                "Páucar del Sara Sara",
            },
        )
        plano = todos_restaurantes()
        self.assertEqual({r["provincia"] for r in plano}, provincias)
        for r in plano:
            self.assertIn("provincia", r)
            self.assertTrue(r["ciudad"])

    def test_comercios_estructura(self):
        self.assertTrue(COMERCIOS)
        total = 0
        for categoria, provincias in COMERCIOS.items():
            self.assertTrue(categoria)
            self.assertTrue(provincias)
            for provincia, opciones in provincias.items():
                self.assertTrue(provincia)
                self.assertTrue(opciones)
                for c in opciones:
                    for key in ("nombre", "tipo", "descripcion", "ciudad", "zona", "rango_precio"):
                        self.assertIn(key, c)
                    self.assertTrue(c["ciudad"])
                    total += 1
        self.assertGreaterEqual(total, 20)

    def test_comercios_categorias_principales(self):
        self.assertEqual(
            set(COMERCIOS.keys()),
            {"Cafeterías", "Peñas y Música", "Centros Comerciales", "Tiendas y Mercados"},
        )

    def test_comercios_plano_incluye_categoria_y_provincia(self):
        plano = todos_comercios()
        self.assertGreaterEqual(len(plano), 20)
        provincias_permitidas = {
            "Huamanga",
            "Huanta",
            "La Mar",
            "Cangallo",
            "Huanca Sancos",
            "Víctor Fajardo",
            "Vilcashuamán",
            "Sucre",
            "Lucanas",
            "Parinacochas",
            "Páucar del Sara Sara",
        }
        categorias = set()
        for c in plano:
            self.assertIn("provincia", c)
            self.assertIn("categoria", c)
            self.assertIn(c["provincia"], provincias_permitidas)
            self.assertTrue(c["ciudad"])
            categorias.add(c["categoria"])
        self.assertEqual(categorias, set(COMERCIOS.keys()))
        self.assertIn("Huamanga", {c["provincia"] for c in plano})

    def test_clima(self):
        self.assertEqual(len(CLIMA), 12)
        for c in CLIMA:
            for key in ("mes", "min", "max", "lluvia", "descripcion"):
                self.assertIn(key, c)
            self.assertIsInstance(c["min"], int)
            self.assertIsInstance(c["max"], int)

    def test_itinerarios(self):
        self.assertTrue(ITINERARIOS)
        for it in ITINERARIOS:
            for key in ("titulo", "descripcion", "paradas"):
                self.assertIn(key, it)
            self.assertTrue(it["paradas"])

    def test_itinerarios_tienen_paradas_gps(self):
        for it in ITINERARIOS:
            with self.subTest(titulo=it["titulo"]):
                paradas = it["paradas_gps"]
                self.assertGreaterEqual(len(paradas), 2)
                for punto in paradas:
                    self.assertTrue(punto["lugar"])
                    self.assertGreaterEqual(punto["lat"], -19)
                    self.assertLessEqual(punto["lat"], -10)
                    self.assertGreaterEqual(punto["lng"], -78)
                    self.assertLessEqual(punto["lng"], -70)

    def test_url_ruta_arma_waypoints(self):
        from ayacucho.datos import gps_de
        from ayacucho.gps import url_maps, url_ruta

        url = url_ruta(ITINERARIOS[0]["paradas_gps"])
        self.assertTrue(url.startswith("https://www.google.com/maps/dir/?api=1&origin="))
        self.assertIn("&destination=", url)
        self.assertIn("&waypoints=", url)
        self.assertIn("travelmode=driving", url)
        self.assertNotIn("%25", url)
        self.assertEqual(url.count("|"), len(ITINERARIOS[0]["paradas_gps"]) - 3)
        self.assertEqual(url_ruta([]), "")
        self.assertEqual(url_ruta([ITINERARIOS[0]["paradas_gps"][0]]),
                         url_maps(*gps_de(ITINERARIOS[0]["paradas_gps"][0])))

    def test_puntos_de_llegada_con_gps(self):
        puntos = COMO_LLEGAR["puntos_de_llegada"]
        self.assertTrue(puntos)
        for p in puntos:
            with self.subTest(lugar=p["lugar"]):
                for key in ("lugar", "descripcion", "ciudad", "lat", "lng"):
                    self.assertIn(key, p)
                self.assertGreaterEqual(p["lat"], -19)
                self.assertLessEqual(p["lat"], -10)
                self.assertGreaterEqual(p["lng"], -78)
                self.assertLessEqual(p["lng"], -70)
        lugares = " ".join(p["lugar"].lower() for p in puntos)
        self.assertIn("aeropuerto", lugares)
        self.assertIn("terminal", lugares)

    def test_indice_unificado_de_lugares(self):
        lugares = todos_los_lugares()
        secciones = {l["seccion"] for l in lugares}
        self.assertEqual(
            secciones,
            {
                "Atracciones",
                "Iglesias",
                "Festividades",
                "Artesanias",
                "Eventos Culturales",
                "Hospedajes",
                "Restaurantes",
                "Comercios",
            },
        )
        self.assertEqual(len(lugares), 184)
        atracciones = {l["nombre"] for l in lugares if l["seccion"] == "Atracciones"}
        iglesias = [l["nombre"] for l in lugares if l["seccion"] == "Iglesias"]
        self.assertTrue(iglesias)
        self.assertFalse(atracciones.intersection(iglesias))

    def test_distancia_entre_lugares(self):
        from ayacucho.gps import distancia, distancia_entre

        plaza = next(l for l in todos_los_lugares() if l["nombre"] == "Plaza Mayor de Ayacucho")
        catedral = next(l for l in todos_los_lugares() if l["nombre"] == "Catedral de Ayacucho")
        km = distancia_entre(plaza, catedral)
        self.assertIsNotNone(km)
        self.assertGreater(km, 0)
        self.assertLess(km, 1)
        self.assertAlmostEqual(
            km,
            distancia(plaza["lat"], plaza["lng"], catedral["lat"], catedral["lng"]),
            places=6,
        )
        self.assertIsNone(distancia_entre(plaza, {"nombre": "sin gps"}))

    def test_cli_importable(self):
        from ayacucho.cli import main

        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()