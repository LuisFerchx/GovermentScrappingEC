#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract table data from web URL with pagination support and export to Excel
Enhanced version that includes código de necesidad de contratación extraction
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Leer clave desde variable de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODELO_IA = None
try:
    if not GEMINI_API_KEY or "TU_CLAVE" in GEMINI_API_KEY:
        raise ValueError("La clave de API de Gemini no ha sido configurada.")
    genai.configure(api_key=GEMINI_API_KEY)
    MODELO_IA = genai.GenerativeModel('gemini-2.5-flash')
    print("  > Modelo de IA (Gemini) configurado correctamente.")
except Exception as e:
    print(f"  ! Advertencia: {e}")
    print("  ! El análisis con IA estará deshabilitado.")

def setup_driver():
    """
    Setup Chrome driver with options
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_codigo_from_html_content(html_content):
    """
    Extrae el código de necesidad de contratación del contenido HTML
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar el texto "Código Necesidad de Contratación:"
        codigo_element = soup.find('strong', string=re.compile(r'Código Necesidad de Contratación'))
        
        if codigo_element:
            # Obtener el texto del elemento padre (que contiene el código)
            parent_text = codigo_element.parent.get_text(strip=True)
            
            # Extraer el código usando regex - buscar el patrón NIC-XXXXX-XXXX-XXXXX
            codigo_match = re.search(r'Código Necesidad de Contratación:\s*(NIC-[0-9]+-[0-9]+-[0-9]+)', parent_text)
            
            if codigo_match:
                codigo = codigo_match.group(1).strip()
                print(f"    [OK] Código encontrado: {codigo}")
                return codigo
            else:
                print(f"    [ERROR] No se pudo extraer el código del texto")
                print(f"    [DEBUG] Texto encontrado: {parent_text[:100]}...")
                return None
        else:
            print(f"    [ERROR] No se encontró el elemento con 'Código Necesidad de Contratación'")
            return None
            
    except Exception as e:
        print(f"    [ERROR] Error extrayendo código: {e}")
        return None

def get_total_pages(driver):
    """
    Get the total number of pages from pagination
    """
    try:
        # Wait for pagination to load
        wait = WebDriverWait(driver, 10)
        pagination = wait.until(EC.presence_of_element_located((By.ID, "table_id_paginate")))
        
        # Find all pagination buttons
        page_buttons = pagination.find_elements(By.CSS_SELECTOR, "a.paginate_button")
        
        # Get the last page number
        max_page = 1
        for button in page_buttons:
            try:
                page_num = int(button.text)
                if page_num > max_page:
                    max_page = page_num
            except ValueError:
                continue
        
        print(f"Total pages found: {max_page}")
        return max_page
        
    except Exception as e:
        print(f"Error getting total pages: {e}")
        return 1

def extract_detail_page_data(driver, detail_url):
    """
    Extract data from detail page (product table) and código de contratación
    """
    try:
        print(f"    [INFO] Extrayendo datos de página de detalle: {detail_url}")
        
        # Handle relative URLs
        if detail_url.startswith('../'):
            # Convert relative URL to absolute
            base_url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/"
            full_url = base_url + detail_url[3:]  # Remove '../' prefix
        elif detail_url.startswith('/'):
            full_url = "https://www.compraspublicas.gob.ec" + detail_url
        else:
            full_url = detail_url
        
        # Navigate to detail page
        driver.get(full_url)
        time.sleep(3)  # Wait for page to load
        
        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        
        # Wait for page to load completely
        time.sleep(3)
        
        # Get page source and parse with BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract código de necesidad de contratación
        codigo_contratacion = extract_codigo_from_html_content(html_content)
        
        # Look for the first table (which contains the product information)
        tables = soup.find_all('table')
        
        if not tables:
            print(f"    [ERROR] No se encontraron tablas en: {detail_url}")
            return [], codigo_contratacion
        
        # Use the first table (which contains product data)
        product_table = tables[0]
        
        # Extract table data
        product_data = []
        rows = product_table.find_all('tr')
        
        # Skip header row and process data rows
        for row in rows[1:]:  # Skip first row (headers)
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 5:  # Expected: No., CPC, Descripción, Unidad, Cantidad
                row_data = [cell.get_text(strip=True) for cell in cells]
                product_data.append(row_data)
        
        print(f"    [OK] Extraídos {len(product_data)} productos de la página de detalle")
        return product_data, codigo_contratacion
        
    except Exception as e:
        print(f"    [ERROR] Error extrayendo datos de página de detalle: {e}")
        return [], None

