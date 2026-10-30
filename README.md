# github_program_portfolio
Portafolio de Programas Github - Bases de Datos

Este repositorio contiene un portafolio de cinco programas desarrollados en Python como parte de las evaluaciones de la materia de Bases de Datos. Los proyectos abarcan técnicas de extracción de datos (web scraping), limpieza y transformación de datos, integración con bases de datos relacionales (MySQL) y no relacionales (MongoDB), así como análisis predictivo utilizando modelos de Machine Learning.

📂 Contenido del Repositorio

A continuación, se describen los cinco programas principales incluidos en esta entrega:

Programa Web Scraping (scraper.py)

Script asíncrono que utiliza Playwright para navegar en Pinterest, simular interacciones de usuario (scroll) y extraer imágenes de tatuajes de calaveras. Obtiene las versiones de alta resolución y guarda los metadatos estructurados (tags, URL, categoría) directamente como documentos JSON en una colección de MongoDB.

Programa de Limpieza de Base de Datos (02_limpiar_y_cargar_mysql.py)

Proceso de ETL (Extracción, Transformación y Carga) utilizando Pandas. Ingiere un archivo Excel con indicadores de pobreza de 2020, filtra exclusivamente los municipios válidos de Jalisco, estandariza nombres de columnas (a snake_case), maneja valores nulos, crea variables categóricas indicadoras (dummy variables) y genera un CSV limpio antes de volcar los datos masivamente en MySQL.

Programa de Vínculo Python a MySQL (import_mysql_movies-modificar.py)

Script directo de conexión a MySQL (usando mysql-connector-python) que demuestra la ejecución de instrucciones CRUD. En este caso, establece conexión por el puerto 3307 y ejecuta una sentencia UPDATE para corregir de manera automatizada registros específicos de títulos de películas, validando las filas afectadas.

Programa de Vínculo Python a MongoDB (chatbot_salud_mental.ipynb)

Cuaderno interactivo que lee colecciones desde MongoDB (salud_mental_db). Extrae datos cualitativos (conversaciones de un chatbot) y utiliza Procesamiento de Lenguaje Natural (PLN) con TextBlob para cuantificar la polaridad y carga emocional de los mensajes del usuario, preparándolos para un análisis estadístico.

Programa de Análisis de Datos ML (01_regresion_lineal_mysql.py)

Implementación de modelos de Machine Learning de Regresión Lineal Simple y Múltiple utilizando statsmodels y scikit-learn. Se alimenta de los datos limpios extraídos de MySQL, entrena los modelos para predecir porcentajes de pobreza en base a distintas carencias sociales, evalúa su rendimiento (R2, RMSE, MAE) y genera gráficas comparativas de tendencias y residuos con matplotlib.

🛠️ Requisitos de Entorno e Infraestructura

Para ejecutar estos programas en un entorno local, se requiere la siguiente configuración:

Lenguaje y Dependencias

Python 3.x

Librerías principales (se pueden instalar vía pip):

playwright (Requiere ejecutar playwright install para descargar los navegadores)

pymongo

mysql-connector-python

pandas

numpy

scikit-learn

statsmodels

matplotlib y seaborn

textblob

python-dotenv

Infraestructura de Bases de Datos

MongoDB Local: Servidor ejecutándose en el puerto 27017 (sin autenticación requerida en este entorno). Bases de datos utilizadas: pinterest_tattoos_db y salud_mental_db.

MySQL Local: Servidor configurado para ejecutarse en el puerto 3307.

Nota: Para los programas de MySQL y Machine Learning, se requiere un archivo .env en la raíz del proyecto con las credenciales de acceso (MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE).

Estructura de Carpetas Necesaria

01_base_original/ (Para los archivos Excel en crudo)

02_base_limpia/ (Ruta de salida para los CSV procesados)

04_codigo_machine_learning/ (Ruta de salida para las gráficas generadas)

🚀 Instrucciones de Ejecución

Clona este repositorio en tu equipo local:

git clone https://github.com/tadhz-alt/github_program_portfolio.git


Instala las dependencias necesarias:

pip install -r requirements.txt
playwright install


Configura tus credenciales de MySQL copiando el archivo .env.example a .env e ingresando tus datos.

Asegúrate de tener encendidos los servicios de MySQL (puerto 3307) y MongoDB (puerto 27017).

Ejecuta los scripts de Python de manera individual desde tu terminal, por ejemplo:

python scraper.py
python 02_limpiar_y_cargar_mysql.py
