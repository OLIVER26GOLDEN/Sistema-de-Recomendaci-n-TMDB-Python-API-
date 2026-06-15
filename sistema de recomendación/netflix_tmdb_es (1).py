import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import webbrowser  # Para abrir el navegador al hacer clic en una tarjeta

# ──────────────────────────────────────────────
#  CONFIGURACIÓN GENERAL
# ──────────────────────────────────────────────
CLAVE_API     = "f888ef6c9c494a1da35c236b5ec5508b"
URL_BASE      = "https://api.themoviedb.org/3"
URL_IMAGENES  = "https://image.tmdb.org/t/p/w185"  # Tamaño de póster: 185px de ancho

# Paleta de colores de la interfaz
COLOR_FONDO      = "#141414"
COLOR_TARJETA    = "#1f1f1f"
COLOR_ROJO       = "#e50914"
COLOR_BLANCO     = "#ffffff"
COLOR_GRIS       = "#808080"
COLOR_OSCURO     = "#2a2a2a"


# ──────────────────────────────────────────────
#  MOTOR DE CONSULTAS A TMDB
# ──────────────────────────────────────────────
class MotorTMDB:
    """Clase encargada de todas las comunicaciones con la API de TMDB."""

    def __init__(self):
        # Sesión reutilizable para mayor eficiencia en las peticiones HTTP
        self.sesion = requests.Session()

    def _obtener(self, endpoint, parametros={}):
        """Realiza una petición GET a la API y devuelve el JSON de respuesta."""
        parametros["api_key"] = CLAVE_API
        parametros["language"] = "es-ES"  # Respuestas en español
        respuesta = self.sesion.get(f"{URL_BASE}{endpoint}", params=parametros, timeout=10)
        respuesta.raise_for_status()
        return respuesta.json()

    def buscar(self, consulta):
        """Busca películas y series según el texto introducido por el usuario."""
        datos = self._obtener("/search/multi", {"query": consulta})
        # Filtrar solo películas (movie) y series (tv), descartar personas u otros
        return [r for r in datos.get("results", [])
                if r.get("media_type") in ("movie", "tv")][:5]

    def obtener_recomendaciones(self, id_media, tipo_media):
        """Devuelve una lista de recomendaciones para una película o serie dada."""
        datos = self._obtener(f"/{tipo_media}/{id_media}/recommendations")
        recomendaciones = []
        for r in datos.get("results", [])[:12]:
            recomendaciones.append({
                "titulo":     r.get("title") or r.get("name", "Sin título"),
                "tipo":       "Película" if tipo_media == "movie" else "Serie",
                "tipo_raw":   tipo_media,   # "movie" o "tv" para construir la URL
                "id_tmdb":    r.get("id"),  # ID necesario para la URL de TMDB
                "puntuacion": r.get("vote_average", 0),
                "sinopsis":   (r.get("overview") or "Sinopsis no disponible.")[:160],
                "poster":     r.get("poster_path", ""),
            })
        return recomendaciones

    def descargar_poster(self, ruta):
        """Descarga un póster desde TMDB y lo devuelve como imagen de tkinter."""
        if not ruta:
            return None
        try:
            respuesta = self.sesion.get(URL_IMAGENES + ruta, timeout=8)
            imagen = Image.open(BytesIO(respuesta.content)).resize((111, 167))
            return ImageTk.PhotoImage(imagen)
        except Exception:
            return None  # Si falla la descarga, devolvemos nada (se mostrará placeholder)

    def obtener_detalles(self, id_media, tipo_media):
        """Obtiene los detalles completos de una película o serie, incluyendo créditos."""
        datos = self._obtener(
            f"/{tipo_media}/{id_media}",
            {"append_to_response": "credits"}
        )
        generos = [g["name"] for g in datos.get("genres", [])]
        return {
            "titulo":     datos.get("title") or datos.get("name", ""),
            "generos":    generos,
            "puntuacion": datos.get("vote_average", 0),
            "sinopsis":   datos.get("overview", ""),
            "poster":     datos.get("poster_path", ""),
        }