def extract_table_data_from_page(driver, page_num, extract_details=False):
    """
    Extract table data from current page
    """
    try:
        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "table_id")))
        
        # Get page source
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the table
        table = soup.find('table', {'id': 'table_id'})
        
        if not table:
            print(f"No table found on page {page_num}")
            return None
        
        # Extract headers (only on first page)
        headers = []
        if page_num == 1:
            header_row = table.find('thead').find('tr')
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
            print(f"Headers: {headers}")
        
        # Extract data rows
        data_rows = []
        tbody = table.find('tbody')
        
        if tbody:
            for row in tbody.find_all('tr'):
                row_data = []
                cells = row.find_all('td')
                detail_url = None
                
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    # Handle special cases for certain columns
                    if i == 7:  # Entidad Contratante column
                        link = cell.find('a')
                        if link:
                            cell_text = link.get_text(strip=True)
                            detail_url = link.get('href')
                    
                    row_data.append(cell_text)
                
                # Only add row if it has the expected number of columns
                if len(row_data) == 10:  # Expected number of columns
                    # Add detail URL to the row for later processing
                    if detail_url:
                        row_data.append(detail_url)  # Add detail URL as last column
                    else:
                        row_data.append("")  # No detail URL
                    
                    data_rows.append(row_data)
        
        print(f"Page {page_num}: Extracted {len(data_rows)} rows")
        return data_rows
        
    except Exception as e:
        print(f"Error extracting data from page {page_num}: {e}")
        return None

def navigate_to_page(driver, page_num):
    """
    Navigate to specific page number
    """
    try:
        if page_num == 1:
            return True  # Already on first page
        
        # Find the pagination button for the specific page
        wait = WebDriverWait(driver, 10)
        pagination = wait.until(EC.presence_of_element_located((By.ID, "table_id_paginate")))
        
        # Look for the specific page button
        page_button = None
        try:
            page_button = pagination.find_element(By.CSS_SELECTOR, f"a[data-dt-idx='{page_num}']")
        except:
            # Try alternative selector
            page_buttons = pagination.find_elements(By.CSS_SELECTOR, "a.paginate_button")
            for button in page_buttons:
                if button.text == str(page_num):
                    page_button = button
                    break
        
        if page_button:
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView(true);", page_button)
            time.sleep(1)
            page_button.click()
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for table to update
            wait.until(EC.presence_of_element_located((By.ID, "table_id")))
            
            print(f"Successfully navigated to page {page_num}")
            return True
        else:
            print(f"Could not find page button for page {page_num}")
            return False
            
    except Exception as e:
        print(f"Error navigating to page {page_num}: {e}")
        return False

