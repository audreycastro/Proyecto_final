import pandas as pd
import os


def leer_datos():
   #Leer los dato extraidos de los archivos csv
    print("\n=== LEYENDO DATOS EXTRAIDOS ===")

    archivo_incidencia = os.path.join("dataset", "incidencia_delictiva.csv")
    archivo_percepcion = os.path.join("dataset", "percepcion_seguridad.csv")

    try:
        df_incidencia = pd.read_csv(archivo_incidencia, encoding='utf-8')
        df_percepcion = pd.read_csv(archivo_percepcion, encoding='utf-8')

        print(f" Datos de incidencia cargados: {len(df_incidencia)} registros")
        print(f" Datos de percepción cargados: {len(df_percepcion)} registros")

        return df_incidencia, df_percepcion

    except Exception as e:
        print(f" Error al leer datos: {e}")
        return None, None


def limpiar_datos(df):

    print("\n=== LIMPIANDO DATOS ===")

    registros_iniciales = len(df)

    # Eliminar duplicados
    df = df.drop_duplicates()
    print(f" Duplicados eliminados: {registros_iniciales - len(df)}")

    # Eliminar registros con valores nulos en columnas importantes
    df = df.dropna(subset=['anio', 'estado', 'tipo_delito', 'cantidad'])
    print(f" Registros con nulos eliminados: {registros_iniciales - len(df)}")

    # Validar que cantidad sea positiva
    df = df[df['cantidad'] > 0]

    # Limpiar espacios en blanco
    df['estado'] = df['estado'].str.strip()
    df['tipo_delito'] = df['tipo_delito'].str.strip()
    df['mes'] = df['mes'].str.strip()

    print(f" Datos limpios: {len(df)} registros")

    return df


def agregar_columnas(df):

    print("\n=== AGREGANDO COLUMNAS CALCULADAS ===")

    # Categorizar delitos en grupos principales
    def categorizar_delito(tipo):
        tipo_lower = str(tipo).lower()
        if 'homicidio' in tipo_lower:
            return 'Homicidio'
        elif 'secuestro' in tipo_lower:
            return 'Secuestro'
        elif 'robo' in tipo_lower:
            return 'Robo'
        elif 'violencia' in tipo_lower and 'familiar' in tipo_lower:
            return 'Violencia familiar'
        elif 'lesion' in tipo_lower:
            return 'Lesiones'
        else:
            return 'Otro'

    df['categoria_delito'] = df['tipo_delito'].apply(categorizar_delito)

    # Calcular porcentaje por estado
    total_por_estado = df.groupby('estado')['cantidad'].transform('sum')
    df['porcentaje_estado'] = (df['cantidad'] / total_por_estado) * 100

    print("✓ Columnas agregadas: categoria_delito, porcentaje_estado")

    return df


def calcular_estadisticas(df):

    print("\n=== CALCULANDO ESTADISTICAS ===")

    # Total de delitos por estado
    total_estado = df.groupby("estado")["cantidad"].sum().reset_index()
    total_estado.columns = ["estado", "total_delitos"]

    print("\nTotal de delitos por estado:")
    print(total_estado.to_string(index=False))

    # Promedio mensual por estado
    promedio_mensual = df.groupby("estado")["cantidad"].mean().reset_index()
    promedio_mensual.columns = ["estado", "promedio_mensual"]

    print("\nPromedio mensual por estado:")
    print(promedio_mensual.to_string(index=False))

    return total_estado, promedio_mensual


def normalizar_datos(df):

    print("\n=== NORMALIZANDO DATOS ===")

    # Normalización Min-Max
    max_cantidad = df['cantidad'].max()
    min_cantidad = df['cantidad'].min()

    df['cantidad_normalizada'] = (
            (df['cantidad'] - min_cantidad) / (max_cantidad - min_cantidad)
    )

    print(f"✓ Normalización completada (rango: {min_cantidad} - {max_cantidad})")

    return df