# ──────────────────────────────────────────────
#  TARJETA VISUAL DE CADA RECOMENDACIÓN
# ──────────────────────────────────────────────
class TarjetaPelicula(tk.Frame):
    """Widget que muestra el póster, título, puntuación y tipo de una recomendación."""

    ANCHO  = 130  # Ancho fijo de cada tarjeta en píxeles
    ALTO   = 250  # Alto fijo de cada tarjeta en píxeles

    def __init__(self, padre, recomendacion, motor, **kwargs):
        super().__init__(padre, bg=COLOR_TARJETA,
                         width=self.ANCHO, height=self.ALTO, **kwargs)
        self.pack_propagate(False)  # Evita que el frame se redimensione con su contenido
        self._referencia_imagen = None  # Guardamos referencia para evitar que el GC borre la imagen

        # ── Póster (placeholder oscuro hasta que cargue la imagen) ──
        self.etiqueta_imagen = tk.Label(self, bg=COLOR_OSCURO,
                                        width=self.ANCHO, height=167,
                                        cursor="hand2")
        self.etiqueta_imagen.pack()

        # ── Título (truncado si es muy largo) ──
        titulo = recomendacion["titulo"]
        if len(titulo) > 22:
            titulo = titulo[:20] + "…"
        tk.Label(self, text=titulo, font=("Arial", 9, "bold"),
                 fg=COLOR_BLANCO, bg=COLOR_TARJETA,
                 wraplength=self.ANCHO - 8,
                 justify="center").pack(pady=(4, 0))

        # ── Puntuación con color según valor ──
        puntuacion = recomendacion["puntuacion"]
        if puntuacion >= 7:
            color_puntuacion = "#f5c518"   # Amarillo: buena puntuación
        elif puntuacion >= 5:
            color_puntuacion = "#e07b39"   # Naranja: puntuación media
        else:
            color_puntuacion = COLOR_GRIS  # Gris: puntuación baja o sin datos

        tk.Label(self, text=f"⭐ {puntuacion:.1f}",
                 font=("Arial", 9),
                 fg=color_puntuacion, bg=COLOR_TARJETA).pack()

        # ── Tipo: Película o Serie ──
        tk.Label(self, text=recomendacion["tipo"],
                 font=("Arial", 8),
                 fg=COLOR_GRIS, bg=COLOR_TARJETA).pack()

        # ── Tooltip con sinopsis al pasar el cursor ──
        self._tooltip = None
        self._sinopsis = recomendacion["sinopsis"]
        self.etiqueta_imagen.bind("<Enter>", self._mostrar_tooltip)
        self.etiqueta_imagen.bind("<Leave>", self._ocultar_tooltip)
        self.bind("<Enter>", self._mostrar_tooltip)
        self.bind("<Leave>", self._ocultar_tooltip)

        # ── Abrir cliver.mom al hacer clic en el póster o la tarjeta ──
        self._titulo_original = recomendacion["titulo"]
        self.etiqueta_imagen.bind("<Button-1>", self._abrir_en_cliver)
        self.bind("<Button-1>", self._abrir_en_cliver)

        # ── Cargar imagen en segundo plano para no bloquear la interfaz ──
        threading.Thread(
            target=self._cargar_imagen,
            args=(motor, recomendacion["poster"]),
            daemon=True
        ).start()

    def _abrir_en_cliver(self, evento=None):
        """Abre cliver.mom en el navegador buscando el título de la película o serie."""
        import urllib.parse
        consulta = urllib.parse.quote(self._titulo_original)
        url = f"https://cliver.mom/index.php?do=search&subaction=search&story={consulta}"
        webbrowser.open(url)

    def _cargar_imagen(self, motor, ruta):
        """Descarga el póster en un hilo secundario y lo muestra al terminar."""
        foto = motor.descargar_poster(ruta)
        if foto:
            self._referencia_imagen = foto  # Mantener referencia para evitar que Python la elimine
            self.etiqueta_imagen.after(
                0,
                lambda: self.etiqueta_imagen.configure(
                    image=self._referencia_imagen, width=111, height=167
                )
            )

    def _mostrar_tooltip(self, evento=None):
        """Muestra una ventana emergente con la sinopsis al pasar el cursor."""
        if self._tooltip or not self._sinopsis:
            return
        x = self.winfo_rootx() + 10
        y = self.winfo_rooty() + 170
        self._tooltip = ventana = tk.Toplevel(self)
        ventana.wm_overrideredirect(True)  # Sin borde ni barra de título
        ventana.wm_geometry(f"+{x}+{y}")
        texto_tooltip = self._sinopsis + "\n\n🖱️ Clic para ver en cliver.mom"
        tk.Label(
            ventana, text=texto_tooltip,
            font=("Arial", 9), bg="#222", fg=COLOR_BLANCO,
            wraplength=220, justify="left", padx=8, pady=6,
            relief="flat"
        ).pack()

    def _ocultar_tooltip(self, evento=None):
        """Cierra el tooltip al retirar el cursor."""
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None


