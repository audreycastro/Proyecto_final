from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import zipfile
import os
import time

#:(((
def configurar_selenium():

    print("\n=== CONFIGURANDO SELENIUM ===")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Configurar carpeta de descargas
    download_dir = os.path.join(os.getcwd(), "descargas")
    os.makedirs(download_dir, exist_ok=True)

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print(" Selenium configurado correctamente")
    return driver, download_dir


def scraping_tabla_inegi(driver):
    """
    Hace web scraping de la tabla HTML del INEGI
    """
    print("\n=== WEB SCRAPING: TABLA HTML DEL INEGI ===")

    try:
        # Navegar a la pagina del INEGI
        url_inegi = "https://www.inegi.org.mx/temas/incidencia/"
        print(f"Navegando a: {url_inegi}")
        driver.get(url_inegi)

        #  para que la pagina cargue completamente
        print("Esperando a que la página cargue")
        time.sleep(10)

        # Intentar esperar a que la tabla esté presente
        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print(" Tabla detectada en la pagina")
        except:
            print(" La tabla puede no estar cargada aun")

        # Obtener el HTML de la página
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Buscar la tabla
        print("Extrayendo tabla HTML...")
        tabla = soup.find('table')

        if not tabla:
            print(" No se encontro la tabla en la pagina")
            print("  (La tabla puede cargarse dinámicamente con JavaScript)")
            return None

        # Extraer encabezados
        encabezados = []
        thead = tabla.find('thead')
        if thead:
            for th in thead.find_all('th'):
                encabezados.append(th.text.strip())

        # Si no hay thead, buscar en la primera fila
        if not encabezados:
            primera_fila = tabla.find('tr')
            if primera_fila:
                for th in primera_fila.find_all(['th', 'td']):
                    encabezados.append(th.text.strip())

        print(f" Encabezados encontrados: {len(encabezados)}")

        # Extraer filas de datos
        filas = []
        tbody = tabla.find('tbody')
        if tbody:
            for tr in tbody.find_all('tr'):
                fila = []
                for td in tr.find_all('td'):
                    fila.append(td.text.strip())
                if fila:
                    filas.append(fila)
        else:
            # Si no hay tbody, buscar todas las filas exepto la primera
            todas_filas = tabla.find_all('tr')[1:]
            for tr in todas_filas:
                fila = []
                for td in tr.find_all('td'):
                    fila.append(td.text.strip())
                if fila:
                    filas.append(fila)

        print(f" Filas extraidas: {len(filas)}")

        # Crear DataFrame
        df = pd.DataFrame(filas, columns=encabezados if encabezados else None)

        # Filtrar por estados de interes
        estados_interes = ['Baja California', 'Sinaloa', 'Chihuahua']
        if 'Entidad' in df.columns:
            df = df[df['Entidad'].isin(estados_interes)]

        print(f" Datos del INEGI extraidos: {len(df)} registros")

        return df

    except Exception as e:
        print(f" Error en scraping del INEGI: {e}")
        print("  (Continuando con la descarga del SESNSP...)")
        return None


def descargar_archivo_sesnsp(driver, download_dir):
    """
    Descarga el archivo del SESNSP usando Selenium
    """
    print("\n=== WEB SCRAPING: DESCARGA DE ARCHIVO DEL SESNSP ===")

    try:
        # Navegar a la pagina del SESNSP
        url_sesnsp = "https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva"
        print(f"Navegando a: {url_sesnsp}")
        driver.get(url_sesnsp)
        time.sleep(5)

        # Buscar el enlace de descarga con texto parcial
        print("Buscando enlace de descarga...")
        wait = WebDriverWait(driver, 20)

        try:
            # Intentar buscar por texto parcial
            enlace_descarga = wait.until(EC.element_to_be_clickable((
                By.PARTIAL_LINK_TEXT, "2015 -2025"
            )))
            print(f" Enlace encontrado por texto parcial")
        except:
            try:
                # Alternativa: buscar por otro texto parcial
                enlace_descarga = wait.until(EC.element_to_be_clickable((
                    By.PARTIAL_LINK_TEXT, "Fuero Común - Delitos"
                )))
                print(f" Enlace encontrado por texto alternativo")
            except:
                print("No se encontro el enlace de descarga")
                return None

        # Obtener el texto del enlace para confirmar
        texto_enlace = enlace_descarga.text
        print(f"  Texto del enlace: {texto_enlace[:80]}...")

        # Hacer clic en el enlace
        print("Haciendo clic en el enlace...")
        enlace_descarga.click()
        time.sleep(8)

        # Cambiar a la nueva ventana (OneDrive)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            print(" Cambiado a ventana de OneDrive")
            time.sleep(5)

            # buscar y hacer clic en el botn de descarga
            try:
                print("Buscando botón de descarga...")
                boton_descarga = wait.until(EC.element_to_be_clickable((By.ID, "downloadCommand")))
                print(" Botón de descarga encontrado")
                boton_descarga.click()
                print(" Descarga iniciada")

                # Esperar a que se complete la descarga
                print("Esperando a que se complete la descarga...")
                archivo_zip = esperar_descarga(download_dir, timeout=230)

                if archivo_zip:
                    print(f" Archivo descargado: {archivo_zip}")
                    return archivo_zip
                else:
                    print("✗ Timeout: La descarga tardó demasiado")
                    return None

            except Exception as e:
                print(f" Error al hacer clic en botón de descarga: {e}")

                return None
        else:
            print(" no se abrio ventana de OneDrive")
            return None

    except Exception as e:
        print(f" Error en descarga del SESNSP: {e}")
        import traceback
        traceback.print_exc()
        return None


