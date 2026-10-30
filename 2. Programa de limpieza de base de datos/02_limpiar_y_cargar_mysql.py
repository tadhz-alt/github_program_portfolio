import os
import unicodedata
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

def quitar_acentos(texto):
    if pd.isna(texto):
        return ""
    texto_limpio = str(texto).replace("\n", " ").strip()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto_limpio)
        if unicodedata.category(c) != "Mn"
    ).lower()

# 1. Leer el archivo original y trabajar sobre una copia
ruta_original = os.path.join("01_base_original", "Concentrado_indicadores_de_pobreza_2020.xlsx")
df_original = pd.read_excel(ruta_original, sheet_name="Concentrado municipal", header=None)
df_copia = df_original.copy()

fila_4 = df_copia.iloc[4].ffill()
fila_5 = df_copia.iloc[5]
encabezados = {}
for idx in range(df_copia.shape[1]):
    sup = str(fila_4.iloc[idx]).replace("\n", " ").strip() if pd.notna(fila_4.iloc[idx]) else ""
    inf = str(fila_5.iloc[idx]).replace("\n", " ").strip() if pd.notna(fila_5.iloc[idx]) else ""
    encabezados[idx] = f"{sup} -> {inf}" if (sup and inf) else (sup or inf or "vacia")

def buscar_col(grupo, sub="porcentaje 2020"):
    for idx, nom in encabezados.items():
        n_norm = quitar_acentos(nom)
        if grupo in n_norm and sub in n_norm:
            return idx
    raise ValueError(f"No se encontro: {grupo} / {sub}")

# 2. Seleccionar y renombrar columnas con nombres limpios en snake_case
columnas_indices = {
    "clave_entidad": 1,
    "entidad_federativa": 2,
    "clave_municipio": 3,
    "municipio": 4,
    "poblacion_2020": 7,
    "pobreza_porcentaje": 10,
    "pobreza_personas": 13,
    "carencias_promedio": buscar_col("pobreza ->", "carencias promedio 2020"),
    "pobreza_extrema_porcentaje": buscar_col("pobreza extrema", "porcentaje 2020"),
    "rezago_educativo_porcentaje": buscar_col("rezago educativo", "porcentaje 2020"),
    "carencia_salud_porcentaje": buscar_col("servicios de salud", "porcentaje 2020"),
    "carencia_seguridad_social_porcentaje": buscar_col("seguridad social", "porcentaje 2020"),
    "carencia_vivienda_porcentaje": buscar_col("calidad y espacios", "porcentaje 2020"),
    "carencia_servicios_basicos_porcentaje": buscar_col("servicios basicos", "porcentaje 2020"),
    "carencia_alimentacion_porcentaje": buscar_col("alimentacion", "porcentaje 2020"),
    "ingreso_inferior_lpi_porcentaje": buscar_col("linea de pobreza por ingresos", "porcentaje 2020"),
}

df_limpio = df_copia.iloc[:, list(columnas_indices.values())].copy()
df_limpio.columns = list(columnas_indices.keys())

# 3. Filtrar solo filas de municipios validos (5 digitos) y del estado de Jalisco ('14')
df_limpio["clave_municipio"] = df_limpio["clave_municipio"].astype(str).str.strip().str.zfill(5)
df_limpio["clave_entidad"] = df_limpio["clave_entidad"].astype(str).str.strip().str.zfill(2)

es_municipio_valido = df_limpio["clave_municipio"].str.fullmatch(r"\d{5}")
df_limpio = df_limpio[es_municipio_valido & (df_limpio["clave_entidad"] == "14")].copy()

# 4. Limpiar textos y convertir columnas numericas a tipos exactos (enteros y decimales redondeados)
df_limpio["entidad_federativa"] = df_limpio["entidad_federativa"].astype(str).str.strip()
df_limpio["municipio"] = df_limpio["municipio"].astype(str).str.strip()

cols_enteras = ["poblacion_2020", "pobreza_personas"]
cols_decimales = [
    "pobreza_porcentaje",
    "carencias_promedio",
    "pobreza_extrema_porcentaje",
    "rezago_educativo_porcentaje",
    "carencia_salud_porcentaje",
    "carencia_seguridad_social_porcentaje",
    "carencia_vivienda_porcentaje",
    "carencia_servicios_basicos_porcentaje",
    "carencia_alimentacion_porcentaje",
    "ingreso_inferior_lpi_porcentaje",
]

for col in cols_enteras:
    df_limpio[col] = pd.to_numeric(df_limpio[col], errors="coerce")

for col in cols_decimales:
    df_limpio[col] = pd.to_numeric(df_limpio[col], errors="coerce").round(2)

# Eliminar cualquier fila con valores vacios o duplicados en clave_municipio
df_limpio = df_limpio.dropna().drop_duplicates(subset=["clave_municipio"]).copy()
for col in cols_enteras:
    df_limpio[col] = df_limpio[col].astype(int)