# ──────────────────────────────────────────────
#  VENTANA PRINCIPAL DE LA APLICACIÓN
# ──────────────────────────────────────────────
class Aplicacion:
    """Clase principal que construye y gestiona la interfaz gráfica completa."""

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Recomendador de Películas y Series · TMDB")
        self.ventana.geometry("980x680")
        self.ventana.configure(bg=COLOR_FONDO)

        self.motor           = MotorTMDB()
        self.resultados_busqueda = []
        self._tarjetas       = []

        self._construir_interfaz()

    def _construir_interfaz(self):
        """Construye todos los elementos visuales de la aplicación."""

        # ── Encabezado ──
        encabezado = tk.Frame(self.ventana, bg=COLOR_FONDO)
        encabezado.pack(fill="x", padx=24, pady=(18, 4))
        tk.Label(encabezado, text="TMDB",
                 font=("Arial", 24, "bold"),
                 fg=COLOR_ROJO, bg=COLOR_FONDO).pack(side="left")
        tk.Label(encabezado, text="  Recomendador de Películas y Series",
                 font=("Arial", 15), fg=COLOR_BLANCO, bg=COLOR_FONDO).pack(side="left", pady=4)

        # ── Barra de búsqueda ──
        marco_busqueda = tk.Frame(self.ventana, bg=COLOR_FONDO)
        marco_busqueda.pack(fill="x", padx=24, pady=4)
        tk.Label(marco_busqueda,
                 text="Escribe el nombre de una película o serie que te haya gustado:",
                 font=("Arial", 11), fg=COLOR_GRIS, bg=COLOR_FONDO).pack(anchor="w")

        fila_entrada = tk.Frame(marco_busqueda, bg=COLOR_FONDO)
        fila_entrada.pack(fill="x", pady=(4, 0))

        self.campo_busqueda = tk.Entry(
            fila_entrada, font=("Arial", 13),
            bg=COLOR_TARJETA, fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO, relief="flat", bd=8
        )
        self.campo_busqueda.pack(side="left", fill="x", expand=True, ipady=7)
        self.campo_busqueda.bind("<Return>", lambda e: self._buscar())  # Buscar al pulsar Enter

        tk.Button(
            fila_entrada, text="Buscar",
            font=("Arial", 12, "bold"),
            bg=COLOR_ROJO, fg=COLOR_BLANCO,
            relief="flat", padx=20, pady=7,
            cursor="hand2", activebackground="#b20710",
            command=self._buscar
        ).pack(side="left", padx=(8, 0))

        # ── Barra de estado ──
        self.texto_estado = tk.StringVar(
            value="Escribe el nombre de una película o serie y pulsa Buscar"
        )
        tk.Label(
            self.ventana, textvariable=self.texto_estado,
            font=("Arial", 10), fg=COLOR_GRIS, bg=COLOR_FONDO
        ).pack(anchor="w", padx=24, pady=2)

        # ── Panel principal: lista izquierda + tarjetas derecha ──
        panel_principal = tk.Frame(self.ventana, bg=COLOR_FONDO)
        panel_principal.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        # Columna izquierda: lista de resultados de búsqueda
        columna_izquierda = tk.Frame(panel_principal, bg=COLOR_FONDO, width=230)
        columna_izquierda.pack(side="left", fill="y", padx=(0, 14))
        columna_izquierda.pack_propagate(False)

        tk.Label(columna_izquierda, text="Resultados de búsqueda",
                 font=("Arial", 10, "bold"),
                 fg=COLOR_BLANCO, bg=COLOR_FONDO).pack(anchor="w")

        self.lista_resultados = tk.Listbox(
            columna_izquierda, font=("Arial", 11),
            bg=COLOR_TARJETA, fg=COLOR_BLANCO,
            selectbackground=COLOR_ROJO, selectforeground=COLOR_BLANCO,
            relief="flat", bd=0, activestyle="none"
        )
        self.lista_resultados.pack(fill="both", expand=True, pady=(4, 0))
        self.lista_resultados.bind("<<ListboxSelect>>", self._al_seleccionar)

        # Columna derecha: tarjetas con pósters
        columna_derecha = tk.Frame(panel_principal, bg=COLOR_FONDO)
        columna_derecha.pack(side="left", fill="both", expand=True)

        tk.Label(columna_derecha, text="Recomendaciones",
                 font=("Arial", 10, "bold"),
                 fg=COLOR_BLANCO, bg=COLOR_FONDO).pack(anchor="w")

        # Canvas con scroll horizontal para mostrar todas las tarjetas
        marco_canvas = tk.Frame(columna_derecha, bg=COLOR_FONDO)
        marco_canvas.pack(fill="both", expand=True, pady=(4, 0))

        self.canvas = tk.Canvas(marco_canvas, bg=COLOR_FONDO, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)

        barra_scroll = ttk.Scrollbar(marco_canvas, orient="horizontal",
                                     command=self.canvas.xview)
        barra_scroll.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=barra_scroll.set)

        # Frame interno que contiene las tarjetas
        self.marco_tarjetas = tk.Frame(self.canvas, bg=COLOR_FONDO)
        self.canvas.create_window((0, 0), window=self.marco_tarjetas, anchor="nw")
        self.marco_tarjetas.bind("<Configure>", self._actualizar_scroll)

        # ── Área de sinopsis de la selección actual ──
        self.area_sinopsis = tk.Text(
            self.ventana, font=("Arial", 10),
            bg=COLOR_TARJETA, fg=COLOR_GRIS,
            relief="flat", height=3, wrap="word",
            state="disabled", bd=10
        )
        self.area_sinopsis.pack(fill="x", padx=24, pady=(0, 12))

    def _actualizar_scroll(self, evento):
        """Recalcula el área de scroll cuando cambia el tamaño del marco de tarjetas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _buscar(self):
        """Realiza la búsqueda en TMDB y muestra los resultados en la lista."""
        consulta = self.campo_busqueda.get().strip()
        if not consulta:
            return

        self.texto_estado.set("Buscando…")
        self.ventana.update()

        try:
            self.resultados_busqueda = self.motor.buscar(consulta)
            self.lista_resultados.delete(0, tk.END)

            for resultado in self.resultados_busqueda:
                icono = "🎬" if resultado.get("media_type") == "movie" else "📺"
                titulo = resultado.get("title") or resultado.get("name", "")
                anio = (resultado.get("release_date") or
                        resultado.get("first_air_date") or "")[:4]
                self.lista_resultados.insert(tk.END, f"{icono} {titulo} ({anio})")

            self.texto_estado.set(
                f"{len(self.resultados_busqueda)} resultados encontrados · "
                "Selecciona uno para ver recomendaciones"
            )
        except Exception as error:
            messagebox.showerror("Error de conexión",
                                 f"No se pudo conectar a TMDB:\n{error}")
            self.texto_estado.set("Error al conectar con TMDB")

    def _al_seleccionar(self, evento):
        """Carga las recomendaciones cuando el usuario selecciona un resultado."""
        seleccion = self.lista_resultados.curselection()
        if not seleccion:
            return

        elemento = self.resultados_busqueda[seleccion[0]]
        id_media   = elemento["id"]
        tipo_media = elemento.get("media_type", "movie")

        self.texto_estado.set("Cargando recomendaciones…")
        self.ventana.update()

        try:
            detalles = self.motor.obtener_detalles(id_media, tipo_media)
            recomendaciones = self.motor.obtener_recomendaciones(id_media, tipo_media)

            # Eliminar tarjetas anteriores
            for widget in self.marco_tarjetas.winfo_children():
                widget.destroy()
            self._tarjetas.clear()

            if not recomendaciones:
                tk.Label(
                    self.marco_tarjetas,
                    text="No hay recomendaciones disponibles para esta selección.",
                    font=("Arial", 12), fg=COLOR_GRIS, bg=COLOR_FONDO
                ).pack(pady=40)
            else:
                # Crear una tarjeta por cada recomendación
                for rec in recomendaciones:
                    tarjeta = TarjetaPelicula(self.marco_tarjetas, rec, self.motor)
                    tarjeta.pack(side="left", padx=8, pady=8)
                    self._tarjetas.append(tarjeta)

            # Actualizar el área de sinopsis con los detalles de la selección
            self.area_sinopsis.configure(state="normal")
            self.area_sinopsis.delete("1.0", tk.END)
            generos = ", ".join(detalles["generos"]) or "No disponible"
            texto_info = (
                f"{detalles['titulo']}  ·  "
                f"Géneros: {generos}  ·  "
                f"⭐ {detalles['puntuacion']:.1f}\n"
                f"{detalles['sinopsis']}"
            )
            self.area_sinopsis.insert("1.0", texto_info)
            self.area_sinopsis.configure(state="disabled")

            self.texto_estado.set(
                f"{len(recomendaciones)} recomendaciones para '{detalles['titulo']}'  ·  "
                "Pasa el cursor sobre un póster para ver la sinopsis · Clic para ver en cliver.mom"
            )

        except Exception as error:
            messagebox.showerror("Error",
                                 f"No se pudieron cargar las recomendaciones:\n{error}")


# ──────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ──────────────────────────────────────────────
if __name__ == "__main__":
    ventana_principal = tk.Tk()
    Aplicacion(ventana_principal)
    ventana_principal.mainloop()
