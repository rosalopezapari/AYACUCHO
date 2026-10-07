"""Utilidades de GPS para ayudar a los usuarios a llegar a cada lugar."""
import math
import webbrowser
from urllib.parse import quote


def url_maps(lat, lng, etiqueta=""):
    """Genera el enlace de Google Maps para unas coordenadas."""
    if etiqueta:
        lugar = f"{etiqueta}, {lat:.6f}, {lng:.6f}"
    else:
        lugar = f"{lat:.6f}, {lng:.6f}"
    return "https://www.google.com/maps/search/?api=1&query=" + quote(lugar)


def url_ruta(puntos, modo="driving"):
    """Genera el enlace de Google Maps con la ruta completa (origen, paradas y destino)."""
    validos = [p for p in puntos if "lat" in p and "lng" in p]
    if len(validos) < 2:
        return url_maps(*coordenadas_de(validos[0])) if validos else ""

    def referencia(punto):
        lat, lng = punto["lat"], punto["lng"]
        etiqueta = punto.get("lugar", "")
        base = f"{lat:.6f},{lng:.6f}"
        return f"{base} ({etiqueta})" if etiqueta else base

    url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote(referencia(validos[0]))}"
        f"&destination={quote(referencia(validos[-1]))}"
        f"&travelmode={modo}"
    )
    intermedias = validos[1:-1]
    if intermedias:
        unidas = "|".join(referencia(p) for p in intermedias)
        url += "&waypoints=" + quote(unidas, safe="|")
    return url


def _a_dms(valor, hemisferio_pos, hemisferio_neg):
    hemisferio = hemisferio_pos if valor >= 0 else hemisferio_neg
    valor = abs(valor)
    grados = int(valor)
    minutos = int((valor - grados) * 60)
    segundos = round(((valor - grados) * 60 - minutos) * 60, 1)
    if segundos >= 60:
        segundos = round(segundos - 60, 1)
        minutos += 1
    if minutos >= 60:
        minutos -= 60
        grados += 1
    return f'{grados}°{minutos}\'{segundos}" {hemisferio}'


def dms(lat, lng):
    """Convierte coordenadas decimales a grados, minutos y segundos."""
    return f"{_a_dms(lat, 'N', 'S')}  {_a_dms(lng, 'E', 'O')}"


def coordenadas_de(entrada):
    """Devuelve (lat, lng) si la entrada trae GPS, si no None."""
    if "lat" in entrada and "lng" in entrada:
        return entrada["lat"], entrada["lng"]
    return None


def distancia(lat1, lng1, lat2, lng2):
    """Distancia en kilómetros entre dos coordenadas (fórmula del haversine)."""
    radio_tierra = 6371.0
    lat1, lng1, lat2, lng2 = map(math.radians, (lat1, lng1, lat2, lng2))
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )
    return 2 * radio_tierra * math.asin(math.sqrt(a))


def distancia_entre(origen, destino):
    """Distancia en km entre dos entradas con GPS; None si a alguna le falta."""
    coord_origen = coordenadas_de(origen)
    coord_destino = coordenadas_de(destino)
    if not coord_origen or not coord_destino:
        return None
    return distancia(*coord_origen, *coord_destino)


def abrir_maps(url):
    """Abre el enlace en el navegador del sistema."""
    return webbrowser.open(url)