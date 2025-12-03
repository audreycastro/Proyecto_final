import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine


class DataDB:
    #Configuración de la base de datos
    USER = "root"
    PASSWORD = "Washmybelly2025"
    NAME_BD = "seguridad_mexico"
    SERVER = "localhost"
    PORT = "3306"


def crear_engine():
    """
    Crea el engine de SQLAlchemy para conexión a MySQL
    """
    try:
        cadena_conexion = f"mysql+mysqlconnector://{DataDB.USER}:{DataDB.PASSWORD}@{DataDB.SERVER}:{DataDB.PORT}/{DataDB.NAME_BD}"
        engine = create_engine(cadena_conexion)
        return engine
    except Exception as e:
        print(f"Error al crear engine: {e}")
        return None


def obtener_datos_bd(query):
    """
    Ejecuta una consulta y retorna un DataFrame usando SQLAlchemy
    """
    engine = crear_engine()
    if not engine:
        return None

    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error al ejecutar query: {e}")
        return None


def crear_grafica_incidencia():
    """
    Grafica 1: Incidencia delictiva por estado
    """
    query = """
    SELECT 
        e.nombre as estado,
        i.anio,
        SUM(i.cantidad) as total_delitos
    FROM incidencia_delictiva i
    JOIN estados e ON i.id_estado = e.id_estado
    GROUP BY e.nombre, i.anio
    ORDER BY i.anio, total_delitos DESC
    """

    df = obtener_datos_bd(query)

    if df is None or df.empty:
        return go.Figure()

    fig = px.bar(df, x="estado", y="total_delitos", color="anio",
                 title="Incidencia Delictiva por Estado (2023-2024)",
                 labels={"total_delitos": "Total de Delitos", "estado": "Estado"},
                 barmode="group",
                 color_discrete_sequence=["#3498db", "#e74c3c"])

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        height=400
    )

    return fig


def crear_grafica_tipos_delito():
    """
    Grafica 2: Tipos de delitos por estado
    """
    query = """
    SELECT 
        t.categoria as tipo_delito,
        e.nombre as estado,
        SUM(i.cantidad) as total
    FROM incidencia_delictiva i
    JOIN tipos_delito t ON i.id_tipo_delito = t.id_tipo_delito
    JOIN estados e ON i.id_estado = e.id_estado
    WHERE t.categoria IS NOT NULL
    GROUP BY t.categoria, e.nombre
    ORDER BY total DESC
    """

    df = obtener_datos_bd(query)

    if df is None or df.empty:
        return go.Figure()

    fig = px.bar(df, x="tipo_delito", y="total", color="estado",
                 title="Tipos de Delitos por Estado",
                 labels={"total": "Total de Delitos", "tipo_delito": "Tipo de Delito"},
                 barmode="group",
                 color_discrete_sequence=["#3498db", "#2ecc71", "#f39c12"])

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        height=400,
        xaxis_tickangle=-45
    )

    return fig


def crear_grafica_promedio_mensual():
    """
    Grafica 3: Promedio mensual de delitos
    """
    query = """
    SELECT 
        e.nombre as estado,
        i.mes,
        i.mes_num,
        AVG(i.cantidad) as promedio
    FROM incidencia_delictiva i
    JOIN estados e ON i.id_estado = e.id_estado
    GROUP BY e.nombre, i.mes, i.mes_num
    ORDER BY i.mes_num
    """

    df = obtener_datos_bd(query)

    if df is None or df.empty:
        return go.Figure()

    fig = px.line(df, x="mes", y="promedio", color="estado",
                  title="Promedio Mensual de Delitos por Estado",
                  labels={"promedio": "Promedio de Delitos", "mes": "Mes"},
                  markers=True,
                  color_discrete_sequence=["#3498db", "#2ecc71", "#f39c12"])

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        height=400,
        xaxis_tickangle=-45
    )

    return fig


def crear_grafica_evolucion():
    """
    Grafica 4: Evolucion temporal de delitos graves
    """
    query = """
    SELECT 
        i.fecha,
        t.nombre as tipo_delito,
        SUM(i.cantidad) as total
    FROM incidencia_delictiva i
    JOIN tipos_delito t ON i.id_tipo_delito = t.id_tipo_delito
    WHERE t.nombre IN ('Homicidio', 'Secuestro')
    GROUP BY i.fecha, t.nombre
    ORDER BY i.fecha
    """

    df = obtener_datos_bd(query)

    if df is None or df.empty:
        return go.Figure()

    df["fecha"] = pd.to_datetime(df["fecha"])

    fig = px.line(df, x="fecha", y="total", color="tipo_delito",
                  title="Evolución Temporal de Delitos Graves",
                  labels={"total": "Total de Delitos", "fecha": "Fecha"},
                  markers=True,
                  color_discrete_sequence=["#e74c3c", "#9b59b6"])

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        height=400
    )

    return fig


