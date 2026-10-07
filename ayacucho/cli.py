"""Interfaz de línea de comandos de la app de turismo."""
import math
import os
import sys
import textwrap

from ayacucho import __version__
import ayacucho.datos as datos
import ayacucho.gps as gps
from ayacucho.datos import (
    ALOJAMIENTO,
    ARTESANIAS,
    ATRACCIONES,
    CLIMA,
    COMERCIOS,
    COMO_LLEGAR,
    CONSEJOS,
    EMERGENCIAS,
    EVENTOS_CULTURALES,
    FESTIVIDADES,
    GASTRONOMIA,
    IGLESIAS,
    INFO_URL,
    ITINERARIOS,
    PLAZA_HUAMANGA,
    QUECHUA,
    RESTAURANTES,
)
from ayacucho.historias import HISTORIAS
from ayacucho.storage import load_favoritos, save_favoritos
import ayacucho.logo as logo
import ayacucho.rutas as rutas
from ayacucho.exporter import exportar_datos
from ayacucho.usuario import EDAD_MINIMA, cargar_usuario, eliminar_usuario, guardar_usuario
from ayacucho.presupuesto import (
    CATEGORIAS,
    cargar_presupuesto,
    eliminar_presupuesto,
    guardar_presupuesto,
    presupuesto_restante,
    presupuesto_vacio,
    total_gastado,
)

try:
    import colorama
    colorama.init()
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
except ImportError:
    RESET = BOLD = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = ""

favoritos_atracciones = load_favoritos()
usuario_actual = cargar_usuario()
presupuesto_actual = cargar_presupuesto()
rutas_guardadas = rutas.cargar_rutas()


def toggle_favorito(nombre: str):
    if nombre in favoritos_atracciones:
        favoritos_atracciones.discard(nombre)
    else:
        favoritos_atracciones.add(nombre)
    save_favoritos(favoritos_atracciones)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


ANCHO_PANTALLA = 60
REGLAS = "=" * ANCHO_PANTALLA


def print_header(title: str):
    """Encabezado de pantalla con la paleta calida del logo (ocre y terracota).

    Solo usa caracteres ASCII: la consola de Windows puede venir en cp1252,
    donde los caracteres de dibujo de caja no existen.
    """
    print()
    print(f"  {YELLOW}{'~' * ANCHO_PANTALLA}{RESET}")
    print(f"{BOLD}{YELLOW}{title.center(ANCHO_PANTALLA + 2)}{RESET}")
    print(f"  {YELLOW}{'~' * ANCHO_PANTALLA}{RESET}")
    print()


def print_seccion(title: str):
    """Subtitulo dentro de una pantalla, con la misma paleta calida."""
    print(f"  {YELLOW}-- {BOLD}{title}{RESET}{YELLOW} {'-' * max(56 - len(title), 0)}{RESET}")


def print_item(numero, nombre, tipo=None, marca=""):
    """Ítem numerado de una lista; si el tipo no cabe, pasa a la línea siguiente."""
    etiqueta = f"{marca}{numero}. {nombre}"
    if tipo and len(etiqueta) + len(tipo) + 3 <= 72:
        print_line(f"{BOLD}{YELLOW}{etiqueta}{RESET} [{GREEN}{tipo}{RESET}]")
        return
    print_line(f"{BOLD}{YELLOW}{etiqueta}{RESET}")
    if tipo:
        print_line(f"   {GREEN}[{tipo}]{RESET}")


def print_dato(etiqueta: str, valor, ancho: int = 16):
    """Imprime una etiqueta y su valor en columnas; el texto largo se ajusta al ancho."""
    ancho = max(ancho, len(etiqueta) + 2)
    sangria = " " * (ancho + 2)
    lineas = textwrap.wrap(str(valor), width=78 - (ancho + 2)) or [""]
    print_line(f"{CYAN}{etiqueta + ':':<{ancho}}{lineas[0]}")
    for extra in lineas[1:]:
        print_line(f"{sangria}{extra}")


def print_texto(texto: str, sangria: int = 3, ancho: int = 72):
    """Imprime un párrafo largo con la sangría estándar de las listas."""
    for linea in textwrap.wrap(str(texto), width=ancho) or [""]:
        print_line(f"{' ' * sangria}{linea}")


def plural(cantidad: int, singular: str, plural_: str):
    """'1 provincia' / '3 provincias'."""
    return f"{cantidad} {singular if cantidad == 1 else plural_}"


def print_line(text: str):
    print(f"  {text}")


def safe_input(prompt: str):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def pause():
    safe_input(f"\n{YELLOW}  Presiona ENTER para continuar...{RESET}")


def menu_principal():
    """Menú principal: única fuente de verdad para el listado y el despacho."""
    return [
        (
            "DESCUBRE AYACUCHO",
            [
                ("1", "Historia de Ayacucho", show_historia),
                ("2", "Atracciones Turísticas", show_atracciones),
                ("3", "Plaza de Huamanga", show_plaza),
                ("4", "Las 33 Iglesias", show_iglesias),
                ("5", "Mapa del centro histórico", show_mapa),
                ("6", "Gastronomía Local", show_gastronomia),
                ("7", "Festividades", show_festividades),
                ("8", "Artesanías", show_artesanias),
                ("9", "Consejos para el Viajero", show_consejos),
                ("10", "Frases en Quechua", show_quechua),
            ],
        ),
        (
            "EN LA CIUDAD",
            [
                ("11", "Emergencias y Servicios", show_emergencias),
                ("12", "Búsqueda General", buscar_general),
                ("13", "Mis Favoritos", show_favoritos),
                ("14", "Acerca de", show_acerca_de),
                ("15", "Cómo Llegar y Moverte", show_como_llegar),
            ],
        ),
        (
            "SERVICIOS Y PLANES",
            [
                ("16", "Dónde Dormir", show_alojamiento),
                ("17", "¿Dónde Comer? Restaurantes", show_restaurantes),
                ("18", "Cafeterías, Peñas y Compras", show_comercios),
                ("19", "Eventos Culturales (GPS)", show_eventos_culturales),
                ("20", "Lugares Cercanos (distancia GPS)", show_lugares_cercanos),
            ],
        ),
        (
            "ORGANIZA TU VIAJE",
            [
                ("21", "Clima Mensual", show_clima),
                ("22", "Itinerarios Sugeridos", show_itinerarios),
                ("23", "Exportar Datos (JSON)", show_exportar),
                ("24", "Mi Perfil / Registrar Usuario", show_perfil),
                ("25", "Presupuesto de Viaje", show_presupuesto),
            ],
        ),
    ]


def show_main_menu():
    clear_screen()
    logo.mostrar_logo(CYAN, RESET, YELLOW)
    print_line("Ciudad fundada el 4 de octubre de 1540 | 2,761 m.s.n.m.")
    print_line("La Ciudad de las 33 Iglesias")
    print()
    for grupo, opciones in menu_principal():
        print_seccion(grupo)
        for clave, etiqueta, _funcion in opciones:
            print_line(f"{GREEN}{clave}{RESET}. {etiqueta}")
        print()
    print_line(f"{GREEN}0{RESET}. Salir")
    print()
    return safe_input(f"  {CYAN}Selecciona una opción: {RESET}")


