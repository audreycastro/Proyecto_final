import pandas as pd
import requests


def extraer_datos_sesnsp():
    """
    Extrae datos de incidencia delictiva del SESNSP
    Simula descarga de archivos CSV/Excel
    """
    # URL base para datos abiertos
    url_base = "https://drive.google.com/uc?export=download&id="

    # IDs de archivos públicos de datos de incidencia delictiva
    # Nota: En producción, estos serían los archivos oficiales del SESNSP
    # Para este proyecto, crearemos datos sintéticos basados en la estructura real

    print("Extrayendo datos de incidencia delictiva...")

    # Crear dataset sintético con estructura real
    datos = crear_datos_sinteticos()

    return datos


def crear_datos_sinteticos():
    """
    Crea datos sintéticos de incidencia delictiva
    para Baja California, Sinaloa y Chihuahua (2023-2024)
    """
    import random
    from datetime import datetime, timedelta

    estados = ["Baja California", "Sinaloa", "Chihuahua"]
    tipos_delito = ["Homicidio", "Secuestro", "Robo", "Violencia familiar", "Extorsión"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    anios = [2023, 2024]

    datos = []

    for anio in anios:
        for mes_num, mes in enumerate(meses, 1):
            for estado in estados:
                for tipo_delito in tipos_delito:
                    # Generar cantidad de delitos con variación realista
                    if tipo_delito == "Homicidio":
                        cantidad = random.randint(50, 200)
                    elif tipo_delito == "Secuestro":
                        cantidad = random.randint(5, 30)
                    elif tipo_delito == "Robo":
                        cantidad = random.randint(300, 800)
                    elif tipo_delito == "Violencia familiar":
                        cantidad = random.randint(200, 600)
                    else:  # Extorsión
                        cantidad = random.randint(50, 150)

                    # Ajustar por estado (Sinaloa tiene más violencia)
                    if estado == "Sinaloa":
                        cantidad = int(cantidad * 1.3)
                    elif estado == "Baja California":
                        cantidad = int(cantidad * 1.1)

                    datos.append({
                        "anio": anio,
                        "mes": mes,
                        "mes_num": mes_num,
                        "estado": estado,
                        "tipo_delito": tipo_delito,
                        "cantidad": cantidad
                    })

    df = pd.DataFrame(datos)
    return df


def extraer_datos_inegi():
    """
    Simula extracción de datos del INEGI sobre percepción de seguridad
    """
    print("Extrayendo datos de percepción de seguridad INEGI...")

    estados = ["Baja California", "Sinaloa", "Chihuahua"]
    anios = [2023, 2024]

    datos = []

    for anio in anios:
        for estado in estados:
            # Percepción de inseguridad (0-100)
            if estado == "Sinaloa":
                percepcion = random.randint(75, 90)
            elif estado == "Baja California":
                percepcion = random.randint(70, 85)
            else:  # Chihuahua
                percepcion = random.randint(65, 80)

            datos.append({
                "anio": anio,
                "estado": estado,
                "percepcion_inseguridad": percepcion
            })

    df = pd.DataFrame(datos)
    return df


def guardar_datos_csv(df, nombre_archivo):
    """
    Guarda el DataFrame en formato CSV
    """
    ruta = f"dataset/{nombre_archivo}"
    df.to_csv(ruta, index=False, encoding='utf-8-sig')
    print(f"Datos guardados en: {ruta}")
    return ruta


def extraer_todos():
    """
    Ejecuta todas las extracciones y guarda los datos
    """
    # Extraer datos de incidencia delictiva
    df_delitos = extraer_datos_sesnsp()
    guardar_datos_csv(df_delitos, "incidencia_delictiva.csv")

    # Extraer datos de percepción
    df_percepcion = extraer_datos_inegi()
    guardar_datos_csv(df_percepcion, "percepcion_seguridad.csv")

    print("\n=== Resumen de extracción ===")
    print(f"Total de registros de delitos: {len(df_delitos)}")
    print(f"Total de registros de percepción: {len(df_percepcion)}")
    print(f"Estados analizados: Baja California, Sinaloa, Chihuahua")
    print(f"Periodo: 2023-2024")

    return df_delitos, df_percepcion


if __name__ == "__main__":
    import random

    random.seed(42)  # Para reproducibilidad

    # Crear directorio para datasets
    import os

    os.makedirs("dataset", exist_ok=True)

    # Ejecutar extracción
    df_delitos, df_percepcion = extraer_todos()

    # Mostrar muestra de datos
    print("\n=== Muestra de datos de delitos ===")
    print(df_delitos.head(10))
    print("\n=== Muestra de datos de percepción ===")
    print(df_percepcion.head())