def crear_grafica_distribucion():
    """
    Grafica 5: Distribucion de tipos de delitos
    """
    query = """
    SELECT 
        t.nombre as tipo_delito,
        SUM(i.cantidad) as total
    FROM incidencia_delictiva i
    JOIN tipos_delito t ON i.id_tipo_delito = t.id_tipo_delito
    GROUP BY t.nombre
    ORDER BY total DESC
    """

    df = obtener_datos_bd(query)

    if df is None or df.empty:
        return go.Figure()

    fig = px.pie(df, values="total", names="tipo_delito",
                 title="Distribucion de Tipos de Delitos (2023-2024)",
                 color_discrete_sequence=px.colors.qualitative.Set3)

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        height=400
    )

    return fig


def crear_grafica_percepcion():
    """
    Grafica 6: Relacion entre delitos y percepcion
    """
    query = """
    SELECT 
        e.nombre as estado,
        inc.anio,
        SUM(inc.cantidad) as total_delitos,
        p.percepcion_inseguridad
    FROM estados e
    JOIN incidencia_delictiva inc ON e.id_estado = inc.id_estado
    JOIN percepcion_seguridad p ON e.id_estado = p.id_estado AND inc.anio = p.anio
    JOIN tipos_delito t ON inc.id_tipo_delito = t.id_tipo_delito
    GROUP BY e.nombre, inc.anio, p.percepcion_inseguridad
    ORDER BY inc.anio, e.nombre
    """

    df = obtener_datos_bd(query)

    if df is None or df.empty:
        return go.Figure()

    fig = px.scatter(df, x="total_delitos", y="percepcion_inseguridad",
                     color="estado", size="total_delitos",
                     title="Relación entre Delitos y Percepción de Inseguridad",
                     labels={"total_delitos": "Total de Delitos",
                             "percepcion_inseguridad": "Percepción de Inseguridad (%)"},
                     color_discrete_sequence=["#3498db", "#2ecc71", "#f39c12"])

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        height=400
    )

    return fig