def show_historia():
    clear_screen()
    print_header("HISTORIA DE AYACUCHO")
    for i, h in enumerate(HISTORIAS, 1):
        print_item(i, h["titulo"])
    print()
    opcion = safe_input(f"  {CYAN}Elige una historia o [0] para volver: {RESET}")
    if opcion.isdigit():
        idx = int(opcion)
        if 1 <= idx <= len(HISTORIAS):
            clear_screen()
            print_header(HISTORIAS[idx - 1]["titulo"])
            for linea in HISTORIAS[idx - 1]["contenido"]:
                print_line(linea)
            pause()
        elif idx != 0:
            print_line(f"{RED}Número fuera de rango.{RESET}")
            pause()


def show_atracciones():
    clear_screen()
    print_header("ATRACCIONES TURÍSTICAS")
    for i, a in enumerate(ATRACCIONES, 1):
        marca = f"{YELLOW}*{RESET} " if a["nombre"] in favoritos_atracciones else ""
        print_item(i, a["nombre"], a["tipo"], marca)
        print_texto(a["descripcion"])
        print_line(f"   {CYAN}Horario:{RESET} {a['horario']}  |  {CYAN}Costo:{RESET} {a['costo']}")
        print()
    opcion = safe_input(f"  {CYAN}Elige un número para ver el detalle o [0] para volver: {RESET}")
    if opcion.isdigit():
        idx = int(opcion)
        if 1 <= idx <= len(ATRACCIONES):
            show_detalle_atraccion(ATRACCIONES[idx - 1])
        else:
            print_line(f"{RED}Número fuera de rango.{RESET}")
            pause()


def show_detalle_atraccion(a):
    clear_screen()
    print_header(f"{a['nombre']}")
    print_seccion("Información")
    print_dato("Tipo", a["tipo"])
    print_dato("Descripción", a["descripcion"])
    if a.get("ciudad"):
        print_dato("Ciudad", a["ciudad"])
    print_dato("Horario", a["horario"])
    print_dato("Costo", a["costo"])
    print_seccion("Ubicación")
    mostrar_gps(a)
    estado = f"{GREEN}Marcado como favorito{RESET}" if a["nombre"] in favoritos_atracciones else f"{YELLOW}No es favorito{RESET}"
    print_dato("Favorito", estado)
    print()
    opcion = safe_input(f"  {CYAN}[F] Favorito  [M] Google Maps  [0] Volver: {RESET}").strip().lower()
    if opcion == "f":
        toggle_favorito(a["nombre"])
        show_detalle_atraccion(a)
    elif opcion == "m":
        abrir_maps_lugar(a)
        pause()
        show_detalle_atraccion(a)


def show_gastronomia():
    clear_screen()
    print_header("GASTRONOMÍA AYACUCHANA")
    for i, g in enumerate(GASTRONOMIA, 1):
        print_item(i, g["nombre"], g["tipo"])
        print_texto(g["descripcion"])
        print_line(f"   {CYAN}Precio:{RESET} {g['precio']}")
        print()
    pause()


def show_festividades():
    clear_screen()
    print_header("FESTIVIDADES Y EVENTOS")
    for i, f in enumerate(FESTIVIDADES, 1):
        print_item(i, f["nombre"], f["fechas"])
        print_texto(f["descripcion"])
        if f.get("lugar"):
            print_texto(f"Lugar: {f['lugar']}", sangria=3, ancho=68)
        mostrar_gps(f)
        print()
    pause()
    elegir_mapa(FESTIVIDADES)


def show_artesanias():
    clear_screen()
    print_header("ARTESANÍAS LOCALES")
    for i, art in enumerate(ARTESANIAS, 1):
        print_item(i, art["nombre"])
        print_texto(art["descripcion"])
        print_texto(f"Dónde comprar: {art['donde_comprar']}", sangria=3, ancho=68)
        print_texto(f"Rango de precio: {art['precio']}", sangria=3, ancho=68)
        mostrar_gps(art)
        print()
    pause()
    elegir_mapa(ARTESANIAS)


def show_consejos():
    clear_screen()
    print_header("CONSEJOS PARA EL VIAJERO")
    for i, c in enumerate(CONSEJOS, 1):
        print_seccion(f"Consejo {i}")
        print_texto(c)
        print()
    pause()


def show_plaza():
    clear_screen()
    print_header("PLAZA DE HUAMANGA")
    plaza = {
        "nombre": PLAZA_HUAMANGA["nombre"],
        "lat": PLAZA_HUAMANGA["lat"],
        "lng": PLAZA_HUAMANGA["lng"],
    }
    print_texto(PLAZA_HUAMANGA["descripcion"])
    print()
    print_seccion("Qué ver alrededor")
    for i, punto in enumerate(PLAZA_HUAMANGA["que_ver"], 1):
        print_texto(f"{i}. {punto}", sangria=3, ancho=68)
    print()
    print_seccion("Ubicación (GPS)")
    mostrar_gps(plaza, sangria=3)
    print()
    print_seccion("Consejos")
    for consejo in PLAZA_HUAMANGA["consejos"]:
        print_texto(f"- {consejo}", sangria=3, ancho=68)
    print()
    print_seccion("Sigue el recorrido")
    print_texto(
        "Opción 2 (Atracciones) y opción 4 (Las 33 Iglesias) completan la "
        "vuelta al centro histórico partiendo de la plaza.",
        sangria=3,
        ancho=68,
    )
    pause()
    elegir_mapa([plaza])


def show_iglesias():
    clear_screen()
    print_header("LAS 33 IGLESIAS")
    print_texto(
        "Ayacucho se conoce como la Ciudad de las 33 Iglesias. Aquí tienes "
        f"{plural(len(IGLESIAS), 'templo', 'templos')} del centro histórico "
        "y de los barrios que rodean la Plaza de Huamanga."
    )
    print()
    print_seccion("Templos para visitar")
    for i, iglesia in enumerate(IGLESIAS, 1):
        print_item(i, iglesia["nombre"], iglesia["tipo"])
        print_line(f"   {CYAN}Barrio:{RESET} {iglesia['barrio']}")
        print_texto(iglesia["dato"])
        mostrar_gps(iglesia)
        if iglesia.get("gps_referencia"):
            print_texto(
                "Coordenada de referencia del centro histórico; confirma el "
                "punto exacto antes de salir.",
                sangria=3,
                ancho=68,
            )
        print()
    print_seccion("Cómo usar esta lista")
    print_texto(
        "Los templos con GPS se abren en Google Maps con la opción [M]; los "
        "demás se ubican por el barrio indicado, todos a pocos minutos a pie "
        "de la plaza.",
        sangria=3,
        ancho=68,
    )
    pause()
    elegir_mapa(IGLESIAS)


MAPA_COLUMNAS = 59
MAPA_FILAS = 17


