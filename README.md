# App de Turismo: Ayacucho, Perú

Aplicación de línea de comandos (CLI) con información turística de Ayacucho: historias, atracciones, la Plaza de Huamanga, las iglesias del centro histórico, gastronomía, festividades, artesanías, consejos, frases en quechua, emergencias y servicios, hospedajes, restaurantes, cafeterías, peñas de música, centros comerciales, tiendas y mercados y eventos culturales en las 11 provincias de la región (Huamanga, Huanta, La Mar, Cangallo, Huanca Sancos, Víctor Fajardo, Vilcashuamán, Sucre, Lucanas, Parinacochas y Páucar del Sara Sara) con sus ciudades principales (Ayacucho, Huanta, San Miguel, Cangallo, Huanca Sancos, Huancapi, Vilcashuamán, Querobamba, Puquio, Coracora y Pausa) y hoteles/hostales/hospedajes, restaurantes y comercios reales (con rangos de precio adaptables a todos los presupuestos y filtros de hospedaje por estilo y por franja de precio), clima mensual, itinerarios sugeridos y cómo llegar/moverse. Incluye GPS (coordenadas decimales y en grados, minutos y segundos) en los 184 lugares visitables de la app: las 10 atracciones, las 6 iglesias que no están en atracciones, las 6 festividades, las 4 artesanías, los 10 eventos culturales, los 69 hospedajes, los 48 restaurantes y los 31 comercios, con enlace directo a Google Maps para ayudar a los usuarios a llegar a cualquier lugar. Cuando el punto exacto no está publicado se usa la coordenada de referencia del pueblo o ciudad. Además, "Cómo llegar" muestra los puntos de ingreso con GPS (Aeropuerto Coronel FAP Alfredo Mendívil Duarte - AYP - y Terminal Terrestre Libertadores de América) y los 3 itinerarios sugeridos listan sus paradas con coordenadas y un enlace de ruta completa en Google Maps. En todos los listados (hospedajes, restaurantes, comercios, festividades, artesanías y puntos de llegada) se puede escribir el número de un lugar para abrirlo directamente en Google Maps. La opción "Lugares Cercanos" calcula la distancia en línea recta (haversine) desde cualquier ciudad/pueblo de la región o desde coordenadas escritas a mano, y lista los lugares más próximos con su sección, distancia y GPS. Los itinerarios se pueden guardar como rutas propias (`[G]`), se muestran con el recorrido aproximado en km y se gestionan desde "Mis rutas guardadas" (abrir en Google Maps o borrar), persistidas en `rutas.json`. La app incluye un logo propio de estilo rústico y cálido: la Plaza de Huamanga de fondo (catedral con sus dos torres, portales laterales, pileta, empedrado y la sierra andina al atardecer). Hay una versión en texto que aparece en el menú principal y en "Acerca de" (`ayacucho/logo.py`, con la catedral entre las montañas y el eslogan "Plaza de Huamanga - Ciudad de las 33 Iglesias") y el archivo vectorial `logo.svg` (512x512, marco de cerámica con cuentas y paleta terracota/ocre/crema). Para usar un logo propio en la terminal, crea `logo.txt` en la raíz del proyecto con el dibujo en texto (se acepta UTF-8 con o sin BOM); si el archivo existe y tiene contenido, reemplaza al logo integrado sin tocar el código. Muestra un mapa esquemático del centro histórico en ASCII (59 x 17 casillas), con la Plaza Mayor, la Catedral, el Museo Huamanga y otras iglesias numeradas y situadas sobre su GPS real, con leyenda de cada punto. Incluye control de acceso para mayores de 18 años al iniciar, búsqueda general en toda la base de datos, registro de usuario persistido en `usuario.json`, marcado de favoritos (*) persistentes en `favoritos.json`, administración del presupuesto de viaje (presupuesto total y gastos por categoría) persistida en `presupuesto.json`, exportación de datos a JSON y sección Acerca de.

## Requisitos

- Python 3.10+

## Instalación

```bash
cd AYACUCHO
pip install -r requirements.txt
```

Para instalarla como comando (opcional):

```bash
pip install -e .
ayacucho
```