def filtrar_datos(df):

    print("\n=== FILTRANDO DATOS ===")

    # Filtrar delitos graves (homicidio y secuestro)
    delitos_graves = ["Homicidio", "Secuestro"]
    df_graves = df[df['categoria_delito'].isin(delitos_graves)]

    print(f" Registros de delitos graves: {len(df_graves)}")

    # Filtrar por cantidad alta (>= 100)
    df_alta_incidencia = df[df['cantidad'] >= 100]

    print(f" Registros con alta incidencia (>=100): {len(df_alta_incidencia)}")

    return df_graves, df_alta_incidencia


def unir_datos(df_delitos, df_percepcion):

    print("\n=== UNIENDO DATOS ===")

    # Agrupar delitos por año y estado
    df_delitos_agrupado = df_delitos.groupby(["anio", "estado"])["cantidad"].sum().reset_index()
    df_delitos_agrupado.columns = ["anio", "estado", "total_delitos"]

    # Unir con percepción
    df_unido = pd.merge(
        df_delitos_agrupado,
        df_percepcion[['anio', 'estado', 'percepcion_inseguridad']],
        on=["anio", "estado"],
        how="left"
    )

    print(f" Datos unidos: {len(df_unido)} registros")
    print("\nMuestra de datos unidos:")
    print(df_unido.to_string(index=False))

    return df_unido


def guardar_datos_transformados(df, nombre_archivo):

    #Guarda los datos transformados en CSV

    ruta = os.path.join("dataset", nombre_archivo)
    df.to_csv(ruta, index=False, encoding='utf-8')
    print(f" Guardado: {ruta}")
    return ruta


def mostrar_resumen(df):

    print("\n=== RESUMEN DE DATOS TRANSFORMADOS ===")

    print(f"\nTotal de registros: {len(df)}")
    print(f"Total de delitos: {df['cantidad'].sum():,}")
    print(f"Promedio de delitos por registro: {df['cantidad'].mean():.2f}")

    print("\n--- Por Estado ---")
    estado_stats = df.groupby('estado')['cantidad'].agg(['sum', 'mean', 'count'])
    print(estado_stats)

    print("\n--- Por Categoria de Delito ---")
    delito_stats = df.groupby('categoria_delito')['cantidad'].agg(['sum', 'mean', 'count'])
    print(delito_stats.sort_values('sum', ascending=False))


def transformar_todos():

    #Ejecuta todas las transformaciones

    print("=" * 60)
    print("TRANSFORMACION Y LIMPIEZA DE DATOS")
    print("Proyecto: Análisis de Violencia y Seguridad Pública en Mexico")
    print("=" * 60)

    #  Leer datos
    df_delitos, df_percepcion = leer_datos()

    if df_delitos is None or df_percepcion is None:
        print("\n No se pundieron leer los datos")
        return None, None, None

    #  Limpiar datos
    df_delitos_limpio = limpiar_datos(df_delitos)

    #  Agregar columnas calculadas
    df_delitos_limpio = agregar_columnas(df_delitos_limpio)

    #  Calcular estadisticas
    total_estado, promedio_mensual = calcular_estadisticas(df_delitos_limpio)

    #  Filtrar datos
    df_graves, df_alta_incidencia = filtrar_datos(df_delitos_limpio)

    #  Normalizar datos
    df_normalizado = normalizar_datos(df_delitos_limpio)

    #  Unir datos con percepcion
    df_unido = unir_datos(df_delitos_limpio, df_percepcion)

    # Guardar datos transformados
    print("\n=== GUARDANDO DATOS TRANSFORMADOS ===")
    guardar_datos_transformados(df_delitos_limpio, "delitos_transformados.csv")
    guardar_datos_transformados(df_normalizado, "delitos_normalizados.csv")
    guardar_datos_transformados(df_unido, "datos_unidos.csv")

    # Mostrar resumen
    mostrar_resumen(df_delitos_limpio)

    print("\n" + "=" * 60)
    print(" TRANSFORMACIÓN DE DATOS COMPLETADA")
    print("=" * 60)


    return df_delitos_limpio, df_normalizado, df_unido


if __name__ == "__main__":
    df_delitos, df_norm, df_unido = transformar_todos()

    if df_delitos is not None:
        print("\n=== Muestra de datos transformados ===")
        print(df_delitos.head(10))