def show_mapa():
    """Mapa esquemático del centro histórico, proyectado desde coordenadas."""
    puntos = datos.puntos_del_mapa_centro()
    lats = [p["lat"] for p in puntos]
    lngs = [p["lng"] for p in puntos]
    lat_span = max(lats) - min(lats) or 1e-6
    lng_span = max(lngs) - min(lngs) or 1e-6
    # Margen de una casilla para que ningún punto quede pegado al marco.
    lat_pad = lat_span / (MAPA_FILAS - 1)
    lng_pad = lng_span / (MAPA_COLUMNAS - 1)
    lat_min, lat_max = min(lats) - lat_pad, max(lats) + lat_pad
    lng_min, lng_max = min(lngs) - lng_pad, max(lngs) + lng_pad
    rejilla = [["." for _ in range(MAPA_COLUMNAS)] for _ in range(MAPA_FILAS)]
    for numero, punto in enumerate(puntos, 1):
        columna = round(
            (punto["lng"] - lng_min) / (lng_max - lng_min) * (MAPA_COLUMNAS - 1)
        )
        fila = round(
            (lat_max - punto["lat"]) / (lat_max - lat_min) * (MAPA_FILAS - 1)
        )
        rejilla[fila][columna] = str(numero)

    metros_columna = (
        (lng_max - lng_min) * 111320 * math.cos(math.radians(13.16))
        / (MAPA_COLUMNAS - 1)
    )
    metros_fila = (lat_max - lat_min) * 110540 / (MAPA_FILAS - 1)

    clear_screen()
    print_header("MAPA DEL CENTRO HISTÓRICO")
    print_seccion("Cómo leer el mapa")
    print_texto(
        "El norte queda arriba. Cada número marca un punto con coordenada "
        "publicada y su posición sale de su GPS, con la misma escala en ambos "
        "ejes: la distancia relativa entre lugares es fiel.",
        sangria=3,
        ancho=72,
    )
    print_texto(
        f"Cada casilla equivale a unos {round(metros_columna)} m de este a "
        f"oeste y {round(metros_fila)} m de norte a sur. El dibujo es un "
        "esquema orientativo, no un plano de calles.",
        sangria=3,
        ancho=72,
    )
    print()
    print_line(" " * 30 + f"{BOLD}{YELLOW}N{RESET}")
    borde = f"{YELLOW}+{'-' * MAPA_COLUMNAS}+{RESET}"
    print_line(borde)
    for fila in rejilla:
        contenido = "".join(
            f"{BOLD}{YELLOW}{c}{RESET}" if c != "." else "." for c in fila
        )
        print_line(f"{YELLOW}|{RESET}{contenido}{YELLOW}|{RESET}")
    print_line(borde)
    print()
    print_seccion("Puntos del mapa")
    for numero, punto in enumerate(puntos, 1):
        print_item(numero, punto["nombre"], punto.get("tipo"))
    print()
    print_texto(
        "Las iglesias sin coordenada publicada no entran en el mapa: aparecen "
        "en la pantalla Las 33 Iglesias con la referencia de la ciudad.",
        sangria=3,
        ancho=72,
    )
    pause()
    elegir_mapa(puntos)


def show_emergencias():
    clear_screen()
    print_header("EMERGENCIAS Y SERVICIOS")
    print_texto(
        "Guarda estos números antes de salir. Los de emergencia se marcan "
        "desde cualquier teléfono, incluso sin saldo."
    )
    print()
    print_seccion("Emergencias")
    for e in [x for x in EMERGENCIAS if x["numero"].isdigit()]:
        print_line(f"{BOLD}{YELLOW}{e['numero']}{RESET}   {BOLD}{e['servicio']}{RESET}")
        print_texto(e["descripcion"])
        print()
    print_seccion("Salud y atención en la ciudad")
    for e in [x for x in EMERGENCIAS if not x["numero"].isdigit()]:
        print_line(f"{BOLD}{YELLOW}{e['servicio']}{RESET}")
        print_texto(e["descripcion"], sangria=3, ancho=68)
        print()
    print_seccion("Recomendaciones")
    print_texto(
        "Los cuatro números de atención son gratuitos y valen para todo el "
        "país.",
        sangria=3,
        ancho=68,
    )
    print_texto(
        "Anota el nombre y la dirección de tu hospedaje: te los pedirán en "
        "cualquier llamada.",
        sangria=3,
        ancho=68,
    )
    print_texto(
        "En el centro histórico atiende personal de salud en los puestos de "
        "salud del distrito de Andrés Avelino Cáceres.",
        sangria=3,
        ancho=68,
    )
    pause()


def show_quechua():
    clear_screen()
    print_header("FRASES EN QUECHUA")
    print_texto(
        "Ayacucho es tierra quechua. Con un saludo en quechua abres muchas "
        "puertas en el mercado y en los barrios; estas frases alcanzan para "
        "empezar."
    )
    print()
    for bloque in QUECHUA:
        print_seccion(bloque["grupo"])
        for frase in bloque["frases"]:
            print_line(
                f"{BOLD}{YELLOW}{frase['quechua']}{RESET}  ->  {frase['espanol']}"
            )
        print()
    print_seccion("Para empezar")
    print_texto(
        'Saluda con "Imaynan" y agradece con "Añay": es la forma ceremonial '
        "de Ayacucho y siempre es bien recibida.",
        sangria=3,
        ancho=68,
    )
    pause()


def show_favoritos():
    clear_screen()
    print_header("MIS FAVORITOS")
    lista = [a for a in ATRACCIONES if a["nombre"] in favoritos_atracciones]
    if not lista:
        print_line(f"{YELLOW}Aún no tienes favoritos. Ve a Atracciones y marca con [F].{RESET}")
    else:
        for i, a in enumerate(lista, 1):
            print_item(i, a["nombre"], a["tipo"])
            print_texto(a["descripcion"])
            print_line(f"   {CYAN}Horario:{RESET} {a['horario']}  |  {CYAN}Costo:{RESET} {a['costo']}")
            print()
    pause()


def show_acerca_de():
    clear_screen()
    print_header("ACERCA DE")
    logo.mostrar_logo(CYAN, RESET, YELLOW)
    print_seccion("La app")
    print_line(f"{BOLD}App de Turismo: Ayacucho, Perú{RESET}  |  {CYAN}Versión:{RESET} {__version__}")
    print_line("Guía de línea de comandos de la Ciudad de las 33 Iglesias, con el")
    print_line("centro histórico y la Plaza de Huamanga como hilo conductor.")
    print_seccion("Recursos")
    print_line(f"{CYAN}Sitio oficial:{RESET} {INFO_URL}")
    print_line(f"{CYAN}Logo vectorial:{RESET} {logo.ARCHIVO_SVG.name} (512 x 512)")
    print_line(f"{CYAN}Logo en texto:{RESET} crea 'logo.txt' en la raíz para usar el tuyo")
    print_line(f"{CYAN}Datos:{RESET} {len(datos.todos_los_lugares())} lugares con GPS | "
               f"{len(ITINERARIOS)} itinerarios | rutas guardadas en rutas.json")
    pause()


def show_como_llegar():
    clear_screen()
    print_header(COMO_LLEGAR["titulo"])
    print_seccion("Cómo llegar a Ayacucho")
    for i, o in enumerate(COMO_LLEGAR["llegada"], 1):
        print_line(f"{YELLOW}{i}. {o['medio']}{RESET}")
        print_texto(o["descripcion"])
        print_line(f"   {CYAN}Tiempo:{RESET} {o['tiempo']}  |  {CYAN}Costo:{RESET} {o['costo']}")
        print()
    if COMO_LLEGAR.get("puntos_de_llegada"):
        print_seccion("Puntos de llegada (GPS)")
        for p in COMO_LLEGAR["puntos_de_llegada"]:
            print_line(f"{YELLOW}{p['lugar']}{RESET}")
            print_texto(p["descripcion"])
            mostrar_gps(p)
            print()
    print_seccion("Moverse dentro de la ciudad")
    for i, d in enumerate(COMO_LLEGAR["desplazamiento"], 1):
        print_texto(f"{i}. {d}", sangria=3, ancho=72)
    print()
    pause()
    elegir_mapa(COMO_LLEGAR.get("puntos_de_llegada", []))


