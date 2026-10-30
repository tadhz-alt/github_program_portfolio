import asyncio
import re
from datetime import datetime
from urllib.parse import quote
from playwright.async_api import async_playwright
from pymongo import MongoClient

# 1. Configurar conexión a MongoDB (se visualiza directo en MongoDB Compass)
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "pinterest_tattoos_db"
COLLECTION_NAME = "skull_tattoos"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Crear índice único en la URL de la imagen para evitar duplicados en la BD
collection.create_index("image_url", unique=True)


async def scrape_skull_tattoos(search_query: str, max_results: int = 15):
    """
    Navega en Pinterest, simula scroll y extrae tatuajes de calaveras guardándolos en MongoDB.
    """
    encoded_query = quote(search_query)
    url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"

    print(f"\n🔍 Buscando: '{search_query}'...")

    async with async_playwright() as p:
        # Usar un navegador real para evitar detección rápida por bot
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            inserted_count = 0
            scroll_attempts = 0

            while inserted_count < max_results and scroll_attempts < 10:
                # Extraer imágenes de las tarjetas de Pinterest
                img_elements = await page.query_selector_all('img[src*="i.pinimg.com"]')

                for img in img_elements:
                    if inserted_count >= max_results:
                        break

                    src = await img.get_attribute("src")
                    alt_text = await img.get_attribute("alt") or "Tatuaje de Calavera"

                    if src and ("236x" in src or "474x" in src or "736x" in src):
                        # Convertir miniatura a la URL de máxima calidad en Pinterest
                        high_res_url = re.sub(r'/(236x|474x|736x)/', '/originals/', src)

                        # Generar etiquetas automáticamente a partir del título/alt
                        tags = list(set([
                            tag.lower() for tag in re.findall(r'\b\w+\b', alt_text)
                            if len(tag) > 3 and tag.lower() not in ["tattoo", "tatuaje", "para", "como", "esta"]
                        ]))
                        tags.extend(["calavera", "tattoo", search_query.lower()])

                        # Estructura del documento JSON para MongoDB
                        tattoo_doc = {
                            "title": alt_text,
                            "category": "Skull Tattoos",
                            "search_term": search_query,
                            "image_url": high_res_url,
                            "thumbnail_url": src,
                            "tags": list(set(tags)),
                            "source": "Pinterest",
                            "created_at": datetime.utcnow()
                        }

                        # Intentar guardar en la Base de Datos
                        try:
                            collection.insert_one(tattoo_doc)
                            inserted_count += 1
                            print(f" [{inserted_count}/{max_results}] Guardado: {alt_text[:40]}...")
                        except Exception:
                            # Ignora si ya existía la URL (gracias al índice único)
                            pass

                # Hacer scroll suave para cargar más imágenes en pantalla
                await page.evaluate("window.scrollBy(0, 1200)")
                await page.wait_for_timeout(2000)
                scroll_attempts += 1

            print(f" Finalizada la búsqueda de '{search_query}'. Nuevos registros: {inserted_count}")

        except Exception as e:
            print(f" Error en el proceso de scraping: {e}")
        finally:
            await browser.close()


async def main():
    # Lista de búsquedas específicas para recopilar diferentes estilos de calaveras
    busquedas_calaveras = [
        "tatuajes calaveras de azucar",
        "tatuajes calaveras realistas",
        "tatuaje calavera con rosas",
        "skull tattoo design blackwork"
    ]

    for busqueda in busquedas_calaveras:
        await scrape_skull_tattoos(search_query=busqueda, max_results=10)


if __name__ == "__main__":
    asyncio.run(main())