def extract_all_pages_data(url, max_pages=None):
    """
    Extract main data from all pages (without details)
    """
    driver = None
    all_data = []
    headers = []
    
    try:
        print(f"Starting extraction from: {url}")
        driver = setup_driver()
        driver.get(url)
        
        # Wait for initial page to load
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "table_id")))
        time.sleep(5)  # Additional wait for data to load
        
        # Get total pages
        total_pages = get_total_pages(driver)
        
        # Limit pages if specified
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            print(f"Limited to {max_pages} pages")
        
        print(f"Extracting data from {total_pages} pages...")
        
        # Extract data from each page
        for page_num in range(1, total_pages + 1):
            print(f"\n--- Processing Page {page_num}/{total_pages} ---")
            
            # Navigate to page (if not first page)
            if page_num > 1:
                if not navigate_to_page(driver, page_num):
                    print(f"Failed to navigate to page {page_num}, skipping...")
                    continue
            
            # Extract data from current page (without details)
            page_data = extract_table_data_from_page(driver, page_num, extract_details=False)
            
            if page_data:
                all_data.extend(page_data)
                
                # Get headers from first page
                if page_num == 1 and page_data:
                    # Extract headers from first row of first page
                    if all_data:
                        headers = [
                            'Tipo de Necesidad',
                            'Código Necesidad de Contratación',
                            'Fecha de Publicación',
                            'Provincia - Cantón',
                            'Descripción del Objeto de compra',
                            'Estado de la Necesidad',
                            'Fecha límite para la entrega de proformas',
                            'Entidad Contratante',
                            'Dirección de Entrega',
                            'Contacto',
                            'URL_Detalle'
                        ]
            else:
                print(f"No data extracted from page {page_num}")
        
        print(f"\nTotal records extracted: {len(all_data)}")
        
        # Create DataFrame
        if all_data and headers:
            df = pd.DataFrame(all_data, columns=headers)
            return df
        else:
            print("No data extracted from any page")
            return None
            
    except Exception as e:
        print(f"Error in extraction process: {e}")
        return None
    finally:
        if driver:
            driver.quit()

# Keywords for filtering
KEYWORDS_HUREONSYS = {
    "Desarrollo Software": [
        "software",
        "sistema informático",
        "plataforma digital",
        "sistema de gestión",
        "aplicativo",
        "implementación de software",
        "mantenimiento de software",
        "firma electrónica"
    ],
    "Ciberseguridad": [
        "ciberseguridad",
        "seguridad informática",
        "análisis de vulnerabilidades",
        "pentesting",
        "seguridad de la información",
        "consultoría en seguridad",
        "ISO 27001"
    ],
    "Datos & IA": [
        "datos",
        "análisis de datos",
        "analítica",
        "procesamiento de datos",
        "ETL",
        "inteligencia de negocios",
        "business intelligence",
        "visualización de datos",
        "modelado de datos",
        "análisis estadístico",
        "estadística",
        "modelado predictivo",
        "inteligencia artificial"
    ],
    "Consultoría y Soporte TI": [
        "consultoría tecnológica",
        "soporte técnico",
        "mesa de ayuda",
        "interoperabilidad",
        "servicios TI"
    ]
}

def analizar_con_gemini(description, modelo):
    if not modelo: return {}
    # --- PROMPT ACTUALIZADO ---
    # Ahora le pedimos a la IA que determine y devuelva la prioridad.
    prompt = f"""
    Eres un Asesor Senior en Contratación Pública Ecuatoriana. Analiza el siguiente contrato del SERCOP para tu cliente HureonSys (experto en Desarrollo de Software, Ciberseguridad, y Análisis de Datos con Estadística) y determina su relevancia.
    Contrato: "{description}"
    Proporciona tu análisis estrictamente en el siguiente formato JSON:
    {{
      "puntuacion_relevancia": [Un número del 0 al 10],
      "prioridad": "[Asigna 'Alta' si la puntuación es >= 7, 'Media' si está entre 4 y 6, y 'Baja' si es <= 3]",
      "motivo": "[Explicación concisa de la puntuación]",
      "accion_recomendada": "[Postular Inmediatamente, Analizar Pliego con Detalle, Baja Prioridad, Descartar]"
    }}
    """
    try:
        response = modelo.generate_content(prompt, request_options={"timeout": 100})
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"    ! Error al analizar con Gemini: {e}")
        return {"puntuacion_relevancia": 0, "prioridad": "Revisar Manualmente", "motivo": str(e), "accion_recomendada": "Revisar Manualmente"}