def buscar_general():
    clear_screen()
    print_header("BÚSQUEDA GENERAL")
    query = safe_input(f"  {CYAN}Escribe un término (nombre, tipo, plato, festividad...): {RESET}").strip().lower()
    if not query:
        print_line(f"{RED}No se ingresó ningún término de búsqueda.{RESET}")
        pause()
        return
    colecciones = [
        ("Atracciones", ATRACCIONES, ("nombre", "tipo", "descripcion")),
        ("Iglesias", IGLESIAS, ("nombre", "tipo", "barrio", "dato")),
        ("Gastronomía", GASTRONOMIA, ("nombre", "tipo", "descripcion")),
        ("Festividades", FESTIVIDADES, ("nombre", "fechas", "descripcion", "lugar", "ciudad")),
        ("Artesanías", ARTESANIAS, ("nombre", "descripcion", "donde_comprar", "ciudad")),
        ("Dónde Dormir", datos.todos_alojamientos(), ("nombre", "tipo", "descripcion", "ciudad", "zona", "provincia")),
        ("¿Dónde Comer?", datos.todos_restaurantes(), ("nombre", "tipo", "descripcion", "ciudad", "zona", "provincia")),
        ("Cafeterías, Peñas y Compras", datos.todos_comercios(), ("nombre", "tipo", "descripcion", "ciudad", "zona", "provincia", "categoria")),
        ("Eventos Culturales", EVENTOS_CULTURALES, ("nombre", "tipo", "fechas", "lugar", "descripcion", "ciudad", "provincia")),
    ]
    total = 0
    print()
    for etiqueta, items, campos in colecciones:
        resultados = [
            item for item in items
            if any(query in str(item.get(campo, "")).lower() for campo in campos)
        ]
        if not resultados:
            continue
        total += len(resultados)
        print_seccion(f"{etiqueta} ({len(resultados)})")
        for item in resultados:
            nombre = item.get("nombre") or item.get("titulo")
            print_texto(f"- {nombre}", sangria=3, ancho=68)
            tipo = item.get("tipo", "")
            if tipo:
                print_texto(f"[{tipo}]", sangria=5, ancho=66)
        print()
    if total == 0:
        print_line(f"{RED}No se encontraron resultados para \"{query}\".{RESET}")
    else:
        print_line(f"{GREEN}Se encontraron {total} resultado(s) en total.{RESET}")
    pause()


def pedir_punto_referencia():
    """Pide una ciudad o unas coordenadas y devuelve (lat, lng) o None."""
    print_seccion("Punto de referencia")
    print_line(f"{YELLOW}1.{RESET} Elegir ciudad o pueblo")
    print_line(f"{YELLOW}2.{RESET} Escribir coordenadas")
    opcion = safe_input(f"  {CYAN}Elige [1/2] o [0] volver: {RESET}").strip()
    if opcion == "1":
        ciudades = list(datos.GPS_CIUDADES)
        print_seccion(f"Ciudades y pueblos ({len(ciudades)})")
        for i, ciudad in enumerate(ciudades, 1):
            print_line(f"{GREEN}{i:>2}.{RESET} {ciudad}")
        print()
        indice = safe_input(f"  {CYAN}Número de ciudad o [0] volver: {RESET}").strip()
        if indice.isdigit() and 1 <= int(indice) <= len(ciudades):
            return datos.GPS_CIUDADES[ciudades[int(indice) - 1]]
        return None
    if opcion == "2":
        print_seccion("Coordenadas decimales")
        lat = safe_input("  Latitud (ej. -13.1588): ").strip().replace(",", ".")
        lng = safe_input("  Longitud (ej. -74.2240): ").strip().replace(",", ".")
        try:
            return float(lat), float(lng)
        except ValueError:
            print_line(f"{RED}Coordenadas no válidas.{RESET}")
            pause()
            return None
    return None


def show_lugares_cercanos():
    """Lista los lugares de la región ordenados por distancia a un punto."""
    while True:
        clear_screen()
        print_header("LUGARES CERCANOS (GPS)")
        print_line("Encuentra qué lugares tienes cerca y ábrelos en Google Maps.")
        print()
        origen = pedir_punto_referencia()
        if not origen:
            return
        cantidad = safe_input("  Cuántos lugares mostrar? (Enter = 15): ").strip()
        try:
            limite = int(cantidad) if cantidad else 15
        except ValueError:
            limite = 15
        if limite <= 0:
            print_line(f"{RED}La cantidad debe ser mayor que cero.{RESET}")
            pause()
            continue

        cercanos = []
        for lugar in datos.todos_los_lugares():
            km = gps.distancia(origen[0], origen[1], lugar["lat"], lugar["lng"])
            cercanos.append((km, lugar))
        cercanos.sort(key=lambda item: item[0])
        cercanos = cercanos[:limite]

        clear_screen()
        print_header("LUGARES MÁS CERCANOS")
        print_line(f"{CYAN}Origen:{RESET} {origen[0]:.6f}, {origen[1]:.6f}  ({gps.dms(*origen)})")
        print()
        for i, (km, lugar) in enumerate(cercanos, 1):
            ciudad = lugar.get("ciudad") or lugar.get("provincia") or "-"
            print_item(i, lugar["nombre"], lugar["seccion"])
            print_line(f"   {CYAN}Distancia:{RESET} {km:.2f} km  |  {CYAN}Ciudad:{RESET} {ciudad}")
            mostrar_gps(lugar)
            print()
        print_line(f"{GREEN}Mostrando {len(cercanos)} de {len(datos.todos_los_lugares())} lugares.{RESET}")
        pause()
        elegir_mapa([lugar for _, lugar in cercanos])


def _entradas_de(coleccion, clave):
    """Entradas de una categoría, tolerando {clave: [entradas]} y {clave: {prov: [entradas]}}."""
    valor = coleccion[clave]
    if isinstance(valor, dict):
        return [entrada for entradas in valor.values() for entrada in entradas]
    return list(valor)


def _iter_fichas(coleccion):
    """Recorre (categoria, provincia, entrada) en cualquiera de los dos formatos."""
    for categoria, valor in coleccion.items():
        if isinstance(valor, dict):
            for provincia, entradas in valor.items():
                for entrada in entradas:
                    yield categoria, provincia, entrada
        else:
            for entrada in valor:
                yield categoria, categoria, entrada


def mostrar_categorias_geo(titulo, coleccion):
    """Submenú de provincias o categorías con la cantidad de opciones de cada una."""
    print_seccion(titulo)
    for i, categoria in enumerate(coleccion, 1):
        print_line(
            f"{GREEN}{i}{RESET}. {categoria} "
            f"({plural(len(_entradas_de(coleccion, categoria)), 'opción', 'opciones')})"
        )
    print_line(f"{GREEN}T{RESET}. Ver todo")