## Ejecución

```bash
python main.py
```

o como módulo:

```bash
python -m ayacucho
```

## Interfaz

Todas las pantallas comparten la misma identidad visual cálida (la del logo):

- **Encabezado** con doble regla `~~~~` y título centrado en ocre (`print_header`).
- **Subtítulos** con regla `-- Subtítulo ----` (`print_seccion`).
- **Fichas** con etiqueta y valor alineados en columnas (`print_dato`).
- **Ítems numerados** con el tipo entre corchetes; si no caben en la línea, el tipo pasa a la siguiente (`print_item`).
- **Párrafos** con sangría de 3 espacios y ajuste automático a 72 caracteres, para no pasar de las 80 columnas de la consola (`print_texto`).
- **Ayudas de red**: todos los listados ofrecen abrir un lugar por número en Google Maps, y las rutas se abren con `[M]`.

La consola de Windows puede venir en cp1252, donde los caracteres de dibujo de caja no existen, así que la interfaz usa solo caracteres imprimibles en Latin-1. Hay un test (`TestPresentacion`) que lo verifica en `cli.py`, `datos.py`, `gps.py`, `logo.py` y `rutas.py`, y otro que comprueba que ningún encabezado ni párrafo supere las 80 columnas.

El menú principal ofrece 25 opciones en cuatro grupos (Descubre Ayacucho, En la ciudad, Servicios y planes, Organiza tu viaje) y termina en `0. Salir`. El listado y el despacho salen de una sola tabla, `menu_principal()`, así que una pantalla nueva aparece en el menú y queda operativa sin tocar el bucle principal. La opción `5. Mapa del centro histórico` dibuja un esquema en la terminal con los puntos de interés numerados por coordenada real y su leyenda.

## Estructura del proyecto

```
AYACUCHO/
├── main.py            # Punto de entrada
├── pyproject.toml     # Empaquetado (entry point: ayacucho)
├── requirements.txt   # Dependencias
├── ayacucho/          # Paquete principal
│   ├── __init__.py
│   ├── __main__.py    # Soporte para python -m ayacucho
│   ├── cli.py         # Menú y pantallas de la CLI
│   ├── datos.py       # Datos turísticos
│   ├── gps.py         # Utilidades GPS (coordenadas, Google Maps, rutas y distancia)
│   ├── historias.py   # Historias de Ayacucho
│   ├── storage.py     # Persistencia de favoritos
│   ├── usuario.py     # Registro y persistencia del usuario
│   ├── presupuesto.py # Administración del presupuesto de viaje
│   ├── exporter.py    # Exportación de datos a JSON
│   ├── rutas.py       # Itinerarios y rutas guardadas por el usuario
│   └── logo.py        # Logo en texto y referencia al logo.svg
└── tests/             # Pruebas
    ├── test_datos.py
    ├── test_cli.py
    ├── test_historias.py
    ├── test_storage.py
    ├── test_usuario.py
    ├── test_presupuesto.py
    ├── test_rutas.py
    ├── test_exporter.py
    └── test_logo.py
```

## Ejecutar pruebas

```bash
python -m unittest discover -s tests -v
```

## Fuentes y avisos

- Los nombres de hospedajes, restaurantes y comercios provienen de información pública de establecimientos de turismo: el registro de establecimientos turísticos del Ministerio de Comercio Exterior y Turismo (MINCETUR) y páginas oficiales en gob.pe.
- Precios, horarios, costos de viaje y distancias son referenciales y pueden cambiar sin aviso; confirma siempre en el lugar.
- Las coordenadas GPS salen de datos públicos; cuando el punto exacto no está publicado, la app usa la coordenada de referencia de la ciudad o pueblo (ver `gps_de` en `ayacucho/datos.py`).
- El mapa del centro histórico es un esquema orientativo calculado con las coordenadas de los puntos, no un plano de calles.

## Derechos de autor

© 2026 rosalopezapari — Todos los derechos reservados.

Este proyecto no se distribuye bajo una licencia de código abierto: no se otorgan permisos de copia, modificación ni redistribución sin autorización escrita de la persona titular del repositorio.