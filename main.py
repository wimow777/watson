from modulos.recordatorios import (
    guardar_recordatorio,
    listar_recordatorios,
    editar_recordatorio,
    borrar_recordatorio
)

from modulos.historial import (
    guardar_evento,
    listar_eventos,
    buscar_eventos,
    borrar_historial,
    guardar_y_analizar  # Importamos esta para análisis inteligente
)

def validar_fecha_hora(fecha_hora):
    from datetime import datetime
    try:
        datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def main():
    print("==== Gestor Watson: Recordatorios e Historial ====")

    while True:
        print("\nOpciones:")
        print("1 - Agregar recordatorio")
        print("2 - Listar recordatorios")
        print("3 - Editar recordatorio")
        print("4 - Borrar recordatorio")
        print("5 - Agregar evento al historial")
        print("6 - Listar historial")
        print("7 - Buscar en historial")
        print("8 - Borrar historial")
        print("9 - Salir")

        opcion = input("Selecciona opción: ").strip()

        if opcion == "1":
            texto = input("Texto del recordatorio: ").strip()
            fecha_hora = input("Fecha y hora (YYYY-MM-DD HH:MM): ").strip()
            if not validar_fecha_hora(fecha_hora):
                print("❌ Fecha y hora inválida. Usa formato YYYY-MM-DD HH:MM")
                continue
            repetir = input("Repetir (ninguno, diario, semanal, mensual): ").lower().strip()
            repetir_val = repetir if repetir in ("diario", "semanal", "mensual") else None
            try:
                guardar_recordatorio(texto, fecha_hora, repetir_val)
                print("✅ Recordatorio guardado correctamente.")
            except Exception as e:
                print(f"Error al guardar recordatorio: {e}")

        elif opcion == "2":
            listar_recordatorios()

        elif opcion == "3":
            try:
                indice = int(input("Índice del recordatorio a editar: "))
                print("Deja vacío para no cambiar un campo.")
                texto = input("Nuevo texto: ").strip()
                texto = texto if texto else None
                fecha_hora = input("Nueva fecha y hora (YYYY-MM-DD HH:MM): ").strip()
                if fecha_hora and not validar_fecha_hora(fecha_hora):
                    print("❌ Fecha y hora inválida. Usa formato YYYY-MM-DD HH:MM")
                    continue
                fecha_hora = fecha_hora if fecha_hora else None
                repetir = input("Repetir (ninguno, diario, semanal, mensual): ").lower().strip()
                repetir = repetir if repetir in ("diario", "semanal", "mensual") else None
                editar_recordatorio(indice, texto, fecha_hora, repetir)
                print("✅ Recordatorio editado.")
            except Exception as e:
                print(f"Error al editar recordatorio: {e}")

        elif opcion == "4":
            try:
                indice = int(input("Índice del recordatorio a borrar: "))
                borrar_recordatorio(indice)
                print("✅ Recordatorio borrado.")
            except Exception as e:
                print(f"Error al borrar recordatorio: {e}")

        elif opcion == "5":
            texto = input("Texto del evento para historial: ").strip()
            etiqueta = input("Etiqueta (opcional, ej: 'recordatorio', 'conversacion'): ").strip()
            etiqueta = etiqueta if etiqueta else None

            # Aquí usamos la función que analiza y guarda recordatorio si detecta
            es_recordatorio = guardar_y_analizar(texto)
            if not es_recordatorio:
                # Si no detectó recordatorio, guarda solo evento normal
                guardar_evento(texto, etiqueta)
                print("✅ Evento guardado en historial.")
            else:
                print("✅ Recordatorio detectado y guardado.")

        elif opcion == "6":
            listar_eventos()

        elif opcion == "7":
            palabra = input("Palabra clave para buscar en historial: ").strip()
            buscar_eventos(palabra)

        elif opcion == "8":
            confirmar = input("¿Seguro que quieres borrar TODO el historial? (s/n): ").lower().strip()
            if confirmar == "s":
                borrar_historial()
                print("✅ Historial borrado.")
            else:
                print("Operación cancelada.")

        elif opcion == "9":
            print("Saliendo...")
            break

        else:
            print("Opción inválida, intenta de nuevo.")

if __name__ == "__main__":
    main()