def mostrar_ficha_geo(entrada, provincia=None):
    """Ficha de hospedaje, restaurante o comercio con sangría uniforme."""
    tipo = f" [{GREEN}{entrada['tipo']}{RESET}]" if entrada.get("tipo") else ""
    lugar = f" ({provincia})" if provincia else ""
    print_line(f"{BOLD}{MAGENTA}{entrada['nombre']}{RESET}{tipo}{lugar}")
    print_texto(entrada["descripcion"])
    rango = entrada.get("rango_precio")
    ubicacion = f"Ciudad: {entrada.get('ciudad', '-')}"
    if rango:
        ubicacion += f"  |  Rango: {rango}"
    print_texto(ubicacion, sangria=3, ancho=68)
    if entrada.get("zona"):
        print_texto(f"Zona: {entrada['zona']}", sangria=3, ancho=68)
    estilo = entrada.get("estilo")
    estrellas = entrada.get("estrellas")
    if estilo and estrellas:
        print_texto(f"Estilo: {estilo}  |  {estrellas} estrellas", sangria=3, ancho=68)
    elif estilo:
        print_texto(f"Estilo: {estilo}  |  sin estrellas clasificadas", sangria=3, ancho=68)
    elif estrellas:
        print_texto(f"Estrellas: {estrellas}", sangria=3, ancho=68)
    if entrada.get("servicios"):
        print_texto(f"Servicios: {entrada['servicios']}", sangria=3, ancho=68)
    mostrar_gps(entrada)
    print()


def mostrar_geo_por_categoria(coleccion):
    """Dumps de todas las categorías agrupadas, usado por los tres catálogos."""
    mostrados = []
    categoria_actual = None
    for categoria, provincia, entrada in _iter_fichas(coleccion):
        if categoria != categoria_actual:
            print_seccion(categoria)
            categoria_actual = categoria
        mostrados.append(entrada)
        mostrar_ficha_geo(entrada, provincia)
    return mostrados


def _alojamientos_de(campo, valor):
    """Hospedajes que cumplen un filtro de estilo o franja de precio."""
    return [a for a in datos.todos_alojamientos() if a.get(campo) == valor]


def _mostrar_alojamientos_filtrados(titulo, alojamientos):
    """Pantalla de resultados de un filtro, con ficha, GPS y apertura en Maps."""
    clear_screen()
    print_header(f"HOSPEDAJES - {titulo}")
    for a in alojamientos:
        mostrar_ficha_geo(a, a["provincia"])
    pause()
    elegir_mapa(alojamientos)


def show_alojamiento_por_estilo():
    estilos = list(dict.fromkeys(a["estilo"] for a in datos.todos_alojamientos() if a.get("estilo")))
    while True:
        clear_screen()
        print_header("FILTRAR HOSPEDAJES POR ESTILO")
        for i, estilo in enumerate(estilos, 1):
            total = len(_alojamientos_de("estilo", estilo))
            print_item(i, estilo, plural(total, "hospedaje", "hospedajes"))
        print()
        opcion = safe_input("  Elige un estilo o [0] volver: ").strip()
        if opcion == "0":
            return
        if opcion.isdigit() and 1 <= int(opcion) <= len(estilos):
            estilo = estilos[int(opcion) - 1]
            _mostrar_alojamientos_filtrados(f"ESTILO {estilo.upper()}", _alojamientos_de("estilo", estilo))
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def show_alojamiento_por_precio():
    while True:
        clear_screen()
        print_header("FILTRAR HOSPEDAJES POR PRECIO")
        print_seccion("Franjas calculadas con el promedio del rango de precios")
        for i, (franja, ayuda) in enumerate(datos.FRANJAS_ALOJAMIENTO, 1):
            total = len(_alojamientos_de("franja", franja))
            print_item(i, franja, f"{ayuda} ({plural(total, 'hospedaje', 'hospedajes')})")
        print()
        opcion = safe_input("  Elige una franja o [0] volver: ").strip()
        if opcion == "0":
            return
        if opcion.isdigit() and 1 <= int(opcion) <= len(datos.FRANJAS_ALOJAMIENTO):
            franja = datos.FRANJAS_ALOJAMIENTO[int(opcion) - 1][0]
            _mostrar_alojamientos_filtrados(f"PRECIO {franja.upper()}", _alojamientos_de("franja", franja))
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def show_alojamiento():
    while True:
        clear_screen()
        print_header("DÓNDE DORMIR EN LA REGIÓN DE AYACUCHO")
        mostrar_categorias_geo(
            f"Hospedajes por provincia ({plural(len(ALOJAMIENTO), 'provincia', 'provincias')})",
            ALOJAMIENTO,
        )
        print()
        opcion = safe_input(
            "  Elige una provincia, [E] estilo, [P] precio, [T] todas o [0] volver: "
        ).strip()
        if opcion.lower() == "e":
            show_alojamiento_por_estilo()
        elif opcion.lower() == "p":
            show_alojamiento_por_precio()
        elif opcion.lower() == "t":
            clear_screen()
            print_header("TODOS LOS HOSPEDAJES")
            mostrados = mostrar_geo_por_categoria(ALOJAMIENTO)
            pause()
            elegir_mapa(mostrados)
        elif opcion.isdigit() and 1 <= int(opcion) <= len(ALOJAMIENTO):
            provincia = list(ALOJAMIENTO.keys())[int(opcion) - 1]
            clear_screen()
            print_header(f"HOSPEDAJES - {provincia.upper()}")
            for a in ALOJAMIENTO[provincia]:
                mostrar_ficha_geo(a)
            pause()
            elegir_mapa(ALOJAMIENTO[provincia])
        elif opcion == "0":
            return
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def show_restaurantes():
    while True:
        clear_screen()
        print_header("DÓNDE COMER EN LA REGIÓN DE AYACUCHO")
        mostrar_categorias_geo(
            f"Restaurantes por provincia ({plural(len(RESTAURANTES), 'provincia', 'provincias')})",
            RESTAURANTES,
        )
        print()
        opcion = safe_input("  Elige una provincia, [T] todas o [0] volver: ").strip()
        if opcion.lower() == "t":
            clear_screen()
            print_header("TODOS LOS RESTAURANTES")
            mostrados = mostrar_geo_por_categoria(RESTAURANTES)
            pause()
            elegir_mapa(mostrados)
        elif opcion.isdigit() and 1 <= int(opcion) <= len(RESTAURANTES):
            provincia = list(RESTAURANTES.keys())[int(opcion) - 1]
            clear_screen()
            print_header(f"RESTAURANTES - {provincia.upper()}")
            for r in RESTAURANTES[provincia]:
                mostrar_ficha_geo(r)
            pause()
            elegir_mapa(RESTAURANTES[provincia])
        elif opcion == "0":
            return
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def show_comercios_categoria(categoria):
    opciones = COMERCIOS[categoria]
    while True:
        clear_screen()
        print_header(f"{categoria.upper()} EN LA REGIÓN DE AYACUCHO")
        mostrar_categorias_geo(
            f"Locales por provincia ({plural(len(opciones), 'provincia', 'provincias')})",
            opciones,
        )
        print()
        opcion = safe_input("  Elige una provincia, [T] todas o [0] volver: ").strip()
        if opcion.lower() == "t":
            clear_screen()
            print_header(f"{categoria.upper()} - TODAS LAS PROVINCIAS")
            mostrados = mostrar_geo_por_categoria(opciones)
            pause()
            elegir_mapa(mostrados)
        elif opcion.isdigit() and 1 <= int(opcion) <= len(opciones):
            provincia = list(opciones.keys())[int(opcion) - 1]
            clear_screen()
            print_header(f"{categoria.upper()} - {provincia.upper()}")
            for c in opciones[provincia]:
                mostrar_ficha_geo(c)
            pause()
            elegir_mapa(opciones[provincia])
        elif opcion == "0":
            return
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def show_comercios():
    while True:
        clear_screen()
        print_header("CAFETERÍAS, PEÑAS, CENTROS COMERCIALES Y TIENDAS")
        print_texto("Descubre opciones de café, música en vivo y compras para todos los presupuestos.")
        print()
        mostrar_categorias_geo("Categorías", COMERCIOS)
        print()
        opcion = safe_input("  Elige una categoría, [T] todas o [0] volver: ").strip()
        if opcion.lower() == "t":
            clear_screen()
            print_header("TODOS LOS COMERCIOS")
            mostrados = mostrar_geo_por_categoria(COMERCIOS)
            pause()
            elegir_mapa(mostrados)
        elif opcion.isdigit() and 1 <= int(opcion) <= len(COMERCIOS):
            categoria = list(COMERCIOS.keys())[int(opcion) - 1]
            show_comercios_categoria(categoria)
        elif opcion == "0":
            return
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def mostrar_gps(entrada, sangria=3):
    coord = gps.coordenadas_de(entrada) or datos.gps_de(entrada)
    if not coord:
        return
    espacio = " " * sangria
    lat, lng = coord
    print_line(f"{espacio}{BOLD}GPS:{RESET}       {lat:.6f}, {lng:.6f}  ({gps.dms(lat, lng)})")
    print_line(f"{espacio}{BOLD}Google Maps:{RESET} {gps.url_maps(lat, lng, entrada.get('nombre'))}")


