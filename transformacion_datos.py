import pandas as pd


def leer_datos():
    """
    Lee los datos extraídos desde los archivos CSV
    """
    df_delitos = pd.read_csv("dataset/incidencia_delictiva.csv")
    df_percepcion = pd.read_csv("dataset/percepcion_seguridad.csv")
    return df_delitos, df_percepcion


def limpiar_datos(df):
    """
    Limpia y valida los datos de delitos
    """
    # Eliminar duplicados
    df_limpio = df.drop_duplicates()

    # Eliminar valores nulos
    df_limpio = df_limpio.dropna()

    # Validar que cantidad sea positiva
    df_limpio = df_limpio[df_limpio.cantidad >= 0]

    print(f"Registros antes de limpiar: {len(df)}")
    print(f"Registros después de limpiar: {len(df_limpio)}")

    return df_limpio


def agregar_columnas(df):
    """
    Agrega columnas calculadas
    """
    # Crear columna de fecha completa
    df["fecha"] = df.apply(lambda row: f"{row['anio']}-{row['mes_num']:02d}-01", axis=1)
    df["fecha"] = pd.to_datetime(df["fecha"])

    # Crear columna de periodo (año-mes)
    df["periodo"] = df.apply(lambda row: f"{row['anio']}-{row['mes']}", axis=1)

    return df


def calcular_estadisticas(df):
    """
    Calcula estadísticas agregadas por estado
    """
    # Total de delitos por estado
    total_estado = df.groupby("estado")["cantidad"].sum().reset_index()
    total_estado.columns = ["estado", "total_delitos"]

    print("\n=== Total de delitos por estado ===")
    print(total_estado)

    # Promedio mensual por estado
    promedio_mensual = df.groupby("estado")["cantidad"].mean().reset_index()
    promedio_mensual.columns = ["estado", "promedio_mensual"]

    print("\n=== Promedio mensual por estado ===")
    print(promedio_mensual)

    return total_estado, promedio_mensual


def transformar_formato(df):
    """
    Transforma el formato de los datos para análisis
    """
    # Formato ancho: delitos por tipo como columnas
    df_ancho = df.pivot_table(
        index=["anio", "mes", "estado"],
        columns="tipo_delito",
        values="cantidad",
        aggfunc="sum"
    ).reset_index()

    print("\n=== Datos en formato ancho ===")
    print(df_ancho.head())

    return df_ancho


def normalizar_datos(df):
    """
    Normaliza los datos de cantidad de delitos usando Min-Max
    """
    # Crear copia para no modificar original
    df_norm = df.copy()

    # Normalización Min-Max por tipo de delito
    max_cantidad = df_norm.cantidad.max()
    min_cantidad = df_norm.cantidad.min()

    df_norm["cantidad_normalizada"] = (
            (df_norm.cantidad - min_cantidad) / (max_cantidad - min_cantidad)
    )

    return df_norm


def filtrar_datos(df):
    """
    Filtra datos según criterios específicos
    """
    # Filtrar delitos graves (homicidio y secuestro)
    delitos_graves = ["Homicidio", "Secuestro"]
    df_graves = df[df.tipo_delito.isin(delitos_graves)]

    print(f"\n=== Registros de delitos graves ===")
    print(f"Total: {len(df_graves)}")

    # Filtrar por cantidad alta (>= 100)
    df_alta_incidencia = df[df.cantidad >= 100]

    print(f"\n=== Registros con alta incidencia (>=100) ===")
    print(f"Total: {len(df_alta_incidencia)}")

    return df_graves, df_alta_incidencia


def unir_datos(df_delitos, df_percepcion):
    """
    Une los datos de delitos con percepción de seguridad
    """
    # Agrupar delitos por año y estado
    df_delitos_agrupado = df_delitos.groupby(["anio", "estado"])["cantidad"].sum().reset_index()
    df_delitos_agrupado.columns = ["anio", "estado", "total_delitos"]

    # Unir con percepción
    df_unido = pd.merge(
        df_delitos_agrupado,
        df_percepcion,
        on=["anio", "estado"],
        how="left"
    )

    print("\n=== Datos unidos (delitos + percepción) ===")
    print(df_unido)

    return df_unido


def guardar_datos_transformados(df, nombre_archivo):
    """
    Guarda los datos transformados
    """
    ruta = f"dataset/{nombre_archivo}"
    df.to_csv(ruta, index=False, encoding='utf-8-sig')
    print(f"\nDatos transformados guardados en: {ruta}")
    return ruta


def transformar_todos():
    """
    Ejecuta todas las transformaciones
    """
    print("=== INICIANDO TRANSFORMACIÓN DE DATOS ===\n")

    # Leer datos
    df_delitos, df_percepcion = leer_datos()

    # Limpiar datos
    df_delitos_limpio = limpiar_datos(df_delitos)

    # Agregar columnas
    df_delitos_limpio = agregar_columnas(df_delitos_limpio)

    # Calcular estadísticas
    total_estado, promedio_mensual = calcular_estadisticas(df_delitos_limpio)

    # Filtrar datos
    df_graves, df_alta_incidencia = filtrar_datos(df_delitos_limpio)

    # Normalizar datos
    df_normalizado = normalizar_datos(df_delitos_limpio)

    # Unir datos
    df_unido = unir_datos(df_delitos_limpio, df_percepcion)

    # Guardar datos transformados
    guardar_datos_transformados(df_delitos_limpio, "delitos_transformados.csv")
    guardar_datos_transformados(df_normalizado, "delitos_normalizados.csv")
    guardar_datos_transformados(df_unido, "datos_unidos.csv")

    print("\n=== TRANSFORMACIÓN COMPLETADA ===")

    return df_delitos_limpio, df_normalizado, df_unido


if __name__ == "__main__":
    df_delitos, df_norm, df_unido = transformar_todos()

    print("\n=== Muestra de datos transformados ===")
    print(df_delitos.head(10))
