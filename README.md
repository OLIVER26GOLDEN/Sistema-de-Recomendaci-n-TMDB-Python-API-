<div align="center">

<img src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg" width="180" alt="TMDB"/>

# 🎬 Recomendador de Películas y Series

**Aplicación de escritorio en Python que recomienda películas y series en tiempo real usando la API oficial de TMDB.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TMDB](https://img.shields.io/badge/API-TMDB-01B4E4?style=for-the-badge&logo=themoviedb&logoColor=white)](https://www.themoviedb.org/)
[![Pillow](https://img.shields.io/badge/Pillow-imaging-11557C?style=for-the-badge)](https://python-pillow.org/)
[![License](https://img.shields.io/badge/Licencia-MIT-22C55E?style=for-the-badge)](LICENSE)

</div>

---

## 📸 Vista previa

```
╔══════════════════════════════════════════════════════════════════╗
║  TMDB   Recomendador de Películas y Series                       ║
╠══════════════════════════════════════════════════════════════════╣
║  🔍  [ Inception                          ]  [ Buscar ]          ║
║  ─────────────────────────────────────────────────────────────   ║
║  Resultados          │  Recomendaciones                          ║
║                      │                                           ║
║  🎬 Inception (2010) │  ┌───────┐ ┌───────┐ ┌───────┐ ┌──────┐ ║
║  🎬 Interstellar     │  │  🖼️  │ │  🖼️  │ │  🖼️  │ │ 🖼️  │ ║
║  📺 Dark             │  │poster │ │poster │ │poster │ │poster│ ║
║                      │  ├───────┤ ├───────┤ ├───────┤ ├──────┤ ║
║                      │  │Tenet  │ │Matrix │ │ Dark  │ │Dune  │ ║
║                      │  │⭐ 7.4 │ │⭐ 8.7 │ │⭐ 8.8 │ │⭐8.0 │ ║
║                      │  │Película│ │Película│ │ Serie │ │Película║
║                      │  └───────┘ └───────┘ └───────┘ └──────┘ ║
║  ─────────────────────────────────────────────────────────────   ║
║  Inception · Ciencia ficción, Acción · ⭐ 8.4                    ║
║  Un ladrón que roba secretos del subconsciente...                ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## ⚡ Características principales

| Función | Descripción |
|---|---|
| 🔍 **Búsqueda en tiempo real** | Encuentra cualquier película o serie al instante via API |
| 🎴 **Tarjetas con póster** | Imágenes oficiales descargadas automáticamente desde TMDB |
| ⭐ **Puntuación cromática** | Amarillo ≥7 · Naranja ≥5 · Gris para el resto |
| 💬 **Sinopsis on hover** | Tooltip con descripción al pasar el cursor sobre el póster |
| 🌐 **Apertura directa** | Clic en la tarjeta → página oficial de TMDB en el navegador |
| ⚡ **Carga asíncrona** | Pósters descargados en segundo plano sin bloquear la UI |
| 🌍 **100% en español** | Interfaz y resultados completamente en español |

---

## 🛠️ Stack tecnológico

```python
stack = {
    "lenguaje"     : "Python 3.8+",
    "interfaz"     : "tkinter",
    "api"          : "TMDB REST API v3",
    "imágenes"     : "Pillow (PIL)",
    "concurrencia" : "threading",
    "http"         : "requests",
    "navegador"    : "webbrowser"
}
```

---

## 🚀 Instalación y uso

### Prerrequisitos

- Python 3.8 o superior
- API key gratuita de [TMDB](https://www.themoviedb.org/signup)

### Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/recomendador-tmdb.git
cd recomendador-tmdb

# 2. Instala dependencias
pip install requests Pillow

# 3. Añade tu API key en netflix_tmdb_es.py
CLAVE_API = "tu_api_key_aqui"

# 4. Ejecuta
python netflix_tmdb_es.py
```

> 💡 `tkinter` viene incluido con Python — no requiere instalación adicional.

---

## 🎯 Cómo funciona

```
Usuario escribe título
        │
        ▼
  API TMDB /search ──► Lista de resultados
        │
  Usuario selecciona
        │
        ▼
  API TMDB /recommendations ──► Hasta 12 títulos
        │
        ├──► Descarga pósters en hilos paralelos (threading)
        │
        ▼
  Interfaz muestra tarjetas con póster + puntuación + sinopsis
        │
  Usuario hace clic
        │
        ▼
  Abre página oficial en TMDB (webbrowser)
```

---

## 📁 Estructura del proyecto

```
recomendador-tmdb/
├── 📄 netflix_tmdb_es.py    ← Aplicación principal
│    ├── MotorTMDB           ← Clase: comunicación con la API
│    ├── TarjetaPelicula     ← Clase: widget visual de cada recomendación
│    └── Aplicacion          ← Clase: ventana principal y lógica de UI
└── 📄 README.md
```

---

## 🔮 Mejoras futuras

- [ ] 🎭 Filtro por género, año o idioma
- [ ] ❤️ Lista de favoritos persistente
- [ ] 🎞️ Reproductor de tráiler integrado
- [ ] 📊 Estadísticas de tus géneros favoritos
- [ ] 📤 Exportar recomendaciones a PDF o CSV

---

## 📄 Licencia y créditos

Distribuido bajo licencia **MIT**. Datos e imágenes proporcionados por
[The Movie Database (TMDB)](https://www.themoviedb.org/).

> Este producto usa la API de TMDB pero no está respaldado ni certificado por TMDB.

---

<div align="center">

Hecho con 🐍 Python por **oliverlugo**

</div>
