import os
import numpy as np
import pandas as pd
import mysql.connector
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 1. Conectar a MySQL (avance_bd) y leer la tabla datos_limpios
load_dotenv()
conexion = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", 3307)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = conexion.cursor()
cursor.execute("SELECT * FROM datos_limpios ORDER BY clave_municipio ASC;")
filas = cursor.fetchall()
columnas = list(cursor.column_names)
cursor.close()
conexion.close()

df = pd.DataFrame(filas, columns=columnas)

# Convertir columnas numericas de Decimal (MySQL) a float/int para statsmodels
cols_numericas = [
    "poblacion_2020", "pobreza_porcentaje", "pobreza_personas", "carencias_promedio",
    "pobreza_extrema_porcentaje", "rezago_educativo_porcentaje", "carencia_salud_porcentaje",
    "carencia_seguridad_social_porcentaje", "carencia_vivienda_porcentaje",
    "carencia_servicios_basicos_porcentaje", "carencia_alimentacion_porcentaje",
    "ingreso_inferior_lpi_porcentaje", "ind_urbano_grande", "ind_semiurbano_medio",
    "ind_intensidad_alta", "ind_intensidad_moderada"
]
for col in cols_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

print("=== 1. LECTURA DESDE MYSQL (avance_bd.datos_limpios) ===")
print(f"Filas leidas desde MySQL: {df.shape[0]} | Columnas: {df.shape[1]}")
print(f"Promedio de 'y' (pobreza_porcentaje): {df['pobreza_porcentaje'].mean():.4f}%")
print(f"Desviacion estandar de 'y':           {df['pobreza_porcentaje'].std():.4f}%")
print(f"Minimo de 'y': {df['pobreza_porcentaje'].min():.2f}% | Maximo de 'y': {df['pobreza_porcentaje'].max():.2f}%")

# Definir variable objetivo 'y'
y = df["pobreza_porcentaje"]

# ==============================================================================
# 2. MODELO 1: REGRESION LINEAL SIMPLE
# y = pobreza_porcentaje | x = ingreso_inferior_lpi_porcentaje
# ==============================================================================
X_simple = sm.add_constant(df[["ingreso_inferior_lpi_porcentaje"]])
modelo_simple = sm.OLS(y, X_simple).fit()
y_pred_simple = modelo_simple.predict(X_simple)
residuos_simple = modelo_simple.resid

b0_s = modelo_simple.params["const"]
b1_s = modelo_simple.params["ingreso_inferior_lpi_porcentaje"]
p0_s = modelo_simple.pvalues["const"]
p1_s = modelo_simple.pvalues["ingreso_inferior_lpi_porcentaje"]
r2_s = modelo_simple.rsquared
r2_adj_s = modelo_simple.rsquared_adj
rmse_s = np.sqrt(mean_squared_error(y, y_pred_simple))
mae_s = mean_absolute_error(y, y_pred_simple)

print("\n=== 2. RESULTADOS: REGRESION LINEAL SIMPLE ===")
print("Variable objetivo (y): pobreza_porcentaje")
print("Variable independiente (x): ingreso_inferior_lpi_porcentaje")
print(f"Ecuacion: pobreza_porcentaje = {b0_s:.4f} + ({b1_s:.4f} * ingreso_inferior_lpi_porcentaje)")
print(f"Intercepto (b0): {b0_s:.4f} (valor p = {p0_s:.4e})")
print(f"Pendiente  (b1): {b1_s:.4f} (valor p = {p1_s:.4e})")
print(f"R2:              {r2_s:.4f} ({r2_s*100:.2f}%)")
print(f"R2 ajustado:     {r2_adj_s:.4f} ({r2_adj_s*100:.2f}%)")
print(f"Error cuadratico medio (RMSE): {rmse_s:.4f} | Error absoluto medio (MAE): {mae_s:.4f}")
print(f"Revision de residuos (Simple) -> Media: {residuos_simple.mean():.6f}, Min: {residuos_simple.min():.4f}, Max: {residuos_simple.max():.4f}")

# ==============================================================================
# 3. MODELO 2: REGRESION LINEAL MULTIPLE
# y = pobreza_porcentaje | x = 7 numericas + 4 indicadoras (0 y 1)
# ==============================================================================
vars_x_multiple = [
    "ingreso_inferior_lpi_porcentaje",
    "rezago_educativo_porcentaje",
    "carencia_salud_porcentaje",
    "carencia_seguridad_social_porcentaje",
    "carencia_vivienda_porcentaje",
    "carencia_servicios_basicos_porcentaje",
    "carencia_alimentacion_porcentaje",
    "ind_urbano_grande",
    "ind_semiurbano_medio",
    "ind_intensidad_alta",
    "ind_intensidad_moderada"
]

X_multiple = sm.add_constant(df[vars_x_multiple])
modelo_multiple = sm.OLS(y, X_multiple).fit()
y_pred_multiple = modelo_multiple.predict(X_multiple)
residuos_multiple = modelo_multiple.resid