def abrir_maps_lugar(entrada):
    coord = gps.coordenadas_de(entrada) or datos.gps_de(entrada)
    if not coord:
        print_line(f"{YELLOW}Este lugar no tiene coordenadas GPS registradas.{RESET}")
        return None
    url = gps.url_maps(*coord, entrada.get("nombre"))
    if gps.abrir_maps(url):
        print_line(f"{GREEN}Abriendo Google Maps en tu navegador...{RESET}")
    else:
        print_line(f"{YELLOW}No se pudo abrir el navegador.{RESET}")
    print_line(f"{CYAN}Si no se abrió, copia y pega:{RESET} {url}")
    return url


def elegir_mapa(entradas):
    """Permite abrir en Google Maps cualquiera de los lugares listados."""
    if not entradas:
        return
    print()
    opcion = safe_input(
        "  Número para abrir en Google Maps (Enter o [0] volver): "
    ).strip().lower()
    if opcion in ("0", ""):
        return
    if opcion == "m":
        print_line(f"{YELLOW}Escribe el número del lugar que quieres abrir en el mapa.{RESET}")
        pause()
        return
    if not opcion.isdigit() or not 1 <= int(opcion) <= len(entradas):
        print_line(f"{RED}Número fuera de rango.{RESET}")
        pause()
        return
    abrir_maps_lugar(entradas[int(opcion) - 1])
    pause()


def show_detalle_evento(ev):
    while True:
        clear_screen()
        print_header(ev["nombre"])
        print_seccion("Ficha del evento")
        print_dato("Tipo", ev["tipo"])
        print_dato("Fechas", ev["fechas"])
        print_dato("Lugar", ev["lugar"])
        print_dato("Ciudad/Provincia", f"{ev['ciudad']} ({ev.get('provincia', '-')})")
        print_dato("Costo", ev.get("costo", "Entrada libre"))
        print_dato("Descripción", ev["descripcion"])
        print_seccion("Ubicación")
        mostrar_gps(ev)
        print()
        opcion = safe_input(f"  {CYAN}[M] Abrir en Google Maps  [0] Volver: {RESET}").strip().lower()
        if opcion == "m":
            abrir_maps_lugar(ev)
            pause()
        elif opcion == "0":
            return


