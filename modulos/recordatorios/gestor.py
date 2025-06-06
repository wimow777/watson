import json
import os
from datetime import datetime, timedelta
import calendar
from plyer import notification
from playsound import playsound

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../modulos/recordatorios
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(BASE_DIR))  # .../Watson

RUTA_DB = os.path.join(RAIZ_PROYECTO, "data", "recordatorios.json")
SONIDO_PATH = os.path.join(RAIZ_PROYECTO, "sonidos", "alerta.mp3")  # ajusta si cambia la ruta

def cargar_recordatorios():
    if not os.path.exists(RUTA_DB):
        with open(RUTA_DB, 'w') as f:
            json.dump([], f)

    with open(RUTA_DB, 'r') as f:
        contenido = f.read().strip()
        if contenido == "":
            return []
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            print("⚠️ Error: recordatorios.json dañado. Reiniciando archivo.")
            with open(RUTA_DB, 'w') as f:
                json.dump([], f)
            return []

def validar_recordatorio(texto, fecha_hora, repetir=None):
    if not texto.strip():
        raise ValueError("El texto del recordatorio no puede estar vacío.")
    
    # Normalizar repetir: si llega vacío o falso, poner None
    if not repetir:
        repetir = None
    
    # Si solo recibimos la fecha sin hora, agregamos "06:00" por defecto
    if len(fecha_hora) == 10:  # YYYY-MM-DD
        fecha_hora += " 06:00"

    try:
        fecha = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Formato de fecha y hora incorrecto. Use 'YYYY-MM-DD HH:MM'.")

    if fecha < datetime.now():
        raise ValueError("La fecha y hora no pueden ser anteriores a la fecha actual.")
    
    if repetir not in (None, "diario", "semanal", "mensual"):
        raise ValueError("Tipo de repetición inválido. Use None, 'diario', 'semanal' o 'mensual'.")


def sumar_mes(fecha):
    año = fecha.year
    mes = fecha.month + 1
    if mes > 12:
        mes = 1
        año += 1
    
    dia = min(fecha.day, calendar.monthrange(año, mes)[1])
    return fecha.replace(year=año, month=mes, day=dia)

def guardar_recordatorio(texto, fecha_hora, repetir=None):
    validar_recordatorio(texto, fecha_hora, repetir)

    recordatorios = cargar_recordatorios()
    recordatorios.append({
        "texto": texto,
        "fecha_hora": fecha_hora,
        "repetir": repetir  # Puede ser "diario", "semanal", "mensual" o None
    })
    with open(RUTA_DB, 'w') as f:
        json.dump(recordatorios, f, indent=4)

def editar_recordatorio(indice, texto=None, fecha_hora=None, repetir=None):
    recordatorios = cargar_recordatorios()
    if indice < 0 or indice >= len(recordatorios):
        raise IndexError("Índice de recordatorio inválido.")

    rec = recordatorios[indice]

    nuevo_texto = texto if texto is not None else rec["texto"]
    nueva_fecha_hora = fecha_hora if fecha_hora is not None else rec["fecha_hora"]
    nuevo_repetir = repetir if repetir is not None else rec.get("repetir")

    validar_recordatorio(nuevo_texto, nueva_fecha_hora, nuevo_repetir)

    rec["texto"] = nuevo_texto
    rec["fecha_hora"] = nueva_fecha_hora
    rec["repetir"] = nuevo_repetir

    with open(RUTA_DB, 'w') as f:
        json.dump(recordatorios, f, indent=4)

def borrar_recordatorio(indice):
    recordatorios = cargar_recordatorios()
    if indice < 0 or indice >= len(recordatorios):
        raise IndexError("Índice de recordatorio inválido.")

    recordatorios.pop(indice)
    with open(RUTA_DB, 'w') as f:
        json.dump(recordatorios, f, indent=4)

def listar_recordatorios():
    recordatorios = cargar_recordatorios()
    if not recordatorios:
        print("No hay recordatorios guardados.")
        return

    for i, rec in enumerate(recordatorios):
        print(f"[{i}] Texto: {rec['texto']}")
        print(f"    Fecha y hora: {rec['fecha_hora']}")
        print(f"    Repetir: {rec.get('repetir', 'No')}")
        print("-" * 30)

def verificar_recordatorios():
    recordatorios = cargar_recordatorios()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    nuevos = []
    
   
    for rec in recordatorios:
        if rec["fecha_hora"] == ahora:
            print(f"🔔 Recordatorio: {rec['texto']}")

            # Notificación pop-up
            notification.notify(
                title="Recordatorio Watson",
                message=rec['texto'],
                timeout=10
            )

            # Sonido
            try:
                playsound(SONIDO_PATH)
            except Exception as e:
                print(f"Error al reproducir sonido: {e}")

            if rec.get("repetir") == "diario":
                proxima_fecha = datetime.strptime(rec["fecha_hora"], "%Y-%m-%d %H:%M") + timedelta(days=1)
                rec_actualizado = rec.copy()
                rec_actualizado["fecha_hora"] = proxima_fecha.strftime("%Y-%m-%d %H:%M")
                nuevos.append(rec_actualizado)

            elif rec.get("repetir") == "semanal":
                proxima_fecha = datetime.strptime(rec["fecha_hora"], "%Y-%m-%d %H:%M") + timedelta(weeks=1)
                rec_actualizado = rec.copy()
                rec_actualizado["fecha_hora"] = proxima_fecha.strftime("%Y-%m-%d %H:%M")
                nuevos.append(rec_actualizado)

            elif rec.get("repetir") == "mensual":
                fecha_actual = datetime.strptime(rec["fecha_hora"], "%Y-%m-%d %H:%M")
                proxima_fecha = sumar_mes(fecha_actual)
                rec_actualizado = rec.copy()
                rec_actualizado["fecha_hora"] = proxima_fecha.strftime("%Y-%m-%d %H:%M")
                nuevos.append(rec_actualizado)

            else:
                # No repetitivo, no se guarda más (se elimina)
                pass
        else:
            nuevos.append(rec)

    with open(RUTA_DB, 'w') as f:
        json.dump(nuevos, f, indent=4)
     