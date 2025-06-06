import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from datetime import datetime
import threading
import time
import sys
import os

# Agregamos ruta raíz para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modulos.recordatorios.gestor import (
    guardar_recordatorio,
    cargar_recordatorios,
    editar_recordatorio,
    borrar_recordatorio,
    verificar_recordatorios,
)
from modulos.historial.historial import (
    guardar_evento,
    listar_eventos,
    buscar_eventos,
    borrar_historial,
    guardar_y_analizar,
)

# Import para sonidos (Windows)
try:
    import winsound
except ImportError:
    winsound = None

class WatsonUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Watson - Gestor de Recordatorios e Historial")
        self.geometry("700x500")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()
        self.start_recordatorio_verifier()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Pestaña Recordatorios
        self.tab_recordatorios = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_recordatorios, text="Recordatorios")

        # Pestaña Historial
        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="Historial")

        self.create_recordatorios_tab()
        self.create_historial_tab()

    def create_recordatorios_tab(self):
        # Frame principal recordatorios
        frame_top = ttk.Frame(self.tab_recordatorios)
        frame_top.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_top, text="Texto:").grid(row=0, column=0, sticky='w')
        self.entrada_texto = ttk.Entry(frame_top, width=50)
        self.entrada_texto.grid(row=0, column=1, sticky='ew', padx=5)

        ttk.Label(frame_top, text="Fecha y hora (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky='w')
        self.entrada_fecha = ttk.Entry(frame_top, width=20)
        self.entrada_fecha.grid(row=1, column=1, sticky='w', padx=5)

        ttk.Label(frame_top, text="Repetir:").grid(row=2, column=0, sticky='w')
        self.repetir_var = tk.StringVar(value="ninguno")
        frame_radio = ttk.Frame(frame_top)
        frame_radio.grid(row=2, column=1, sticky='w')
        for opt in ["ninguno", "diario", "semanal", "mensual"]:
            ttk.Radiobutton(frame_radio, text=opt.capitalize(), variable=self.repetir_var, value=opt).pack(side='left')

        btn_agregar = ttk.Button(frame_top, text="Agregar recordatorio", command=self.agregar_recordatorio)
        btn_agregar.grid(row=3, column=0, columnspan=2, pady=8)

        # Listado recordatorios
        self.listado_rec = scrolledtext.ScrolledText(self.tab_recordatorios, width=80, height=15)
        self.listado_rec.pack(padx=10, pady=10, fill='both', expand=True)
        self.listado_rec.configure(state='disabled')

        # Botones editar y borrar
        frame_botones = ttk.Frame(self.tab_recordatorios)
        frame_botones.pack(pady=5)
        ttk.Button(frame_botones, text="Editar recordatorio", command=self.editar_recordatorio).pack(side='left', padx=10)
        ttk.Button(frame_botones, text="Borrar recordatorio", command=self.borrar_recordatorio).pack(side='left', padx=10)

        self.actualizar_listado_recordatorios()

    def create_historial_tab(self):
        frame_top = ttk.Frame(self.tab_historial)
        frame_top.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_top, text="Texto evento:").grid(row=0, column=0, sticky='w')
        self.entrada_historial = ttk.Entry(frame_top, width=50)
        self.entrada_historial.grid(row=0, column=1, sticky='ew', padx=5)

        ttk.Label(frame_top, text="Etiqueta (opcional):").grid(row=1, column=0, sticky='w')
        self.entrada_etiqueta = ttk.Entry(frame_top, width=20)
        self.entrada_etiqueta.grid(row=1, column=1, sticky='w', padx=5)

        btn_agregar_hist = ttk.Button(frame_top, text="Agregar evento", command=self.agregar_evento_historial)
        btn_agregar_hist.grid(row=2, column=0, columnspan=2, pady=8)

        # Buscador historial
        frame_buscar = ttk.Frame(self.tab_historial)
        frame_buscar.pack(padx=10, pady=5, fill='x')

        ttk.Label(frame_buscar, text="Buscar en historial:").pack(side='left')
        self.busqueda_var = tk.StringVar()
        self.entrada_buscar = ttk.Entry(frame_buscar, textvariable=self.busqueda_var, width=30)
        self.entrada_buscar.pack(side='left', padx=5)
        ttk.Button(frame_buscar, text="Buscar", command=self.buscar_historial).pack(side='left', padx=5)
        ttk.Button(frame_buscar, text="Mostrar todo", command=self.actualizar_listado_historial).pack(side='left', padx=5)
        ttk.Button(frame_buscar, text="Borrar todo historial", command=self.borrar_historial_confirmar).pack(side='right')

        # Listado historial
        self.listado_hist = scrolledtext.ScrolledText(self.tab_historial, width=80, height=20)
        self.listado_hist.pack(padx=10, pady=10, fill='both', expand=True)
        self.listado_hist.configure(state='disabled')

        self.actualizar_listado_historial()

    def validar_fecha_hora(self, fecha_hora):
        try:
            datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            return False

    def agregar_recordatorio(self):
        texto = self.entrada_texto.get().strip()
        fecha_hora = self.entrada_fecha.get().strip()
        repetir = self.repetir_var.get()

        if not texto:
            messagebox.showerror("Error", "El texto del recordatorio no puede estar vacío.")
            return
        if not self.validar_fecha_hora(fecha_hora):
            messagebox.showerror("Error", "Fecha y hora inválida. Use formato YYYY-MM-DD HH:MM")
            return
        repetir_val = repetir if repetir in ("diario", "semanal", "mensual") else None
        try:
            guardar_recordatorio(texto, fecha_hora, repetir_val)
            messagebox.showinfo("Éxito", "Recordatorio guardado correctamente.")
            self.entrada_texto.delete(0, tk.END)
            self.entrada_fecha.delete(0, tk.END)
            self.repetir_var.set("ninguno")
            self.actualizar_listado_recordatorios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el recordatorio:\n{e}")

    def actualizar_listado_recordatorios(self):
        recordatorios = cargar_recordatorios()
        self.listado_rec.configure(state='normal')
        self.listado_rec.delete(1.0, tk.END)
        if not recordatorios:
            self.listado_rec.insert(tk.END, "No hay recordatorios guardados.\n")
        else:
            for i, rec in enumerate(recordatorios):
                rep = rec.get('repetir', 'No')
                self.listado_rec.insert(tk.END, f"[{i}] {rec['texto']} - {rec['fecha_hora']} - Repetir: {rep}\n")
        self.listado_rec.configure(state='disabled')

    def seleccionar_indice_recordatorio(self):
        try:
            texto = self.listado_rec.get("sel.first", "sel.last")
        except tk.TclError:
            messagebox.showwarning("Aviso", "Selecciona el texto del recordatorio en la lista para editar o borrar.")
            return None
        # El texto tiene formato: "[i] texto - fecha - repetir", extraemos el índice
        try:
            indice = int(texto.split(']')[0].strip('['))
            return indice
        except:
            messagebox.showerror("Error", "No se pudo obtener el índice del recordatorio seleccionado.")
            return None

    def editar_recordatorio(self):
        indice = self.seleccionar_indice_recordatorio()
        if indice is None:
            return

        recordatorios = cargar_recordatorios()
        if indice < 0 or indice >= len(recordatorios):
            messagebox.showerror("Error", "Índice fuera de rango.")
            return

        rec = recordatorios[indice]

        dialog = EditRecordatorioDialog(self, rec)
        self.wait_window(dialog)
        if dialog.result:
            texto, fecha_hora, repetir = dialog.result
            repetir_val = repetir if repetir in ("diario", "semanal", "mensual") else None
            try:
                editar_recordatorio(indice, texto, fecha_hora, repetir_val)
                messagebox.showinfo("Éxito", "Recordatorio editado correctamente.")
                self.actualizar_listado_recordatorios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo editar el recordatorio:\n{e}")

    def borrar_recordatorio(self):
        indice = self.seleccionar_indice_recordatorio()
        if indice is None:
            return
        if messagebox.askyesno("Confirmar", f"¿Seguro que quieres borrar el recordatorio [{indice}]?"):
            try:
                borrar_recordatorio(indice)
                messagebox.showinfo("Éxito", "Recordatorio borrado correctamente.")
                self.actualizar_listado_recordatorios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar el recordatorio:\n{e}")

    def agregar_evento_historial(self):
        texto = self.entrada_historial.get().strip()
        etiqueta = self.entrada_etiqueta.get().strip()
        etiqueta = etiqueta if etiqueta else None

        if not texto:
            messagebox.showerror("Error", "El texto del evento no puede estar vacío.")
            return

        try:
            es_recordatorio = guardar_y_analizar(texto)
            if not es_recordatorio:
                guardar_evento(texto, etiqueta)
                messagebox.showinfo("Éxito", "Evento guardado en historial.")
            else:
                messagebox.showinfo("Éxito", "Recordatorio detectado y guardado.")
            self.entrada_historial.delete(0, tk.END)
            self.entrada_etiqueta.delete(0, tk.END)
            self.actualizar_listado_historial()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el evento:\n{e}")

    def actualizar_listado_historial(self, eventos=None):
        if eventos is None:
            eventos = listar_eventos()
        self.listado_hist.configure(state='normal')
        self.listado_hist.delete(1.0, tk.END)
        if not eventos:
            self.listado_hist.insert(tk.END, "No hay eventos en el historial.\n")
        else:
            for i, ev in enumerate(eventos):
                etiqueta = ev.get('etiqueta', 'Sin etiqueta')
                texto = ev.get('texto', '')
                fecha = ev.get('fecha', '')
                self.listado_hist.insert(tk.END, f"[{i}] {fecha} - {etiqueta} - {texto}\n")
        self.listado_hist.configure(state='disabled')

    def buscar_historial(self):
        palabra = self.busqueda_var.get().strip()
        if not palabra:
            messagebox.showwarning("Aviso", "Ingresa una palabra clave para buscar.")
            return
        resultados = buscar_eventos(palabra)
        self.actualizar_listado_historial(resultados)

    def borrar_historial_confirmar(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar TODO el historial?"):
            try:
                borrar_historial()
                messagebox.showinfo("Éxito", "Historial borrado correctamente.")
                self.actualizar_listado_historial()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar el historial:\n{e}")

    def start_recordatorio_verifier(self):
        def verificar_loop():
            while True:
                try:
                    próximos = verificar_recordatorios()
                    if próximos:
                        for rec in próximos:
                            self.alerta_recordatorio(rec)
                    time.sleep(30)  # Verifica cada 30 segundos
                except Exception:
                    pass  # para que no cierre el hilo si hay error

        self.verifier_thread = threading.Thread(target=verificar_loop, daemon=True)
        self.verifier_thread.start()

    def alerta_recordatorio(self, rec):
        def alerta_popup():
            if winsound:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            messagebox.showinfo("Recordatorio", f"⏰ ¡Recordatorio!\n\n{rec['texto']}\nHora: {rec['fecha_hora']}")
        # Lo ejecutamos en main thread porque messagebox no es thread-safe
        self.after(0, alerta_popup)

    def on_close(self):
        # Aquí podrías guardar estados o pedir confirmación si quieres
        self.destroy()

class EditRecordatorioDialog(tk.Toplevel):
    def __init__(self, parent, recordatorio):
        super().__init__(parent)
        self.title("Editar Recordatorio")
        self.resizable(False, False)
        self.result = None

        ttk.Label(self, text="Texto:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.entrada_texto = ttk.Entry(self, width=50)
        self.entrada_texto.grid(row=0, column=1, padx=10, pady=5)
        self.entrada_texto.insert(0, recordatorio['texto'])

        ttk.Label(self, text="Fecha y hora (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.entrada_fecha = ttk.Entry(self, width=20)
        self.entrada_fecha.grid(row=1, column=1, padx=10, pady=5)
        self.entrada_fecha.insert(0, recordatorio['fecha_hora'])

        ttk.Label(self, text="Repetir:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.repetir_var = tk.StringVar(value=recordatorio.get('repetir', 'ninguno'))
        frame_radio = ttk.Frame(self)
        frame_radio.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        for opt in ["ninguno", "diario", "semanal", "mensual"]:
            ttk.Radiobutton(frame_radio, text=opt.capitalize(), variable=self.repetir_var, value=opt).pack(side='left')

        btn_guardar = ttk.Button(self, text="Guardar cambios", command=self.guardar)
        btn_guardar.grid(row=3, column=0, columnspan=2, pady=10)

    def guardar(self):
        texto = self.entrada_texto.get().strip()
        fecha_hora = self.entrada_fecha.get().strip()
        repetir = self.repetir_var.get()
        if not texto:
            messagebox.showerror("Error", "El texto no puede estar vacío.")
            return
        try:
            datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Fecha y hora inválida. Usa formato YYYY-MM-DD HH:MM")
            return
        self.result = (texto, fecha_hora, repetir)
        self.destroy()


if __name__ == "__main__":
    app = WatsonUI()
    app.mainloop()