# Crear aplicacion Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout de la aplicacion
app.layout = html.Div([
    # Encabezado
    html.Div([
        html.H1("Análisis de Violencia y Seguridad Pública en México",
                style={"textAlign": "center", "color": "#2c3e50", "padding": "20px"}),
        html.Hr()
    ]),

    # Navegacion
    html.Div([
        dbc.Nav([
            dbc.NavLink("Inicio", href="#inicio", active="exact"),
            dbc.NavLink("Dashboard", href="#dashboard", active="exact"),
            dbc.NavLink("Análisis", href="#analisis", active="exact"),
            dbc.NavLink("Conclusiones", href="#conclusiones", active="exact"),
        ], pills=True, style={"justifyContent": "center", "marginBottom": "20px"})
    ]),

    # Seccion: Inicio
    html.Div(id="inicio", children=[
        html.Div([
            html.H2("Introducción", style={"color": "#34495e"}),
            html.Img(src="/assets/images/seguridad_mexico.jpg",
                     style={"width": "100%", "maxWidth": "800px", "display": "block",
                            "margin": "20px auto", "borderRadius": "10px"}),
            html.P([
                "La violencia y la inseguridad son dos de los problemas más graves que enfrenta México. ",
                "Este análisis examina la incidencia delictiva en tres estados clave: ",
                html.Strong("Baja California, Sinaloa y Chihuahua"),
                " durante el periodo 2023-2024."
            ], style={"fontSize": "16px", "textAlign": "justify", "maxWidth": "900px",
                      "margin": "20px auto", "lineHeight": "1.6"}),
            html.P([
                "A través de datos oficiales, buscamos entender las tendencias de diferentes tipos de delitos ",
                "(homicidios, secuestros, robos, violencia familiar y extorsión) y su impacto en la percepción ",
                "de seguridad de la población."
            ], style={"fontSize": "16px", "textAlign": "justify", "maxWidth": "900px",
                      "margin": "20px auto", "lineHeight": "1.6"}),
        ], style={"padding": "20px", "backgroundColor": "#ecf0f1", "borderRadius": "10px",
                  "margin": "20px"}),
    ]),

    html.Hr(),

    # Seccion: Dashboard
    html.Div(id="dashboard", children=[
        html.H2("Dashboard Interactivo",
                style={"textAlign": "center", "color": "#34495e", "marginTop": "30px"}),

        # Fila 1: Graficas 1 y 2
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="grafica-incidencia", figure=crear_grafica_incidencia())
            ], width=6),
            dbc.Col([
                dcc.Graph(id="grafica-tipos", figure=crear_grafica_tipos_delito())
            ], width=6),
        ], style={"marginTop": "20px"}),

        # Fila 2: Grafica 3
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="grafica-promedio", figure=crear_grafica_promedio_mensual())
            ], width=12),
        ], style={"marginTop": "20px"}),

        # Fila 3: Graficas 4 y 5
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="grafica-evolucion", figure=crear_grafica_evolucion())
            ], width=6),
            dbc.Col([
                dcc.Graph(id="grafica-distribucion", figure=crear_grafica_distribucion())
            ], width=6),
        ], style={"marginTop": "20px"}),

        # Fila 4: Grafica 6
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="grafica-percepcion", figure=crear_grafica_percepcion())
            ], width=12),
        ], style={"marginTop": "20px"}),
    ], style={"padding": "20px"}),

    html.Hr(),

    # Seccion: Analisis
    html.Div(id="analisis", children=[
        html.Div([
            html.H2("Análisis de Resultados", style={"color": "#34495e"}),

            html.H4("1. ¿Cuáles son los estados con mayor incidencia delictiva?",
                    style={"color": "#2980b9", "marginTop": "20px"}),
            html.P([
                html.Strong("Sinaloa"), " registra la mayor incidencia delictiva con un total de ",
                html.Strong("37,580 delitos"), " en el periodo 2023-2024, seguido de ",
                html.Strong("Baja California"), " con 29,853 delitos y ",
                html.Strong("Chihuahua"), " con 28,513 delitos. ",
                "Se observa un incremento en Sinaloa y Baja California en 2024, mientras que ",
                "Chihuahua muestra una ligera disminución."
            ], style={"fontSize": "15px", "textAlign": "justify", "lineHeight": "1.6"}),

            html.H4("2. ¿Qué tipos de delitos son más frecuentes?",
                    style={"color": "#2980b9", "marginTop": "20px"}),
            html.P([
                "El ", html.Strong("robo"), " es el delito más frecuente en los tres estados, ",
                "representando aproximadamente el 40% del total de delitos. ",
                "Le sigue la ", html.Strong("violencia familiar"), " con cerca del 30%. ",
                "Los delitos graves como ", html.Strong("homicidio"), " y ",
                html.Strong("secuestro"), " representan un porcentaje menor pero significativo, ",
                "especialmente en Sinaloa."
            ], style={"fontSize": "15px", "textAlign": "justify", "lineHeight": "1.6"}),

            html.H4("3. ¿Cuál es el promedio mensual y en qué meses hay mayor actividad?",
                    style={"color": "#2980b9", "marginTop": "20px"}),
            html.P([
                "El promedio mensual de delitos es de ", html.Strong("313 en Sinaloa"), ", ",
                html.Strong("249 en Baja California"), " y ", html.Strong("238 en Chihuahua"), ". ",
                "Los meses con mayor actividad delictiva son ", html.Strong("septiembre"),
                " y ", html.Strong("marzo"), ", mientras que ", html.Strong("febrero"),
                " y ", html.Strong("agosto"), " muestran los niveles más bajos."
            ], style={"fontSize": "15px", "textAlign": "justify", "lineHeight": "1.6"}),

        ], style={"padding": "20px", "backgroundColor": "#ecf0f1", "borderRadius": "10px",
                  "margin": "20px", "maxWidth": "1000px", "marginLeft": "auto",
                  "marginRight": "auto"}),
    ]),

    html.Hr(),

    # Seccion: Conclusiones
    html.Div(id="conclusiones", children=[
        html.Div([
            html.H2("Conclusiones", style={"color": "#34495e"}),
            html.Ul([
                html.Li("Sinaloa presenta los niveles más altos de incidencia delictiva, "
                        "con una tendencia al alza en 2024.",
                        style={"marginBottom": "10px", "fontSize": "15px"}),
                html.Li("El robo y la violencia familiar son los delitos más comunes, "
                        "lo que sugiere la necesidad de políticas preventivas específicas.",
                        style={"marginBottom": "10px", "fontSize": "15px"}),
                html.Li("Existe una correlación entre la percepción de inseguridad y "
                        "el número real de delitos registrados.",
                        style={"marginBottom": "10px", "fontSize": "15px"}),
                html.Li("Los delitos graves (homicidio y secuestro) muestran variaciones "
                        "estacionales que requieren atención.",
                        style={"marginBottom": "10px", "fontSize": "15px"}),
                html.Li("Es necesario fortalecer las estrategias de seguridad pública "
                        "en estos tres estados, con enfoque en prevención y atención a víctimas.",
                        style={"marginBottom": "10px", "fontSize": "15px"}),
            ], style={"lineHeight": "1.8"}),

            html.Img(src="/assets/images/mapa_mexico.jpg",
                     style={"width": "100%", "maxWidth": "600px", "display": "block",
                            "margin": "30px auto", "borderRadius": "10px"}),
        ], style={"padding": "20px", "backgroundColor": "#ecf0f1", "borderRadius": "10px",
                  "margin": "20px", "maxWidth": "1000px", "marginLeft": "auto",
                  "marginRight": "auto"}),
    ]),

    # Pie de la pagina
    html.Div([
        html.Hr(),
        html.P("Proyecto de Programación Para la Extracción de Datos | 2024",
               style={"textAlign": "center", "color": "#7f8c8d", "padding": "20px"})
    ])
], style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#ffffff"})
#quedo
if __name__ == "__main__":
    print("Iniciando dashboard...")
    print("Abre tu navegador en: http://localhost:8050")
    app.run(debug=True, port=8050)