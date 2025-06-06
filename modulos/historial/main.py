import sys
import os

# Agregar la raíz del proyecto al path para que se puedan importar modulos correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modulos.historial.historial import (
    listar_eventos,
    buscar_eventos,
    borrar_historial,
    guardar_y_analizar
)
from modulos.recordatorios.gestor import listar_recordatorios

def main():
    while True:
        print("\n--- Menú Watson - Historial y Recordatorios ---")
        print("1. Escribir texto (con o sin recordatorio)")
        print("2. Ver historial completo")
        print("3. Buscar algo en historial")
        print("4. Ver todos los recordatorios")
        print("5. Borrar todo el historial")
        print("6. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            texto = input("Escribe tu texto: ")
            es_rec = guardar_y_analizar(texto)
            if es_rec:
                print("✅ Se detectó un posible recordatorio y fue creado.")
            else:
                print("📝 Texto guardado sin recordatorio.")

        elif opcion == "2":
            listar_eventos()

        elif opcion == "3":
            clave = input("Palabra clave para buscar: ")
            buscar_eventos(clave)

        elif opcion == "4":
            listar_recordatorios()

        elif opcion == "5":
            confirmar = input("¿Seguro que quieres borrar todo el historial? (s/n): ")
            if confirmar.lower() == "s":
                borrar_historial()

        elif opcion == "6":
            print("👋 Cerrando Watson...")
            break

        else:
            print("❌ Opción inválida, intenta de nuevo.")

if __name__ == "__main__":
    main()