def esperar_descarga(download_dir, timeout=230):
    """
    Espera a que se complete la descarga
    """
    tiempo_espera = 0

    while tiempo_espera < timeout:
        # Buscar archivos ZIP
        archivos = [f for f in os.listdir(download_dir) if f.endswith('.zip')]

        # Verificar que no sean archivos temporales
        archivos_completos = [f for f in archivos if not f.endswith('.crdownload') and not f.endswith('.tmp')]

        if archivos_completos:
            archivo_zip = os.path.join(download_dir, archivos_completos[0])
            # Verificar que el archivo tenga tamaño > 0
            if os.path.getsize(archivo_zip) > 1000000:  # Más de 1 MB
                return archivo_zip

        time.sleep(2)
        tiempo_espera += 2

        if tiempo_espera % 10 == 0:
            print(f"  Esperando descarga ({tiempo_espera}s)")

    return None


def extraer_csv_de_zip(archivo_zip, download_dir):
    """
    Extrae el archivo CSV del ZIP descargado
    """
    print("\n=== EXTRAYENDO ARCHIVO CSV ===")

    try:
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            archivos = zip_ref.namelist()
            print(f"Archivos en el ZIP: {archivos}")

            # Buscar el archivo CSV
            archivo_csv = [f for f in archivos if f.endswith('.csv')][0]

            print(f"Extrayendo: {archivo_csv}")
            zip_ref.extract(archivo_csv, download_dir)

            ruta_csv = os.path.join(download_dir, archivo_csv)
            print(f" CSV extraido: {ruta_csv}")

            return ruta_csv

    except Exception as e:
        print(f" Error al extraer CSV: {e}")
        return None


def procesar_datos_sesnsp(ruta_csv):
    """
    Procesa el CSV del SESNSP
    """
    print("\n=== PROCESANDO DATOS DEL SESNSP ===")

    try:
        # Leer CSV
        print("Leyendo archivo CSV...")
        df = pd.read_csv(ruta_csv, encoding='latin-1', low_memory=False)

        print(f" Datos cargados: {len(df)} registros")

        # Filtrar por estados
        estados_interes = ['Baja California', 'Sinaloa', 'Chihuahua']
        df = df[df['Entidad'].isin(estados_interes)]
        print(f" Filtrado por estados: {len(df)} registros")

        # Filtrar por años
        df = df[df['Año'].isin([2023, 2024])]
        print(f" Filtrado por años 2023-2024: {len(df)} registros")

        # Filtrar por delitos relevantes
        delitos_relevantes = [
            'Homicidio', 'Secuestro', 'Robo',
            'Violencia familiar', 'Lesiones'
        ]

        df = df[df['Tipo de delito'].str.contains('|'.join(delitos_relevantes), case=False, na=False)]
        print(f" Filtrado por delitos relevantes: {len(df)} registros")

        # Transformar de formato wide a long
        print("Transformando formato de datos (wide → long)...")

        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        columnas_id = ['Año', 'Entidad', 'Tipo de delito', 'Subtipo de delito', 'Modalidad']
        meses_disponibles = [m for m in meses if m in df.columns]

        df_long = pd.melt(
            df,
            id_vars=columnas_id,
            value_vars=meses_disponibles,
            var_name='mes',
            value_name='cantidad'
        )

        # Renombrar columnas
        df_long = df_long.rename(columns={
            'Año': 'anio',
            'Entidad': 'estado',
            'Tipo de delito': 'tipo_delito',
            'Subtipo de delito': 'subtipo_delito',
            'Modalidad': 'modalidad'
        })

        # Agregar columna mes_num
        meses_dict = {
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
            'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
            'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
        }
        df_long['mes_num'] = df_long['mes'].map(meses_dict)

        # Agregar columnas adicionales
        df_long['fecha'] = df_long['anio'].astype(str) + '-' + df_long['mes_num'].astype(str).str.zfill(2)
        df_long['periodo'] = df_long['mes'] + ' ' + df_long['anio'].astype(str)

        # Convertir cantida a numerico
        df_long['cantidad'] = pd.to_numeric(df_long['cantidad'], errors='coerce').fillna(0).astype(int)

        # Eliminar registros con cantidad 0
        df_long = df_long[df_long['cantidad'] > 0]

        print(f" Datos finales del SESNSP: {len(df_long)} registros")

        return df_long

    except Exception as e:
        print(f" Error al procesar datos: {e}")
        import traceback
        traceback.print_exc()
        return None