def show_eventos_culturales():
    while True:
        clear_screen()
        print_header("EVENTOS CULTURALES EN AYACUCHO")
        print_texto("Festivales, ferias, concursos y encuentros, con GPS para llegar fácil.")
        print()
        print_seccion(f"Eventos ({len(EVENTOS_CULTURALES)})")
        for i, ev in enumerate(EVENTOS_CULTURALES, 1):
            print_item(i, ev["nombre"], ev["tipo"])
            print_texto(f"{ev['fechas']} | {ev['lugar']} | {ev['ciudad']}", sangria=3, ancho=68)
        print()
        opcion = safe_input("  Elige un evento para ver el detalle o [0] volver: ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(EVENTOS_CULTURALES):
            show_detalle_evento(EVENTOS_CULTURALES[int(opcion) - 1])
        elif opcion == "0":
            return
        else:
            print_line(f"{RED}Número fuera de rango.{RESET}")
            pause()


def show_clima():
    clear_screen()
    print_header("CLIMA MENSUAL EN AYACUCHO")
    print_line("Altitud: 2,761 m.s.n.m. | Clima templado de altura")
    print()
    print_seccion("Temperaturas y lluvias")
    print_line(f"{BOLD}{'Mes':<12}{'Mín':>5}{'Máx':>5}  {'Lluvia':<8}{RESET}".rstrip())
    print_line(f"{CYAN}{'-' * 40}{RESET}")
    for c in CLIMA:
        print_line(f"{c['mes']:<12}{c['min']:>4}°{c['max']:>5}°  {c['lluvia']:<8}".rstrip())
        print_texto(c["descripcion"], sangria=6, ancho=66)
    print()
    print_seccion("Recomendaciones")
    print_line(f"{GREEN}Mejor época para visitar:{RESET} mayo a septiembre (estación seca).")
    print_line(f"{GREEN}Radiación UV alta todo el año:{RESET} usa protector solar y ropa de abrigo.")
    pause()


def show_itinerarios():
    while True:
        clear_screen()
        print_header("ITINERARIOS SUGERIDOS")
        for i, it in enumerate(ITINERARIOS, 1):
            print_item(i, it["titulo"])
            print_texto(it["descripcion"])
            for paso in it["paradas"]:
                print_texto(f"-> {paso}", sangria=6, ancho=66)
            paradas_gps = it.get("paradas_gps") or []
            if paradas_gps:
                print_line(f"   {GREEN}Paradas con GPS:{RESET} {len(paradas_gps)}")
                print_line(f"   {GREEN}Recorrido aprox:{RESET} {rutas.distancia_total({'paradas': paradas_gps})} km")
                for punto in paradas_gps:
                    print_texto(
                        f"- {punto['lugar']}: {punto['lat']:.6f}, {punto['lng']:.6f}",
                        sangria=3,
                        ancho=66,
                    )
                print_line(f"   {BOLD}Ruta en Google Maps:{RESET} {gps.url_ruta(paradas_gps)}")
            print()
        if rutas_guardadas:
            print_seccion(f"Mis rutas guardadas ({len(rutas_guardadas)})")
            for i, r in enumerate(rutas_guardadas, 1):
                print_line(f"   {GREEN}{i}.{RESET} {r['titulo']} ({len(r['paradas'])} paradas)")
            print()
        opcion = safe_input(
            "  Elige un itinerario, [G] mis rutas guardadas o [0] volver: "
        ).strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(ITINERARIOS):
            show_detalle_itinerario(ITINERARIOS[int(opcion) - 1])
        elif opcion.lower() == "g":
            show_mis_rutas()
        elif opcion == "0":
            return
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def mostrar_ruta(ruta, guardada=False):
    print_header(ruta["titulo"])
    if ruta.get("descripcion"):
        print_texto(ruta["descripcion"], sangria=0)
    print()
    print_seccion("Paradas")
    for i, parada in enumerate(ruta["paradas"], 1):
        print_item(i, parada["lugar"])
        print_line(
            f"   {CYAN}GPS:{RESET} {parada['lat']:.6f}, {parada['lng']:.6f}"
            f"  ({gps.dms(parada['lat'], parada['lng'])})"
        )
    print()
    print_seccion("Resumen")
    print_line(f"{GREEN}Recorrido aproximado:{RESET} {rutas.distancia_total(ruta)} km")
    print_line(f"{BOLD}Ruta en Google Maps:{RESET} {rutas.url_de_ruta(ruta)}")
    print_line(f"{CYAN}Tip:{RESET} pulsa [M] para abrirla sin copiar el enlace.")
    if guardada:
        print_line(f"{CYAN}Guardada el:{RESET} {ruta.get('creado', '-')}")


def show_detalle_itinerario(itinerario):
    while True:
        clear_screen()
        mostrar_ruta(
            {
                "titulo": itinerario["titulo"],
                "descripcion": itinerario["descripcion"],
                "paradas": itinerario.get("paradas_gps", []),
            }
        )
        print()
        opcion = safe_input(
            "  [G] Guardar esta ruta  [M] Abrir en Google Maps  [0] Volver: "
        ).strip().lower()
        if opcion == "g":
            guardar_ruta(itinerario["titulo"])
            pause()
        elif opcion == "m":
            url = gps.url_ruta(itinerario.get("paradas_gps", []))
            if not url:
                print_line(f"{YELLOW}Esta ruta no tiene coordenadas para el mapa.{RESET}")
            elif gps.abrir_maps(url):
                print_line(f"{GREEN}Abriendo la ruta en Google Maps...{RESET}")
            else:
                print_line(f"{YELLOW}No se pudo abrir el navegador.{RESET}")
                print_line(f"{CYAN}Copia y pega:{RESET} {url}")
            pause()
        elif opcion == "0":
            return


def guardar_ruta(titulo):
    """Guarda un itinerario de los sugeridos en rutas.json."""
    itinerario = next((i for i in ITINERARIOS if i["titulo"] == titulo), None)
    if itinerario is None:
        print_line(f"{RED}Itinerario no encontrado.{RESET}")
        return None
    try:
        actualizadas = rutas.agregar_ruta(rutas.ruta_desde_itinerario(itinerario))
    except OSError as error:
        print_line(f"{RED}No se pudo guardar la ruta: {error}{RESET}")
        return None
    if actualizadas is None:
        print_line(f"{RED}La ruta no tiene suficientes paradas con GPS.{RESET}")
        return None
    rutas_guardadas[:] = actualizadas
    print_line(f"{GREEN}Ruta guardada: {titulo}{RESET}")
    return actualizadas


def show_mis_rutas():
    global rutas_guardadas
    while True:
        clear_screen()
        print_header("MIS RUTAS GUARDADAS")
        rutas_guardadas = rutas.cargar_rutas()
        if not rutas_guardadas:
            print_line(f"{YELLOW}Aún no tienes rutas guardadas.{RESET}")
            print_line("Ve a Itinerarios Sugeridos y elige [G] para guardar una.")
            pause()
            return
        for i, r in enumerate(rutas_guardadas, 1):
            print_item(i, r["titulo"])
            print_line(
                f"   {GREEN}{len(r['paradas'])} paradas  |  "
                f"{rutas.distancia_total(r)} km  |  guardada: {r.get('creado', '-')}{RESET}"
            )
        print()
        opcion = safe_input(
            "  [M] Número para abrir la ruta  [X] Número para borrar  [0] Volver: "
        ).strip().lower()
        if opcion in ("0", ""):
            return
        if opcion == "x":
            numero = safe_input("  Número de ruta a borrar: ").strip()
            if numero.isdigit() and 1 <= int(numero) <= len(rutas_guardadas):
                titulo = rutas_guardadas[int(numero) - 1]["titulo"]
                try:
                    rutas_guardadas[:] = rutas.eliminar_ruta(titulo)
                except OSError as error:
                    print_line(f"{RED}No se pudo borrar: {error}{RESET}")
                else:
                    print_line(f"{GREEN}Ruta borrada: {titulo}{RESET}")
            else:
                print_line(f"{RED}Número fuera de rango.{RESET}")
            pause()
        elif opcion == "m":
            numero = safe_input("  Número de ruta: ").strip()
            if numero.isdigit() and 1 <= int(numero) <= len(rutas_guardadas):
                ruta = rutas_guardadas[int(numero) - 1]
                clear_screen()
                mostrar_ruta(ruta, guardada=True)
                print()
                url = rutas.url_de_ruta(ruta)
                if url and gps.abrir_maps(url):
                    print_line(f"{GREEN}Abriendo la ruta en Google Maps...{RESET}")
                pause()
            else:
                print_line(f"{RED}Número fuera de rango.{RESET}")
                pause()
        elif opcion.isdigit() and 1 <= int(opcion) <= len(rutas_guardadas):
            ruta = rutas_guardadas[int(opcion) - 1]
            clear_screen()
            mostrar_ruta(ruta, guardada=True)
            print()
            url = rutas.url_de_ruta(ruta)
            if url and gps.abrir_maps(url):
                print_line(f"{GREEN}Abriendo la ruta en Google Maps...{RESET}")
            pause()
        else:
            print_line(f"{RED}Opción no válida.{RESET}")
            pause()


def show_exportar():
    clear_screen()
    print_header("EXPORTAR DATOS A JSON")
    ruta = safe_input(f"  {CYAN}Nombre del archivo (Enter para datos_ayacucho.json): {RESET}").strip()
    if not ruta:
        ruta = "datos_ayacucho.json"
    try:
        exportar_datos(ruta)
    except OSError as error:
        print_line(f"{RED}No se pudo exportar: {error}{RESET}")
    else:
        print_line(f"{GREEN}Datos exportados correctamente a: {ruta}{RESET}")
    pause()


def registrar_usuario():
    global usuario_actual
    clear_screen()
    print_header("REGISTRO DE USUARIO")
    print_line(f"{YELLOW}Solo se permiten usuarios mayores de {EDAD_MINIMA} años.{RESET}")
    print()
    nombre = safe_input(f"  {CYAN}Nombre y apellido: {RESET}").strip()
    if not nombre:
        print_line(f"{RED}El nombre es obligatorio. Registro cancelado.{RESET}")
        pause()
        return
    edad = pedir_edad()
    if edad is None:
        print_line(f"{RED}El registro solo está disponible para mayores de {EDAD_MINIMA} años.{RESET}")
        pause()
        return
    pais = safe_input(f"  {CYAN}País de origen: {RESET}").strip()
    ciudad = safe_input(f"  {CYAN}Ciudad: {RESET}").strip()
    email = safe_input(f"  {CYAN}Correo electrónico (opcional): {RESET}").strip()
    motivo = safe_input(f"  {CYAN}Motivo del viaje (turismo, negocios, estudio): {RESET}").strip()
    usuario_actual = {
        "nombre": nombre,
        "edad": edad,
        "pais": pais,
        "ciudad": ciudad,
        "email": email,
        "motivo": motivo or "turismo",
    }
    try:
        guardar_usuario(usuario_actual)
    except OSError as error:
        print_line(f"{RED}No se pudo guardar el usuario: {error}{RESET}")
    else:
        print_line(f"{GREEN}Usuario registrado correctamente.{RESET}")
    pause()


def pedir_edad():
    while True:
        valor = safe_input(f"  {CYAN}Edad: {RESET}").strip()
        if not valor.isdigit():
            print_line(f"{RED}La edad debe ser un número entero.{RESET}")
            continue
        edad = int(valor)
        if edad < EDAD_MINIMA:
            return None
        return edad


def show_perfil():
    global usuario_actual
    while True:
        clear_screen()
        print_header("MI PERFIL DE VIAJERO")
        if usuario_actual:
            campos = [
                ("Nombre", "nombre"),
                ("Edad", "edad"),
                ("País", "pais"),
                ("Ciudad", "ciudad"),
                ("Correo", "email"),
                ("Motivo de viaje", "motivo"),
            ]
            print_seccion("Datos del viajero")
            for etiqueta, clave in campos:
                print_dato(etiqueta, usuario_actual.get(clave) or "-")
        else:
            print_line(f"{YELLOW}No tienes perfil registrado.{RESET}")
            print_line("Regístrate para personalizar tu experiencia.")
        print()
        opcion = safe_input(f"  {CYAN}[R] Registrar/editar  [B] Borrar  [0] Volver: {RESET}").strip().lower()
        if opcion == "r":
            registrar_usuario()
        elif opcion == "b":
            if usuario_actual:
                eliminar_usuario()
                usuario_actual = None
                print_line(f"{GREEN}Perfil borrado.{RESET}")
            else:
                print_line(f"{YELLOW}No hay perfil que borrar.{RESET}")
            pause()
        elif opcion == "0":
            return


def pedir_monto(prompt: str):
    while True:
        valor = safe_input(prompt).strip().replace(",", ".")
        try:
            monto = float(valor)
        except ValueError:
            print_line(f"{RED}Ingresa un monto válido.{RESET}")
            continue
        if monto <= 0:
            print_line(f"{RED}El monto debe ser mayor que cero.{RESET}")
            continue
        return round(monto, 2)


def pedir_categoria():
    print_seccion("Categorías")
    for i, categoria in enumerate(CATEGORIAS, 1):
        print_line(f"{GREEN}{i}{RESET}. {categoria}")
    while True:
        opcion = safe_input("  Elige una categoría (1-{}): ".format(len(CATEGORIAS)))
        if opcion.isdigit() and 1 <= int(opcion) <= len(CATEGORIAS):
            return CATEGORIAS[int(opcion) - 1]
        print_line(f"{RED}Categoría no válida.{RESET}")


def show_presupuesto():
    global presupuesto_actual
    while True:
        clear_screen()
        print_header("PRESUPUESTO DE VIAJE")
        total = float(presupuesto_actual.get("presupuesto_total") or 0.0)
        if total > 0 or presupuesto_actual["gastos"]:
            gastado = total_gastado(presupuesto_actual)
            restante = presupuesto_restante(presupuesto_actual)
            barra = "#" * int(min(restante / max(total, 1), 1) * 20)
            print_seccion("Resumen")
            print_line(f"{CYAN}Presupuesto total:{RESET} S/ {total:.2f}")
            print_line(f"{YELLOW}Gastado:{RESET} S/ {gastado:.2f}")
            if restante >= 0:
                print_line(f"{GREEN}Restante:{RESET} S/ {restante:.2f}  [{barra.ljust(20)}]")
            else:
                print_line(f"{RED}Excedido por:{RESET} S/ {abs(restante):.2f}  [{'#' * 20}]")
            print()
            print_seccion("Gastos registrados")
            for i, gasto in enumerate(presupuesto_actual["gastos"], 1):
                etiqueta = f"{GREEN}{i}{RESET}. "
                print_line(f"{etiqueta}[{gasto.get('categoria', 'Otros')}] {gasto.get('concepto')}: S/ {float(gasto.get('monto') or 0.0):.2f}")
        else:
            print_line(f"{YELLOW}Aún no tienes un presupuesto definido.{RESET}")
            print_line("Define un monto total para organizar tus días en Ayacucho.")
        print()
        opcion = safe_input(
            f"  {CYAN}[T] Total  [A] Agregar gasto  [E] Eliminar  [N] Nuevo  [0] Volver: {RESET}"
        ).strip().lower()
        if opcion == "t":
            total = pedir_monto("  Monto total del presupuesto (S/): ")
            presupuesto_actual["presupuesto_total"] = total
            guardar_presupuesto(presupuesto_actual)
            print_line(f"{GREEN}Presupuesto establecido en S/ {total:.2f}.{RESET}")
            pause()
        elif opcion == "a":
            concepto = safe_input("  Concepto del gasto: ").strip()
            if not concepto:
                print_line(f"{RED}El concepto es obligatorio.{RESET}")
                pause()
                continue
            categoria = pedir_categoria()
            monto = pedir_monto("  Monto del gasto (S/): ")
            presupuesto_actual["gastos"].append(
                {"concepto": concepto, "categoria": categoria, "monto": monto}
            )
            guardar_presupuesto(presupuesto_actual)
            print_line(f"{GREEN}Gasto registrado: {concepto} - S/ {monto:.2f}{RESET}")
            pause()
        elif opcion == "e":
            if not presupuesto_actual["gastos"]:
                print_line(f"{YELLOW}No hay gastos registrados.{RESET}")
                pause()
                continue
            numero = safe_input("  Número del gasto a eliminar: ").strip()
            if numero.isdigit() and 1 <= int(numero) <= len(presupuesto_actual["gastos"]):
                eliminado = presupuesto_actual["gastos"].pop(int(numero) - 1)
                guardar_presupuesto(presupuesto_actual)
                print_line(f"{GREEN}Gasto eliminado: {eliminado['concepto']}{RESET}")
            else:
                print_line(f"{RED}Número de gasto no válido.{RESET}")
            pause()
        elif opcion == "n":
            eliminar_presupuesto()
            presupuesto_actual = presupuesto_vacio()
            print_line(f"{YELLOW}Presupuesto reiniciado.{RESET}")
            pause()
        elif opcion == "0":
            return


def verificar_acceso():
    clear_screen()
    print_header("CONTROL DE ACCESO")
    if usuario_actual:
        print_line(f"{GREEN}Bienvenido/a {usuario_actual['nombre']}!{RESET}")
        print_line("Acceso permitido.")
        print()
        return
    print_line(f"{YELLOW}Esta app es solo para mayores de {EDAD_MINIMA} años.{RESET}")
    print()
    edad = pedir_edad()
    if edad is None:
        print_line(f"{RED}Acceso denegado: debes ser mayor de {EDAD_MINIMA} años.{RESET}")
        print()
        sys.exit(0)
    print_line(f"{GREEN}Acceso permitido. Bienvenido/a!{RESET}")
    print()


def main():
    verificar_acceso()
    despacho = {
        clave: funcion
        for _grupo, opciones in menu_principal()
        for clave, _etiqueta, funcion in opciones
        if funcion
    }
    while True:
        option = show_main_menu()
        if option == "0":
            clear_screen()
            print_header("¡Hasta luego!")
            print_line(f"{GREEN}Gracias por usar Turismo Ayacucho.{RESET}")
            print_line("¡Que tengas un excelente viaje!")
            print_line(f"  {CYAN}Más información: {RESET}{INFO_URL}")
            print()
            sys.exit()
        funcion = despacho.get(option)
        if funcion is None:
            print(f"\n  {RED}Opción no válida. Intenta de nuevo.{RESET}")
            pause()
        else:
            funcion()


if __name__ == "__main__":
    main()