r2_m = modelo_multiple.rsquared
r2_adj_m = modelo_multiple.rsquared_adj
rmse_m = np.sqrt(mean_squared_error(y, y_pred_multiple))
mae_m = mean_absolute_error(y, y_pred_multiple)

print("\n=== 3. RESULTADOS: REGRESION LINEAL MULTIPLE ===")
print(f"R2:          {r2_m:.4f} ({r2_m*100:.2f}%)")
print(f"R2 ajustado: {r2_adj_m:.4f} ({r2_adj_m*100:.2f}%)")
print(f"Estadistico F: {modelo_multiple.fvalue:.4f} (valor p global = {modelo_multiple.f_pvalue:.4e})")
print(f"RMSE:        {rmse_m:.4f} | MAE: {mae_m:.4f}")
print(f"Revision de residuos (Multiple) -> Media: {residuos_multiple.mean():.6f}, Min: {residuos_multiple.min():.4f}, Max: {residuos_multiple.max():.4f}")

print("\nTabla de Coeficientes y Valores p (Regresion Lineal Multiple):")
print(f"{'Variable':<40} | {'Coeficiente':>12} | {'Error Est.':>10} | {'Valor p':>12} | {'Significativa (p<0.05)'}")
print("-" * 98)
for nombre_var in X_multiple.columns:
    coef = modelo_multiple.params[nombre_var]
    ee = modelo_multiple.bse[nombre_var]
    pval = modelo_multiple.pvalues[nombre_var]
    sig = "SI" if pval < 0.05 else "NO"
    print(f"{nombre_var:<40} | {coef:>12.4f} | {ee:>10.4f} | {pval:>12.4e} | {sig}")

# ==============================================================================
# 4. COMPARACION ENTRE AMBOS MODELOS
# ==============================================================================
print("\n=== 4. TABLA COMPARATIVA: SIMPLE VS MULTIPLE ===")
print(f"Metrica       | Regresion Simple | Regresion Multiple | Diferencia")
print(f"R2            | {r2_s:16.4f} | {r2_m:18.4f} | {r2_m - r2_s:+.4f}")
print(f"R2 ajustado   | {r2_adj_s:16.4f} | {r2_adj_m:18.4f} | {r2_adj_m - r2_adj_s:+.4f}")
print(f"RMSE (error)  | {rmse_s:16.4f} | {rmse_m:18.4f} | {rmse_m - rmse_s:+.4f}")
print(f"MAE  (error)  | {mae_s:16.4f} | {mae_m:18.4f} | {mae_m - mae_s:+.4f}")

# ==============================================================================
# 5. GENERAR Y GUARDAR LAS GRAFICAS
# ==============================================================================
ruta_grafica_1 = os.path.join("04_codigo_machine_learning", "grafica_1_regresion_simple.png")
plt.figure(figsize=(8, 5))
plt.scatter(df["ingreso_inferior_lpi_porcentaje"], y, alpha=0.75, label="Municipios de Jalisco (125)")
x_linea = np.linspace(df["ingreso_inferior_lpi_porcentaje"].min(), df["ingreso_inferior_lpi_porcentaje"].max(), 100)
y_linea = b0_s + b1_s * x_linea
plt.plot(x_linea, y_linea, color="red", linewidth=2, label=f"Recta: y = {b0_s:.2f} + {b1_s:.2f}x (R²={r2_s:.4f})")
plt.title("Regresión Lineal Simple: Pobreza (%) vs. Ingreso Inferior a LPI (%) en Jalisco")
plt.xlabel("Población con ingreso inferior a la línea de pobreza por ingresos (%) [x]")
plt.ylabel("Población en situación de pobreza (%) [y]")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(ruta_grafica_1, dpi=150)
plt.close()

ruta_grafica_2 = os.path.join("04_codigo_machine_learning", "grafica_2_residuos_comparacion.png")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].scatter(y_pred_simple, residuos_simple, alpha=0.75)
axes[0].axhline(0, color="red", linestyle="--", linewidth=1.5)
axes[0].set_title("Residuos vs. Predicciones (Regresión Simple)")
axes[0].set_xlabel("Pobreza estimada (%)")
axes[0].set_ylabel("Residuo (Real - Estimado)")
axes[0].grid(True, linestyle="--", alpha=0.5)

axes[1].scatter(y_pred_multiple, residuos_multiple, alpha=0.75, color="green")
axes[1].axhline(0, color="red", linestyle="--", linewidth=1.5)
axes[1].set_title("Residuos vs. Predicciones (Regresión Múltiple)")
axes[1].set_xlabel("Pobreza estimada (%)")
axes[1].set_ylabel("Residuo (Real - Estimado)")
axes[1].grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(ruta_grafica_2, dpi=150)
plt.close()

print("\n=== 5. GRAFICAS GUARDADAS EXITOSAMENTE ===")
print(f"Grafica 1 guardada en: {ruta_grafica_1}")
print(f"Grafica 2 guardada en: {ruta_grafica_2}")