# Análisis de Violencia y Seguridad Pública en México

Este proyecto fue desarrollado para la materia de "Programación Para la Extracción de Datos" y tiene como objetivo analizar la problemática social de la violencia y seguridad pública en México, enfocándose en los estados de Baja California, Sinaloa y Chihuahua durante el periodo 2023-2024.

## Preguntas de Investigación (Objetivos)

El proyecto se centra en responder las siguientes preguntas:

1.  **¿Cuáles son los estados con mayor incidencia delictiva y cómo ha evolucionado esta tendencia en los últimos años?**
2.  **¿Qué tipos de delitos (homicidios, secuestros, robos, violencia familiar) son más frecuentes en las diferentes regiones del país?**
3.  **¿Cuál es el promedio mensual de delitos por estado y en qué meses se registra mayor actividad delictiva?**

## Fuentes de Datos

Para este análisis, se utilizaron las siguientes fuentes de datos:

*   **Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP):** Se consultaron los datos abiertos de incidencia delictiva para obtener información sobre los delitos registrados en el fuero común.
*   **Instituto Nacional de Estadística y Geografía (INEGI):** Se tomaron como referencia los datos de la Encuesta Nacional de Victimización y Percepción sobre Seguridad Pública (ENVIPE) para complementar el análisis.

Los datos se extraen en tiempo real mediante **web scraping con Selenium** del portal de Datos Abiertos del SESNSP, garantizando que el análisis se basa en la información más reciente y oficial.

## Estructura del Proyecto

El proyecto está organizado en los siguientes archivos, siguiendo un enfoque modular:

### Scripts de ETL

*   `extraccion_datos.py`: Script de **web scraping con Selenium** para extraer datos reales del portal del SESNSP.
*   `transformacion_datos.py`: Realiza la limpieza, validación, normalización y enriquecimiento de los datos extraídos.
*   `crear_bd.sql`: Script SQL para crear la estructura de la base de datos `seguridad_mexico` en MySQL, incluyendo tablas, relaciones y vistas.
*   `carga_bd.py`: Contiene las funciones para conectarse a la base de datos MySQL y cargar los datos transformados.

### Visualización

*   **`dashboard.py`**: Aplicación web interactiva con Dash que presenta el análisis completo con gráficas interactivas (RECOMENDADO)

### Carpetas

*   `dataset/`: Contiene los archivos CSV con los datos extraídos y transformados


## Instrucciones de Uso




### Creación de la Base de Datos en MySQL

1.  Abre MySQL 
2.  Abre el archivo `db_seguridadMexico.sql`.
3.  Ejecuta el script completo. Esto creará la base de datos `seguridad_mexico` y todas sus tablas y vistas.

### Configuración de la Conexión en PyCharm

*   Abre los archivos `carga_bd.py`, `visualizacion.py` y `dashboard.py` en PyCharm
*   Modifica las credenciales de conexión a tu base de datos en la clase `DataDB`:

```python
class DataDB:
    USER = "tu_usuario_mysql"
    PASSWORD = "tu_contraseña_mysql"
    NAME_BD = "seguridad_mexico"
    SERVER = "localhost"
```

### Ejecución del Proyecto

####  Dashboard Web Interactivo 

**IMPORTANTE:** Asegúrate de haber creado la base de datos en mysql antes de ejecutar estos scripts.

Ejecuta los scripts en el siguiente orden desde la terminal de PyCharm:

**Nota:** La ejecución de `extraccion_datos.py` puede tardar varios minutos mientras realiza el web scraping y descarga los archivos. Aunque en este caso no funcione al 100% aunque se supone que esta bien implementado (se trato de arreglar de todas las maneras posibles u.u), en la carpeta de datasets están los archivos que se supone se extrajeron del webscrapping, agregarlos a una carpeta llamada datasets en pycharm y correr la tranformacion de datos:



# 1. Extraer los datos
python extraccion_datos.py

# 2. Transformar los datos
python transformacion_datos.py

# 3. Cargar a MySQL
python carga_bd.py

# 4. Iniciar el dashboard web
python dashboard.py


Luego abre tu navegador en: **http://localhost:8050**


## Dashboard Web Interactivo

El dashboard web incluye las siguientes secciones:

### Inicio
- Introducción al problema de violencia y seguridad pública
- Contexto sobre los estados analizados
- Imágenes relacionadas con el tema

### Dashboard
- 6 gráficas interactivas con Plotly:
  1. Incidencia delictiva por estado (2023-2024)
  2. Tipos de delitos por estado
  3. Promedio mensual de delitos
  4. Evolución temporal de delitos graves
  5. Distribución de tipos de delitos
  6. Relación entre delitos y percepción de inseguridad


