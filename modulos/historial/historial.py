import json
import os
import re
from datetime import datetime
from modulos.recordatorios.gestor import guardar_recordatorio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../modulos/historial
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(BASE_DIR))  # .../Watson

RUTA_HISTORIAL = os.path.join(RAIZ_PROYECTO, "data", "historial.json")

# ------------------ Funciones base ------------------

def cargar_historial():
    if not os.path.exists(RUTA_HISTORIAL):
        with open(RUTA_HISTORIAL, "w") as f:
            json.dump([], f)
    with open(RUTA_HISTORIAL, "r") as f:
        contenido = f.read().strip()
        if contenido == "":
            return []
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            print("⚠️ Historial dañado, reiniciando archivo.")
            with open(RUTA_HISTORIAL, "w") as f:
                json.dump([], f)
            return []

def guardar_evento(texto, etiqueta=None):
    historial = cargar_historial()
    evento = {
        "texto": texto,
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "etiqueta": etiqueta  # ejemplo: 'recordatorio', 'conversacion'
    }
    historial.append(evento)
    with open(RUTA_HISTORIAL, "w") as f:
        json.dump(historial, f, indent=4)

def listar_eventos():
    historial = cargar_historial()
    if not historial:
        print("No hay eventos en el historial.")
        return
    for i, evento in enumerate(historial):
        print(f"[{i}] ({evento.get('etiqueta', 'sin etiqueta')}) {evento['fecha_hora']}: {evento['texto']}")

def buscar_eventos(palabra_clave):
    historial = cargar_historial()
    resultados = [e for e in historial if palabra_clave.lower() in e["texto"].lower()]
    if not resultados:
        print(f"No se encontraron eventos con la palabra '{palabra_clave}'.")
        return
    for i, evento in enumerate(resultados):
        print(f"[{i}] ({evento.get('etiqueta', 'sin etiqueta')}) {evento['fecha_hora']}: {evento['texto']}")

def borrar_historial():
    with open(RUTA_HISTORIAL, "w") as f:
        json.dump([], f)
    print("Historial borrado.")

# ------------------ Inteligencia básica ------------------

def es_recordatorio(texto):
    patrones = [
        r"\brecuérdame\b",
        r"\brecordar\b",
        r"\bno olvidar\b",
        r"\bel \d{4}-\d{2}-\d{2} a las \d{1,2}:\d{2}\b",
        r"\ba las \d{1,2}(:\d{2})?\b",
    ]
    texto = texto.lower()
    return any(re.search(p, texto) for p in patrones)

def extraer_fecha_hora(texto):
    match = re.search(r"(\d{4}-\d{2}-\d{2})[^\d]*(\d{1,2}:\d{2})", texto)
    if match:
        return match.group(1), match.group(2)
    return None, None

def guardar_y_analizar(texto):
    guardar_evento(texto, etiqueta="usuario")

    if es_recordatorio(texto):
        fecha, hora = extraer_fecha_hora(texto)
        if fecha and hora:
            texto_base = re.sub(r"el \d{4}-\d{2}-\d{2} a las \d{1,2}:\d{2}", "", texto, flags=re.IGNORECASE)
            texto_base = re.sub(r"\brecuérdame\b|\brecordar\b|\bno olvidar\b", "", texto_base, flags=re.IGNORECASE).strip()

            fecha_hora = f"{fecha} {hora}"  # Concatenamos fecha y hora en un solo string

            guardar_recordatorio(texto_base, fecha_hora, repetir=None)  # Pasamos repetir=None explícito
            guardar_evento(f"Recordatorio creado: {texto_base} para el {fecha_hora}", etiqueta="recordatorio")
            print(f"✅ Recordatorio creado: '{texto_base}' para el {fecha_hora}")
            return True
        else:
            print("⚠️ Se detectó un recordatorio, pero no se pudo extraer la fecha/hora.")
    return False