def generar_datos_percepcion(df_delitos):
    """
    Genera datos de percepcion de seguridad
    """
    print("\n=== GENERANDO DATOS DE PERCEPCION ===")

    percepcion = df_delitos.groupby(['anio', 'estado'])['cantidad'].sum().reset_index()
    percepcion.columns = ['anio', 'estado', 'total_delitos']

    max_delitos = percepcion['total_delitos'].max()
    min_delitos = percepcion['total_delitos'].min()

    percepcion['percepcion_inseguridad'] = (
            60 + (percepcion['total_delitos'] - min_delitos) / (max_delitos - min_delitos) * 35
    ).round(2)

    print(f" Datos de percepcion generados: {len(percepcion)} registros")

    return percepcion


def guardar_datos(df, nombre_archivo):
    """
    Guarda los datos en un archivo CSV
    """
    dataset_dir = "dataset"
    os.makedirs(dataset_dir, exist_ok=True)

    ruta = os.path.join(dataset_dir, nombre_archivo)
    df.to_csv(ruta, index=False, encoding='utf-8')

    print(f" Guardado: {ruta}")
    return ruta


def main():
    """
    Función principal
    """
    print("=" * 60)
    print("EXTRACCION DE DATOS - WEB SCRAPING ")

    print("=" * 60)

    # Configurar Selenium
    driver, download_dir = configurar_selenium()

    try:
        # Web Scraping de tabla HTML del INEGI (opcional/complementario)
        print("\n" + "=" * 60)
        print("FUENTE 1: INEGI (Scraping de tabla HTML)")
        print("=" * 60)
        df_inegi = scraping_tabla_inegi(driver)

        #Descarga de archivo del SESNSP con Selenium
        print("\n" + "=" * 60)
        print("FUENTE 2: SESNSP (Descarga con navegador)")
        print("=" * 60)
        archivo_zip = descargar_archivo_sesnsp(driver, download_dir)

        if not archivo_zip:


            print("1. Descarga manualmente el archivo desde:")
            print("   https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva")

            return

        # Extraer CSV del ZIP
        ruta_csv = extraer_csv_de_zip(archivo_zip, download_dir)

        if not ruta_csv:
            print("\n No se pudo extraer el CSV del ZIP")
            return

        # Procesar datos
        df_delitos = procesar_datos_sesnsp(ruta_csv)

        if df_delitos is None or len(df_delitos) == 0:
            print("\n No se pudieron procesar los datos")
            return

        # Generar datos de percepcion
        df_percepcion = generar_datos_percepcion(df_delitos)

        #  Guardar datos
        print("\n=== GUARDANDO DATOS ===")
        guardar_datos(df_delitos, "incidencia_delictiva.csv")
        guardar_datos(df_percepcion, "percepcion_seguridad.csv")

        if df_inegi is not None and len(df_inegi) > 0:
            guardar_datos(df_inegi, "datos_inegi.csv")

        # Mostrar resumen
        print("\n" + "=" * 60)
        print(" EXTRACCIÓN DE DATOS COMPLETADA")
        print("=" * 60)
        print(f"\nTotal de registros extraidos: {len(df_delitos)}")
        print(f"Estados: {df_delitos['estado'].unique().tolist()}")
        print(f"Años: {sorted(df_delitos['anio'].unique().tolist())}")
        print(f"Tipos de delito únicos: {df_delitos['tipo_delito'].nunique()}")

        print("\nArchivos generados:")
        print("  - dataset/incidencia_delictiva.csv")
        print("  - dataset/percepcion_seguridad.csv")
        if df_inegi is not None:
            print("  - dataset/datos_inegi.csv")

        print("\nMétodos de web scraping utilizados:")
        print("   Selenium - Navegación automatica")
        print("   Selenium - Descarga de archivos")
        if df_inegi is not None:
            print("  BeautifulSoup - Scraping de tablas HTML")



    finally:
        # Cerrar el navegador
        print("\nCerrando navegador...")
        driver.quit()
        print(" Navegador cerrado")


if __name__ == "__main__":
    main()