"""
Configuración central del Radar AGRODASIN.

Define palabras clave, entidades prioritarias, territorios y reglas de
puntuación basadas en la Matriz de Vigilancia AGRODASIN.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# SECOP II – Datos Abiertos
# Conjunto: "SECOP II - Procesos de Contratación"
# Endpoint Socrata (datos.gov.co)
# ---------------------------------------------------------------------------
SECOP_DATASET_ID = "p6dx-8zbt"
SECOP_BASE_URL = "https://www.datos.gov.co/resource/{dataset}.json"
SECOP_API_URL = SECOP_BASE_URL.format(dataset=SECOP_DATASET_ID)

# Número máximo de registros por consulta (límite Socrata)
SECOP_PAGE_LIMIT = 1000

# Campos que se solicitan a la API para reducir el volumen de datos
SECOP_FIELDS = [
    "id_del_portafolio",
    "referencia_del_proceso",
    "nombre_de_la_entidad",
    "nit_entidad",
    "departamento",
    "ciudad",
    "nombre_del_procedimiento",
    "descripcion_del_procedimiento",
    "estado_del_procedimiento",
    "modalidad_de_contratacion",
    "valor_total_estimado",
    "fecha_de_publicacion_del",
    "fecha_limite_de_recepcion",
    "urlproceso",
    "codigo_unspsc",
]

# ---------------------------------------------------------------------------
# Palabras clave y puntajes de relevancia (positivos)
# ---------------------------------------------------------------------------
KEYWORDS: list[dict] = [
    # Extensión agropecuaria
    {"categoria": "Extensión agropecuaria", "clave": "extensión agropecuaria", "puntaje": 30},
    {"categoria": "Extensión agropecuaria", "clave": "asistencia técnica", "puntaje": 25},
    {"categoria": "Extensión agropecuaria", "clave": "epsea", "puntaje": 25},
    {"categoria": "Extensión agropecuaria", "clave": "servicio de extensión", "puntaje": 20},
    {"categoria": "Extensión agropecuaria", "clave": "acompañamiento técnico", "puntaje": 20},
    # Piscicultura / Acuicultura
    {"categoria": "Piscicultura", "clave": "piscicultura", "puntaje": 30},
    {"categoria": "Piscicultura", "clave": "piscícola", "puntaje": 30},
    {"categoria": "Piscicultura", "clave": "acuicultura", "puntaje": 30},
    {"categoria": "Piscicultura", "clave": "estanques", "puntaje": 20},
    {"categoria": "Piscicultura", "clave": "alevinos", "puntaje": 20},
    {"categoria": "Piscicultura", "clave": "alimento balanceado", "puntaje": 15},
    {"categoria": "Piscicultura", "clave": "pesca artesanal", "puntaje": 20},
    # Agricultura y ruralidad
    {"categoria": "Agricultura", "clave": "agricultura familiar", "puntaje": 25},
    {"categoria": "Agricultura", "clave": "productores rurales", "puntaje": 20},
    {"categoria": "Agricultura", "clave": "fortalecimiento productivo", "puntaje": 20},
    {"categoria": "Agricultura", "clave": "economía campesina", "puntaje": 20},
    {"categoria": "Agricultura", "clave": "seguridad alimentaria", "puntaje": 20},
    {"categoria": "Agricultura", "clave": "insumos agrícolas", "puntaje": 15},
    {"categoria": "Agricultura", "clave": "maquinaria agrícola", "puntaje": 15},
    {"categoria": "Agricultura", "clave": "herramientas menores", "puntaje": 10},
    # Asociaciones y organizaciones
    {"categoria": "Asociaciones", "clave": "fortalecimiento organizacional", "puntaje": 25},
    {"categoria": "Asociaciones", "clave": "asociaciones campesinas", "puntaje": 25},
    {"categoria": "Asociaciones", "clave": "economía popular", "puntaje": 20},
    {"categoria": "Asociaciones", "clave": "cooperativas", "puntaje": 15},
    {"categoria": "Asociaciones", "clave": "fortalecimiento de asociaciones", "puntaje": 25},
    {"categoria": "Asociaciones", "clave": "organización comunitaria", "puntaje": 15},
    # Formación y capacitación
    {"categoria": "Formación", "clave": "capacitación", "puntaje": 15},
    {"categoria": "Formación", "clave": "talleres", "puntaje": 10},
    {"categoria": "Formación", "clave": "formación rural", "puntaje": 20},
    {"categoria": "Formación", "clave": "diplomado", "puntaje": 10},
    {"categoria": "Formación", "clave": "acompañamiento productivo", "puntaje": 15},
    # Comercialización y compras públicas
    {"categoria": "Comercialización", "clave": "compras públicas", "puntaje": 20},
    {"categoria": "Comercialización", "clave": "abastecimiento alimentario", "puntaje": 20},
    {"categoria": "Comercialización", "clave": "mercados campesinos", "puntaje": 25},
    {"categoria": "Comercialización", "clave": "alimentación escolar", "puntaje": 20},
    {"categoria": "Comercialización", "clave": "PAE", "puntaje": 15},
    {"categoria": "Comercialización", "clave": "compra local", "puntaje": 15},
    # Medio ambiente y reforestación
    {"categoria": "Medio ambiente", "clave": "reforestación", "puntaje": 15},
    {"categoria": "Medio ambiente", "clave": "recuperación de suelos", "puntaje": 15},
    {"categoria": "Medio ambiente", "clave": "viveros", "puntaje": 15},
    {"categoria": "Medio ambiente", "clave": "medio ambiente rural", "puntaje": 15},
    # Interventoría / apoyo técnico
    {"categoria": "Interventoría", "clave": "interventoría", "puntaje": 10},
    {"categoria": "Interventoría", "clave": "apoyo técnico", "puntaje": 15},
    {"categoria": "Interventoría", "clave": "supervisión técnica", "puntaje": 10},
]

# ---------------------------------------------------------------------------
# Entidades compradoras prioritarias y puntajes
# ---------------------------------------------------------------------------
PRIORITY_ENTITIES: list[dict] = [
    {"entidad": "alcaldía", "puntaje": 15},
    {"entidad": "gobernación", "puntaje": 15},
    {"entidad": "adr", "puntaje": 20},
    {"entidad": "agencia de desarrollo rural", "puntaje": 20},
    {"entidad": "sena", "puntaje": 20},
    {"entidad": "icbf", "puntaje": 15},
    {"entidad": "ministerio de agricultura", "puntaje": 20},
    {"entidad": "unidad solidaria", "puntaje": 15},
    {"entidad": "finagro", "puntaje": 15},
    {"entidad": "ica", "puntaje": 15},
    {"entidad": "aunap", "puntaje": 20},
    {"entidad": "universidad", "puntaje": 10},
    {"entidad": "corporación autónoma", "puntaje": 10},
    {"entidad": "upra", "puntaje": 15},
]

# ---------------------------------------------------------------------------
# Territorios prioritarios y puntajes
# ---------------------------------------------------------------------------
PRIORITY_TERRITORIES: list[dict] = [
    {"territorio": "bolívar", "puntaje": 20},
    {"territorio": "magdalena", "puntaje": 20},
    {"territorio": "cesar", "puntaje": 15},
    {"territorio": "sucre", "puntaje": 15},
    {"territorio": "córdoba", "puntaje": 15},
    {"territorio": "atlántico", "puntaje": 10},
    {"territorio": "la guajira", "puntaje": 10},
    {"territorio": "caribe", "puntaje": 10},
    {"territorio": "santa marta", "puntaje": 15},
    {"territorio": "talaigua nuevo", "puntaje": 25},
    {"territorio": "mompox", "puntaje": 20},
    {"territorio": "barranquilla", "puntaje": 10},
]

# ---------------------------------------------------------------------------
# Palabras de descarte y penalizaciones
# ---------------------------------------------------------------------------
DISCARD_KEYWORDS: list[dict] = [
    {"clave": "software especializado", "penalizacion": -20},
    {"clave": "infraestructura hospitalaria", "penalizacion": -30},
    {"clave": "armamento", "penalizacion": -100},
    {"clave": "vigilancia armada", "penalizacion": -50},
    {"clave": "combustible aeronáutico", "penalizacion": -50},
    {"clave": "equipos biomédicos", "penalizacion": -40},
    {"clave": "sistemas de información", "penalizacion": -15},
    {"clave": "infraestructura vial", "penalizacion": -20},
    {"clave": "obra pública", "penalizacion": -15},
    {"clave": "seguridad física", "penalizacion": -30},
]

# ---------------------------------------------------------------------------
# Umbrales de prioridad
# ---------------------------------------------------------------------------
THRESHOLD_ALTA = 70
THRESHOLD_MEDIA = 40
THRESHOLD_BAJA = 20

# Prioridades
PRIORIDAD_ALTA = "ALTA"
PRIORIDAD_MEDIA = "MEDIA"
PRIORIDAD_BAJA = "BAJA"
PRIORIDAD_DESCARTAR = "DESCARTAR"

# ---------------------------------------------------------------------------
# Puntaje de vigencia basado en días al cierre
# ---------------------------------------------------------------------------
VIGENCIA_RULES: list[dict] = [
    {"max_dias": -1, "puntaje": -50},   # vencido
    {"max_dias": 3,  "puntaje": 25},    # cierra pronto
    {"max_dias": 10, "puntaje": 20},
    {"max_dias": 30, "puntaje": 10},
    {"max_dias": 999, "puntaje": 0},    # muy lejano
]

# ---------------------------------------------------------------------------
# Estados activos en SECOP II
# ---------------------------------------------------------------------------
ACTIVE_STATES = {
    "publicado",
    "en presentación de ofertas",
    "evaluación de ofertas",
    "adjudicación",
    "en proceso",
    "convocado",
    "abierto",
}
