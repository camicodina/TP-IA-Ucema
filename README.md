# TP Inteligencia Artificial - UCEMA 

**Alumnos:** Camila Codina, Isabella Marafioti, Luca Sucri, Luciano Esteban y Martin Garcia

Este proyecto es una web application con un frontend construido en Angular y un backend con FastAPI (Python).

## ⚙️ Prerequisitos

- Node.js y npm (para el frontend)
- Python 3.13 o superior (para el backend)
- Angular CLI

---

## -- Backend --

El backend es una aplicación de Python que utiliza el framework FastAPI.

### Instalación 

1. Se recomienda usar un entorno virtual para instalar las dependencias. Crea y activa un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```
2. Instala los paquetes requeridos usando pip:

```bash
pip3 install -r backend/requirements.txt
```

### Ejecución 

Para correr el servidor del backend, navega al directorio backend y usa uvicorn:

```bash
cd backend
py -m uvicorn main:app --reload
```

El backend se estará ejecutando en http://127.0.0.1:8000.

---

## -- Frontend --

El frontend es una aplicación de Angular.

### Instalación 

1. Navega al directorio frontend:

```bash
cd frontend
```
2. Instala los paquetes npm:

```bash
npm install
```

### Ejecución 

Para iniciar el servidor de desarrollo, ejecuta:

```bash
ng serve
```
Navega a http://localhost:4200/. 
La aplicación se recargará automáticamente si cambias alguno de los archivos de origen.

---

## ▶️ Probar la app:

Graba o sube un archivo y mirá cómo lo clasifica!