# 5. Crear 2 variables categoricas "x" y sus variables indicadoras (0 y 1)
def clasificar_poblacion(pob):
    if pob >= 100000:
        return "Urbano_Grande"
    elif pob >= 15000:
        return "Semiurbano_Medio"
    else:
        return "Rural_Pequeno"

def clasificar_intensidad_carencias(prom):
    if prom >= 2.30:
        return "Intensidad_Alta"
    elif prom >= 1.90:
        return "Intensidad_Moderada"
    else:
        return "Intensidad_Baja"

df_limpio["tipo_municipio_poblacion"] = df_limpio["poblacion_2020"].apply(clasificar_poblacion)
df_limpio["nivel_intensidad_carencias"] = df_limpio["carencias_promedio"].apply(clasificar_intensidad_carencias)

# Variables indicadoras (0 y 1), dejando Rural_Pequeno e Intensidad_Baja como categorias base (0, 0)
df_limpio["ind_urbano_grande"] = (df_limpio["tipo_municipio_poblacion"] == "Urbano_Grande").astype(int)
df_limpio["ind_semiurbano_medio"] = (df_limpio["tipo_municipio_poblacion"] == "Semiurbano_Medio").astype(int)
df_limpio["ind_intensidad_alta"] = (df_limpio["nivel_intensidad_carencias"] == "Intensidad_Alta").astype(int)
df_limpio["ind_intensidad_moderada"] = (df_limpio["nivel_intensidad_carencias"] == "Intensidad_Moderada").astype(int)

# Ordenar columnas exactamente como en la tabla datos_limpios de MySQL
orden_columnas = [
    "clave_municipio", "clave_entidad", "entidad_federativa", "municipio",
    "poblacion_2020", "pobreza_porcentaje", "pobreza_personas", "carencias_promedio",
    "pobreza_extrema_porcentaje", "rezago_educativo_porcentaje", "carencia_salud_porcentaje",
    "carencia_seguridad_social_porcentaje", "carencia_vivienda_porcentaje",
    "carencia_servicios_basicos_porcentaje", "carencia_alimentacion_porcentaje",
    "ingreso_inferior_lpi_porcentaje", "tipo_municipio_poblacion", "nivel_intensidad_carencias",
    "ind_urbano_grande", "ind_semiurbano_medio", "ind_intensidad_alta", "ind_intensidad_moderada"
]
df_limpio = df_limpio[orden_columnas].sort_values("clave_municipio").reset_index(drop=True)

# 6. Guardar archivo CSV en la carpeta 02_base_limpia
ruta_csv_limpio = os.path.join("02_base_limpia", "pobreza_municipal_jalisco_2020_limpia.csv")
df_limpio.to_csv(ruta_csv_limpio, index=False, encoding="utf-8")

print("=== 1. COMPARACION ANTES Y DESPUES DE LA LIMPIEZA ===")
print(f"Filas antes (archivo original completo): {df_original.shape[0]} | Columnas antes: {df_original.shape[1]}")
print(f"Filas despues (Jalisco limpio):          {df_limpio.shape[0]}  | Columnas despues: {df_limpio.shape[1]}")
print(f"Total de valores vacios en la base limpia: {df_limpio.isna().sum().sum()}")
print(f"Archivo CSV guardado en: {ruta_csv_limpio}")

print("\n=== 2. ENCABEZADOS Y TIPOS DE DATOS DE LA BASE LIMPIA ===")
for i, col in enumerate(df_limpio.columns, 1):
    print(f"{i:02d}. {col} ({df_limpio[col].dtype})")

print("\n=== 3. CONTEO DE MUNICIPIOS POR CATEGORIA (VARIABLES CATEGORICAS X) ===")
print("Distribución de tipo_municipio_poblacion:")
print(df_limpio["tipo_municipio_poblacion"].value_counts().to_string())
print("\nDistribución de nivel_intensidad_carencias:")
print(df_limpio["nivel_intensidad_carencias"].value_counts().to_string())

# 7. Cargar la base limpia en MySQL (tabla datos_limpios)
load_dotenv()
conexion = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", 3307)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)
cursor = conexion.cursor()
cursor.execute("TRUNCATE TABLE datos_limpios;")

placeholders = ", ".join(["%s"] * len(orden_columnas))
sql_insert = f"INSERT INTO datos_limpios ({', '.join(orden_columnas)}) VALUES ({placeholders})"

registros = [tuple(fila) for fila in df_limpio.to_numpy()]
cursor.executemany(sql_insert, registros)
conexion.commit()

cursor.execute("SELECT COUNT(*) FROM datos_limpios;")
conteo_limpios = cursor.fetchone()[0]
print(f"\n=== 4. CARGA EN MYSQL COMPLETADA ===")
print(f"Filas insertadas en avance_bd.datos_limpios: {conteo_limpios}")
cursor.close()
conexion.close()