def filter_data_by_keywords(df):
    """
    Filter data based on keywords in 'Descripción del Objeto de compra' column
    """
    if df is None or df.empty:
        return df
    
    # Get the description column (index 4)
    descripcion_col = df.columns[4]  # 'Descripción del Objeto de compra'
    
    # Create a list to store filtered data
    filtered_rows = []
    matched_categories = []
    
    print(f"\n[INFO] Filtrando datos por palabras clave en: '{descripcion_col}'")
    print("=" * 60)
    
    for idx, row in df.iterrows():
        descripcion = str(row[descripcion_col]).lower()
        matched_keywords = []
        matched_category = None
        
        # Check each category and its keywords
        for category, keywords in KEYWORDS_HUREONSYS.items():
            for keyword in keywords:
                if keyword.lower() in descripcion:
                    matched_keywords.append(keyword)
                    matched_category = category
                    break  # Found a match in this category, move to next row
            if matched_category:  # If we found a match, break out of category loop
                break
        
        # If we found a match, add to filtered data
        if matched_category:
            # Add category and matched keywords to the row
            row_data = row.tolist()
            row_data.extend([matched_category, ', '.join(matched_keywords)])
            filtered_rows.append(row_data)
            matched_categories.append(matched_category)
    
    if filtered_rows:
        # Create new DataFrame with filtered data
        new_columns = list(df.columns) + ['Categoría', 'Palabras Clave Encontradas']
        filtered_df = pd.DataFrame(filtered_rows, columns=new_columns)
        
        # Print summary
        print(f"[OK] Registros encontrados: {len(filtered_df)}")
        print("\n[INFO] Resumen por categoría:")
        category_counts = pd.Series(matched_categories).value_counts()
        for category, count in category_counts.items():
            print(f"   • {category}: {count} registros")
        
        return filtered_df
    else:
        print("[ERROR] No se encontraron registros que coincidan con las palabras clave")
        return pd.DataFrame()

def clean_data(df):
    """
    Clean and format the data
    """
    if df is None or df.empty:
        return df
    
    # Remove any empty rows
    df = df.dropna(how='all')
    
    # Clean up text data
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', '')
    
    return df

def export_to_excel(df, output_file):
    """
    Export DataFrame to Excel file
    """
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Necesidades de Contratación', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Necesidades de Contratación']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Data successfully exported to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False

def extract_details_for_filtered_records(df_filtered, base_url):
    """
    Extract product details only for filtered records with código de contratación
    """
    if df_filtered.empty:
        print("[ERROR] No hay registros filtrados para extraer detalles")
        return df_filtered
    
    print(f"\n[INFO] EXTRAYENDO DETALLES DE PRODUCTOS PARA REGISTROS FILTRADOS")
    print("=" * 70)
    print(f"[INFO] Registros filtrados a procesar: {len(df_filtered)}")
    
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            print("[ERROR] No se pudo configurar el driver")
            return df_filtered
        
        # Add column for product details
        df_filtered = df_filtered.copy()
        df_filtered['Detalles_Productos'] = [[] for _ in range(len(df_filtered))]
        df_filtered['Codigo_Necesidad_Contratacion'] = [None for _ in range(len(df_filtered))]
        
        # Check if we have detail URLs in the DataFrame
        detail_url_column = None
        for col in df_filtered.columns:
            if 'url' in col.lower() or 'href' in col.lower():
                detail_url_column = col
                break
        
        if detail_url_column is None:
            print("[ERROR] No se encontró columna con URLs de detalle")
            print("   Columnas disponibles:", list(df_filtered.columns))
            return df_filtered
        
        print(f"[OK] Usando columna de URLs: {detail_url_column}")
        
        # Process each filtered record
        for idx, row in df_filtered.iterrows():
            print(f"\n[INFO] Procesando registro {idx + 1}/{len(df_filtered)}")
            print(f"   Entidad: {row.get('Entidad Contratante', 'N/A')}")
            print(f"   Descripción: {row.get('Descripción del Objeto de compra', 'N/A')[:80]}...")
            
            # Get detail URL from the row
            detail_url = row.get(detail_url_column, "")
            
            if detail_url and detail_url.strip():
                print(f"   [INFO] URL de detalle: {detail_url}")
                try:
                    # Extract product details from the detail page
                    detail_data, codigo_contratacion = extract_detail_page_data(driver, detail_url)
                    if detail_data:
                        df_filtered.at[idx, 'Detalles_Productos'] = detail_data
                        print(f"   [OK] Extraídos {len(detail_data)} productos")
                    else:
                        print(f"   [ERROR] No se pudieron extraer productos")
                        df_filtered.at[idx, 'Detalles_Productos'] = []
                    
                    if codigo_contratacion:
                        df_filtered.at[idx, 'Codigo_Necesidad_Contratacion'] = codigo_contratacion
                        print(f"   [OK] Código de contratación: {codigo_contratacion}")
                    else:
                        print(f"   [ERROR] No se pudo extraer código de contratación")
                        df_filtered.at[idx, 'Codigo_Necesidad_Contratacion'] = None
                        
                except Exception as e:
                    print(f"   [ERROR] Error extrayendo detalles: {e}")
                    df_filtered.at[idx, 'Detalles_Productos'] = []
                    df_filtered.at[idx, 'Codigo_Necesidad_Contratacion'] = None
            else:
                print(f"   [INFO] No hay URL de detalle disponible")
                df_filtered.at[idx, 'Detalles_Productos'] = []
                df_filtered.at[idx, 'Codigo_Necesidad_Contratacion'] = None
        
        print(f"\n[OK] Procesamiento de detalles completado")
        return df_filtered
        
    except Exception as e:
        print(f"[ERROR] Error extrayendo detalles: {e}")
        return df_filtered
    finally:
        if driver:
            driver.quit()

