import threading
import time
from gestor import (
    guardar_recordatorio,
    verificar_recordatorios,
    listar_recordatorios,
    editar_recordatorio,
    borrar_recordatorio,
    cargar_recordatorios,
)

def verificador_periodico(intervalo_segundos):
    while True:
        verificar_recordatorios()
        time.sleep(intervalo_segundos)

def main():
    print("=== Watson - Módulo de Recordatorios ===")

    hilo_verificador = threading.Thread(target=verificador_periodico, args=(30,), daemon=True)
    hilo_verificador.start()

    while True:
        print("\nOpciones:")
        print("1. Agregar recordatorio")
        print("2. Ver recordatorios")
        print("3. Editar recordatorio")
        print("4. Borrar recordatorio")
        print("5. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            texto = input("Texto del recordatorio: ")
            fecha_hora = input("Fecha y hora (YYYY-MM-DD HH:MM): ")
            repetir = input("Repetir (diario, semanal, mensual, nada): ").lower()
            repetir = repetir if repetir in ["diario", "semanal", "mensual"] else None

            try:
                guardar_recordatorio(texto, fecha_hora, repetir)
                print("Recordatorio guardado con éxito.")
            except ValueError as e:
                print(f"Error: {e}")

        elif opcion == "2":
            listar_recordatorios()

        elif opcion == "3":
            listar_recordatorios()
            id_edit = input("Ingresa el ID del recordatorio a editar: ")
            if not id_edit.isdigit():
                print("ID inválido.")
                continue
            id_edit = int(id_edit)
            recordatorios = cargar_recordatorios()
            if id_edit < 0 or id_edit >= len(recordatorios):
                print("ID fuera de rango.")
                continue

            texto = input(f"Nuevo texto (dejar vacío para no cambiar) [{recordatorios[id_edit]['texto']}]: ")
            fecha_hora = input(f"Nueva fecha y hora (YYYY-MM-DD HH:MM) (dejar vacío para no cambiar) [{recordatorios[id_edit]['fecha_hora']}]: ")
            repetir = input(f"Repetir (diario, semanal, mensual, nada) (dejar vacío para no cambiar) [{recordatorios[id_edit].get('repetir', 'nada')}]: ").lower()
            repetir = repetir if repetir in ["diario", "semanal", "mensual"] else recordatorios[id_edit].get('repetir')

            # Si se dejó vacío, pasamos None para que no cambie
            texto = texto if texto.strip() else None
            fecha_hora = fecha_hora if fecha_hora.strip() else None

            try:
                editar_recordatorio(id_edit, texto, fecha_hora, repetir)
                print("Recordatorio editado con éxito.")
            except ValueError as e:
                print(f"Error al editar recordatorio: {e}")

        elif opcion == "4":
            listar_recordatorios()
            id_borrar = input("Ingresa el ID del recordatorio a borrar: ")
            if not id_borrar.isdigit():
                print("ID inválido.")
                continue
            id_borrar = int(id_borrar)
            try:
                borrar_recordatorio(id_borrar)
                print("Recordatorio eliminado con éxito.")
            except IndexError as e:
                print(f"Error al borrar recordatorio: {e}")

        elif opcion == "5":
            print("Saliendo... ¡Nos vemos!")
            break

        else:
            print("Opción no válida. Intenta otra vez.")

if __name__ == "__main__":
    main()
