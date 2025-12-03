from mysql.connector import connect, Error
import pandas as pd


class DataDB:
    #Configuración de la base de datos
    USER = "root"
    PASSWORD = "Washmybelly2025"
    NAME_BD = "seguridad_mexico"
    SERVER = "localhost"


def conectar():

    #Establece conexión con la base de datos mysql
    #La base de datos previamente creada en mysql

    try:
        conexion = connect(
            host=DataDB.SERVER,
            user=DataDB.USER,
            password=DataDB.PASSWORD,
            database=DataDB.NAME_BD
        )
        print(" Conexión exitosa a la base de datos")
        return conexion
    except Error as e:
        print(f" Error al conectar: {e}")


        return None


def obtener_id_estado(nombre_estado, cursor):

    #Obtiene el id de un estado por su nombre

    sql = "SELECT id_estado FROM estados WHERE nombre = %s"
    cursor.execute(sql, (nombre_estado,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def insertar_tipo_delito(nombre, subtipo, modalidad, categoria, cursor):

    #Inserta un tipo de delito y retorna su id
    #Si ya existe, retorna el id existente

    # Verificar si ya existe
    sql_buscar = """SELECT id_tipo_delito FROM tipos_delito 
                    WHERE nombre = %s AND subtipo = %s AND modalidad = %s"""
    cursor.execute(sql_buscar, (nombre, subtipo, modalidad))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    # Si no existe, insertar
    sql_insertar = """INSERT INTO tipos_delito (nombre, subtipo, modalidad, categoria) 
                      VALUES (%s, %s, %s, %s)"""
    cursor.execute(sql_insertar, (nombre, subtipo, modalidad, categoria))
    return cursor.lastrowid


def insertar_tipos_delito(df):

    #Inserta todos los tipos de delito unicos del DataFrame

    print("\n=== INSERTANDO TIPOS DE DELITO ===")

    conexion = conectar()
    if not conexion:
        return

    cursor = conexion.cursor()

    # Obtener combinaciones únicas de delitos
    delitos_unicos = df[['tipo_delito', 'subtipo_delito', 'modalidad', 'categoria_delito']].drop_duplicates()

    registros_insertados = 0

    for _, row in delitos_unicos.iterrows():
        try:
            insertar_tipo_delito(
                row['tipo_delito'],
                row['subtipo_delito'],
                row['modalidad'],
                row['categoria_delito'],
                cursor
            )
            registros_insertados += 1
        except Error as e:
            print(f"Error al insertar delito: {e}")

    conexion.commit()
    cursor.close()
    conexion.close()

    print(f" Tipos de delito insertados: {registros_insertados}")


def obtener_id_tipo_delito(nombre, subtipo, modalidad, cursor):

    #Obtiene el id de un tipo de delito por su nombre, subtipo y modalidad

    sql = """SELECT id_tipo_delito FROM tipos_delito 
             WHERE nombre = %s AND subtipo = %s AND modalidad = %s"""
    cursor.execute(sql, (nombre, subtipo, modalidad))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def insertar_incidencia_delictiva(df):

    #Inserta datos de incidencia delictiva en la base de datos

    print("\n=== INSERTANDO INCIDENCIA DELICTIVA ===")

    conexion = conectar()
    if not conexion:
        return

    cursor = conexion.cursor()

    sql = """INSERT INTO incidencia_delictiva 
             (anio, mes, mes_num, id_estado, id_tipo_delito, cantidad, fecha, periodo, 
              porcentaje_estado, cantidad_normalizada)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    registros_insertados = 0
    registros_omitidos = 0

    for index, row in df.iterrows():
        id_estado = obtener_id_estado(row["estado"], cursor)
        id_tipo_delito = obtener_id_tipo_delito(
            row["tipo_delito"],
            row["subtipo_delito"],
            row["modalidad"],
            cursor
        )

        if id_estado and id_tipo_delito:
            try:
                valores = (
                    int(row["anio"]),
                    str(row["mes"]),
                    int(row["mes_num"]),
                    id_estado,
                    id_tipo_delito,
                    int(row["cantidad"]),
                    str(row["fecha"]),
                    str(row["periodo"]),
                    float(row.get("porcentaje_estado", 0)),
                    float(row.get("cantidad_normalizada", 0))
                )
                cursor.execute(sql, valores)
                registros_insertados += 1

                if registros_insertados % 100 == 0:
                    print(f"  Insertados: {registros_insertados} registros...")

            except Error as e:
                print(f"Error al insertar registro {index}: {e}")
                registros_omitidos += 1
        else:
            registros_omitidos += 1

    conexion.commit()
    cursor.close()
    conexion.close()

    print(f" Registros insertados: {registros_insertados}")
    print(f" Registros omitidos: {registros_omitidos}")


def insertar_percepcion_seguridad(df):

    #Inserta datos de percepción de seguridad en la base de datos

    print("\n=== INSERTANDO PERCEPCIÓN DE SEGURIDAD ===")

    conexion = conectar()
    if not conexion:
        return

    cursor = conexion.cursor()

    sql = """INSERT INTO percepcion_seguridad 
             (anio, id_estado, percepcion_inseguridad, total_delitos)
             VALUES (%s, %s, %s, %s)"""

    registros_insertados = 0

    for index, row in df.iterrows():
        id_estado = obtener_id_estado(row["estado"], cursor)

        if id_estado:
            try:
                valores = (
                    int(row["anio"]),
                    id_estado,
                    float(row["percepcion_inseguridad"]),
                    int(row.get("total_delitos", 0))
                )
                cursor.execute(sql, valores)
                registros_insertados += 1
            except Error as e:
                print(f"Error al insertar percepción: {e}")

    conexion.commit()
    cursor.close()
    conexion.close()

    print(f" Registros de percepción insertados: {registros_insertados}")


def leer_datos_transformados():

    #Lee los datos transformados desde los archivos CSV

    print("\n=== LEYENDO DATOS TRANSFORMADOS ===")

    try:
        df_delitos = pd.read_csv("dataset/delitos_transformados.csv", encoding='utf-8')
        df_percepcion = pd.read_csv("dataset/percepcion_seguridad.csv", encoding='utf-8')

        print(f"Datos de delitos cargados: {len(df_delitos)} registros")
        print(f"Datos de percepción cargados: {len(df_percepcion)} registros")

        return df_delitos, df_percepcion

    except Exception as e:
        print(f"Error al leer datos: {e}")
        return None, None


def verificar_carga():

    print("\n=== VERIFICANDO CARGA DE DATOS ===")

    conexion = conectar()
    if not conexion:
        return

    cursor = conexion.cursor()

    # Contar registros en cada tabla
    tablas = [
        "estados",
        "tipos_delito",
        "incidencia_delictiva",
        "percepcion_seguridad"
    ]

    for tabla in tablas:
        sql = f"SELECT COUNT(*) FROM {tabla}"
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        print(f"  {tabla}: {count} registros")

    cursor.close()
    conexion.close()


def main():

    #Función principal que ejecuta el proceso de carga

    print("=" * 60)
    print("CARGA DE DATOS A MYSQL")
    print("Proyecto: Análisis de Violencia y Seguridad Pública en México")
    print("=" * 60)

    #  Leer datos transformados
    df_delitos, df_percepcion = leer_datos_transformados()

    if df_delitos is None or df_percepcion is None:
        print("\n No se pudieron leer los datos transformados")

        return

    #  Insertar tipos de delito
    insertar_tipos_delito(df_delitos)

    #  Insertar incidencia delictiva
    insertar_incidencia_delictiva(df_delitos)

    #  Insertar percepcion de seguridad
    insertar_percepcion_seguridad(df_percepcion)

    #  Verificar carga
    verificar_carga()

    print("\n" + "=" * 60)
    print(" CARGA DE DATOS COMPLETADA")
    print("=" * 60)
    print("\nLa base de datos está lista para ser consultada")



if __name__ == "__main__":
    main()