def process_product_details(df):
    """
    Process and display product details information
    """
    if 'Detalles_Productos' not in df.columns:
        print("[ERROR] No se encontraron detalles de productos en el DataFrame")
        return df
    
    print(f"\n[INFO] PROCESANDO DETALLES DE PRODUCTOS")
    print("=" * 50)
    
    # Count records with product details
    records_with_details = df['Detalles_Productos'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False).sum()
    print(f"[INFO] Registros con detalles de productos: {records_with_details}/{len(df)}")
    
    # Show sample product details
    sample_records = df[df['Detalles_Productos'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)].head(3)
    
    for idx, row in sample_records.iterrows():
        print(f"\n[INFO] Registro {idx + 1}:")
        print(f"   Entidad: {row.get('Entidad Contratante', 'N/A')}")
        print(f"   Descripción: {row.get('Descripción del Objeto de compra', 'N/A')[:100]}...")
        print(f"   Código: {row.get('Codigo_Necesidad_Contratacion', 'N/A')}")
        
        if isinstance(row['Detalles_Productos'], list) and len(row['Detalles_Productos']) > 0:
            print(f"   Productos encontrados: {len(row['Detalles_Productos'])}")
            for i, product in enumerate(row['Detalles_Productos'][:3]):  # Show first 3 products
                if len(product) >= 5:
                    print(f"     {i+1}. {product[2][:50]}... (Cantidad: {product[4]})")
        else:
            print("   [ERROR] No se encontraron productos")
    
    return df

