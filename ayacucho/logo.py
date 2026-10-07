"""Logo de la app: versión en texto para la terminal y archivo vectorial."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_SVG = RAIZ / "logo.svg"
ARCHIVO_PNG = RAIZ / "logo.png"
ARCHIVO_TEXTO = RAIZ / "logo.txt"

LETRAS = {
    "A": [" ### ", "#   #", "#####", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#### ", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", " ####"],
    "D": ["#### ", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#### ", "#    ", "#####"],
    "F": ["#####", "#    ", "#### ", "#    ", "#    "],
    "G": [" ####", "#    ", "#  ##", "#   #", " ####"],
    "H": ["#   #", "#   #", "#####", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "#####"],
    "J": ["  ###", "   # ", "   # ", "   # ", "###  "],
    "K": ["#   #", "#  # ", "###  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "#  ##", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#### ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "# # #", " ## #", "    #"],
    "R": ["#### ", "#   #", "#### ", "#  # ", "#   #"],
    "S": [" ####", "#    ", " ### ", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "# # #", "## ##", "#   #"],
    "X": ["#   #", " # # ", "  #  ", " # # ", "#   #"],
    "Y": ["#   #", " # # ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "   # ", "  #  ", " #   ", "#####"],
    "0": [" ### ", "#  ##", "# # #", "##  #", " ### "],
    "3": [" ####", "    #", " ### ", "    #", "#### "],
    " ": ["     ", "     ", "     ", "     ", "     "],
}

MONTAÑAS = [
    "        /\\        _|_        /\\",
    "       /  \\      /   \\      /  \\",
    "      /    \\    /  o  \\    /    \\",
    "     /      \\__/|     |\\__/      \\",
    "    /___________|_|_|_|___________\\",
    "        [|=|=|=|=|=|=|=|=|=|=|=|=]",
]

TAGLINE = "PLAZA DE HUAMANGA  -  CIUDAD DE LAS 33 IGLESIAS"


def texto_bloque(palabra, separador="  "):
    """Convierte una palabra en lineas de letras grandes."""
    letras = [LETRAS.get(c.upper(), LETRAS[" "]) for c in palabra]
    return [
        separador.join(letra[fila] for letra in letras)
        for fila in range(len(LETRAS["A"]))
    ]


def lineas_logo_interno():
    """Lineas del logo integrado: montanas, nombre y eslogan."""
    return MONTAÑAS + texto_bloque("AYACUCHO") + [TAGLINE]


def cargar_logo(ruta=ARCHIVO_TEXTO):
    """Devuelve las lineas de un logo.txt personalizado, o None si no existe."""
    archivo = Path(ruta)
    if not archivo.exists():
        return None
    try:
        lineas = archivo.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    lineas = lineas if lineas and lineas[-1].strip() else lineas[:-1]
    return lineas if any(linea.strip() for linea in lineas) else None


def lineas_logo():
    """Logo activo: el personalizado (logo.txt) o el integrado."""
    return cargar_logo() or lineas_logo_interno()


def ancho_logo():
    return max(len(linea) for linea in lineas_logo())


def centrar(linea, ancho):
    """Rellena a la izquierda para centrar una linea dentro de un ancho dado."""
    return " " * max(0, (ancho - len(linea)) // 2) + linea


def mostrar_logo(cyan="", reset="", yellow=""):
    """Imprime el logo activo en la terminal."""
    personalizado = cargar_logo()
    print()
    if personalizado:
        for linea in personalizado:
            print(f"{cyan}{linea}{reset}")
        print()
        return
    bloque = texto_bloque("AYACUCHO")
    ancho = len(bloque[0])
    ancho_escena = max(len(linea) for linea in MONTAÑAS)
    for linea in MONTAÑAS:
        print(f"{cyan}{centrar(linea.ljust(ancho_escena), ancho).rstrip()}{reset}")
    for fila, linea in enumerate(bloque):
        if fila in (0, len(bloque) - 1):
            print(f"{yellow}{linea}{reset}")
        else:
            print(linea)
    print(f"{cyan}{centrar(TAGLINE, ancho)}{reset}")
    print()