def display_dataframe_info(df, df_name="DataFrame"):
    """
    Display comprehensive information about a DataFrame
    """
    if df is None or df.empty:
        print(f"[ERROR] {df_name} está vacío o no disponible")
        return
    
    print(f"\n[INFO] INFORMACIÓN DEL {df_name.upper()}")
    print("=" * 60)
    print(f"[INFO] Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"[INFO] Columnas: {list(df.columns)}")
    print(f"[INFO] Tipos de datos:")
    for col, dtype in df.dtypes.items():
        print(f"   • {col}: {dtype}")
    
    print(f"\n[INFO] Estadísticas básicas:")
    print(f"   • Registros no nulos por columna:")
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        print(f"     - {col}: {non_null_count}/{len(df)} ({non_null_count/len(df)*100:.1f}%)")
    
    print(f"\n[INFO] Primeras 5 filas:")
    print(df.head().to_string())
    
    if len(df) > 5:
        print(f"\n[INFO] Últimas 3 filas:")
        print(df.tail(3).to_string())

def main():
    """
    Main function
    """
    url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/FrmNCOListado.cpe"
    output_file = "necesidades_contratacion_filtrado_TI_con_codigo.xlsx"
    
    print("=== EXTRACTOR DE DATOS DE CONTRATACIÓN PÚBLICA CON PAGINACIÓN Y CÓDIGO ===\n")
    
    max_pages = int(os.getenv("MAX_PAGES", ""))
    
    # STEP 1: Extract main data from all pages (without details)
    print("[PASO 1] Extrayendo datos principales de todas las páginas...")
    df = extract_all_pages_data(url, max_pages=max_pages)  # Set max_pages=5 for testing
    
    if df is None or df.empty:
        print("[ERROR] No se pudieron extraer datos de la página web")
        return None
    
    print(f"\n[INFO] Datos principales extraídos: {len(df)} filas, {len(df.columns)} columnas")
    print(f"[INFO] Columnas: {list(df.columns)}")
    
    # Clean data
    df = clean_data(df)
    
    # Display information about the original DataFrame
    display_dataframe_info(df, "DataFrame Original")
    
    # STEP 2: Filter data by keywords
    print("\n[PASO 2] Filtrando datos por palabras clave...")
    df_filtered = filter_data_by_keywords(df)
    
    if df_filtered.empty:
        print("\n[ERROR] No se encontraron registros que coincidan con los criterios de filtrado")
        return df  # Return original DataFrame even if filtered is empty
    
    # Display information about the filtered DataFrame
    display_dataframe_info(df_filtered, "DataFrame Filtrado")
    
    # STEP 3: Extract product details only for filtered records
    print("\n[PASO 3] Extrayendo detalles de productos solo para registros filtrados...")
    df_with_details = extract_details_for_filtered_records(df_filtered, url)
    
    # Process and display product details
    if 'Detalles_Productos' in df_with_details.columns:
        df_with_details = process_product_details(df_with_details)
        
        # Create a separate DataFrame for product details
        print(f"\n[INFO] CREANDO DATAFRAME DE DETALLES DE PRODUCTOS")
        print("=" * 60)
        
        product_details_list = []
        for idx, row in df_with_details.iterrows():
            if isinstance(row['Detalles_Productos'], list) and len(row['Detalles_Productos']) > 0:
                for product in row['Detalles_Productos']:
                    if len(product) >= 5:  # Ensure we have all required columns
                        product_details_list.append({
                            'Registro_ID': idx,
                            'Entidad_Contratante': row.get('Entidad Contratante', 'N/A'),
                            'Descripcion_Objeto': row.get('Descripción del Objeto de compra', 'N/A'),
                            'Codigo_Necesidad_Contratacion': row.get('Codigo_Necesidad_Contratacion', 'N/A'),
                            'No': product[0] if len(product) > 0 else '',
                            'CPC': product[1] if len(product) > 1 else '',
                            'Descripcion_Producto': product[2] if len(product) > 2 else '',
                            'Unidad': product[3] if len(product) > 3 else '',
                            'Cantidad': product[4] if len(product) > 4 else ''
                        })
        
        # Create DataFrame for product details
        if product_details_list:
            df_product_details = pd.DataFrame(product_details_list)
            print(f"[OK] DataFrame de detalles de productos creado: {len(df_product_details)} productos")
            print(f"[INFO] Columnas: {list(df_product_details.columns)}")
            
            # Display the product details DataFrame
            print(f"\n[INFO] DATAFRAME DE DETALLES DE PRODUCTOS:")
            print("=" * 80)
            print(df_product_details.to_string(index=False))
            
            # Save product details to separate Excel file
            product_details_file = "detalles_productos_con_codigo.xlsx"
            df_product_details.to_excel(product_details_file, index=False)
            print(f"\n[OK] Detalles de productos guardados en: {product_details_file}")
            
            # Analizando con Gemini
            df_consolidado = pd.DataFrame()
            if MODELO_IA:
                print(f"\n--- INICIANDO ANÁLISIS CON GEMINI ---")
                for index, row in df_product_details.iterrows():
                    if pd.isna(row.get('Puntuación IA')):
                        print(f"  > Analizando OCID: {row.get('CPC', 'N/A')}...")
                        resultado_ia = analizar_con_gemini(row.get('Descripcion_Producto'), MODELO_IA)
                        # --- LÓGICA ACTUALIZADA ---
                        # Ahora llenamos también la prioridad con la respuesta de la IA
                        df_consolidado.loc[index, 'Puntuación IA'] = resultado_ia.get('puntuacion_relevancia')
                        df_consolidado.loc[index, 'Prioridad'] = resultado_ia.get('prioridad') # <--- NUEVO
                        df_consolidado.loc[index, 'Motivo IA'] = resultado_ia.get('motivo')
                        df_consolidado.loc[index, 'Acción IA'] = resultado_ia.get('accion_recomendada')
                        df_consolidado.loc[index, 'Codigo Necesidad de Contratacion'] = row.get('Codigo_Necesidad_Contratacion')
                        df_consolidado.loc[index, 'Entidad Contratante'] = row.get('Entidad_Contratante')
                        time.sleep(4.1)
            
                print(f"[INFO] Columnas del Analisis: {list(df_consolidado.columns)}")
                
                # Display the product details DataFrame
                print(df_consolidado.to_string(index=False))
                
                # Export df_consolidado to Excel
                consolidado_file = "analisis_gemini_consolidado_con_codigo.xlsx"
                try:
                    df_consolidado.to_excel(consolidado_file, index=False)
                    print(f"\n[OK] Análisis consolidado guardado en: {consolidado_file}")
                except Exception as e:
                    print(f"[ERROR] Error guardando análisis consolidado: {e}")
            
            
        else:
            print("[ERROR] No se encontraron detalles de productos para mostrar")
            df_product_details = pd.DataFrame()
    
    # Export final data to Excel
    print(f"\n[INFO] Exportando datos finales a {output_file}...")
    success = export_to_excel(df_with_details, output_file)
    
    if success:
        print(f"\n[OK] Proceso completado exitosamente!")
        print(f"[INFO] Archivo generado: {output_file}")
        print(f"[INFO] Total de registros extraídos: {len(df)}")
        print(f"[INFO] Registros filtrados (TI): {len(df_filtered)}")
        print(f"[INFO] Registros con detalles: {len(df_with_details)}")
        
        # Return all DataFrames for further use
        result_dict = {
            'original_df': df,
            'filtered_df': df_filtered,
            'final_df': df_with_details,
            'excel_file': output_file
        }
        
        # Add product details DataFrame if it exists
        if 'df_product_details' in locals():
            result_dict['product_details_df'] = df_product_details
            result_dict['product_details_file'] = product_details_file
        
        # Add consolidated analysis DataFrame if it exists
        if 'df_consolidado' in locals() and not df_consolidado.empty:
            result_dict['consolidated_df'] = df_consolidado
            result_dict['consolidated_file'] = consolidado_file
        
        return result_dict
        
    else:
        print("\n[ERROR] Error en la exportación")
        return df  # Return original DataFrame even if export failed

if __name__ == "__main__":
    # Execute main function and get results
    result = main()
    
    # If result is a dictionary with DataFrames, provide additional information
    if isinstance(result, dict) and 'original_df' in result:
        print(f"\n[INFO] DATAFRAMES DISPONIBLES PARA USO:")
        print("=" * 50)
        print("• result['original_df'] - DataFrame con todos los datos extraídos")
        print("• result['filtered_df'] - DataFrame con datos filtrados por TI")
        print("• result['excel_file'] - Ruta del archivo Excel generado")
        print(f"\n[INFO] Ejemplo de uso:")
        print("   original_data = result['original_df']")
        print("   filtered_data = result['filtered_df']")
        print("   print(f'Total registros: {len(original_data)}')")
        print("   print(f'Registros TI: {len(filtered_data)}')")
    elif result is not None:
        print(f"\n[INFO] DATAFRAME DISPONIBLE:")
        print("=" * 30)
        print("• result - DataFrame con los datos extraídos")
        print(f"\n[INFO] Ejemplo de uso:")
        print("   data = result")
        print("   print(f'Total registros: {len(data)}')")
