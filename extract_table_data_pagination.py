#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract table data from web URL with pagination support and export to Excel
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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

def extract_table_data_from_page(driver, page_num):
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
                
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    
                    # Handle special cases for certain columns
                    if i == 7:  # Entidad Contratante column
                        link = cell.find('a')
                        if link:
                            cell_text = link.get_text(strip=True)
                    
                    row_data.append(cell_text)
                
                # Only add row if it has the expected number of columns
                if len(row_data) == 10:  # Expected number of columns
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
    Extract data from all pages
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
            
            # Extract data from current page
            page_data = extract_table_data_from_page(driver, page_num)
            
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
                            'Contacto'
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
    
    print(f"\n🔍 Filtrando datos por palabras clave en: '{descripcion_col}'")
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
        print(f"✅ Registros encontrados: {len(filtered_df)}")
        print("\n📊 Resumen por categoría:")
        category_counts = pd.Series(matched_categories).value_counts()
        for category, count in category_counts.items():
            print(f"   • {category}: {count} registros")
        
        return filtered_df
    else:
        print("❌ No se encontraron registros que coincidan con las palabras clave")
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

def main():
    """
    Main function
    """
    url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/FrmNCOListado.cpe"
    output_file = "necesidades_contratacion_filtrado_TI.xlsx"
    
    print("=== EXTRACTOR DE DATOS DE CONTRATACIÓN PÚBLICA CON PAGINACIÓN ===\n")
    
    # Extract data from all pages
    df = extract_all_pages_data(url, max_pages=120)  # Set max_pages=10 for testing
    
    if df is None or df.empty:
        print("❌ No se pudieron extraer datos de la página web")
        return
    
    print(f"\n📊 Datos extraídos: {len(df)} filas, {len(df.columns)} columnas")
    print(f"Columnas: {list(df.columns)}")
    
    # Clean data
    df = clean_data(df)
    
    # Filter data by keywords
    df_filtered = filter_data_by_keywords(df)
    
    if df_filtered.empty:
        print("\n❌ No se encontraron registros que coincidan con los criterios de filtrado")
        return
    
    # Show first few rows of filtered data
    print("\nPrimeras 3 filas de datos filtrados:")
    print(df_filtered.head(3).to_string())
    
    # Export filtered data to Excel
    print(f"\n💾 Exportando datos filtrados a {output_file}...")
    success = export_to_excel(df_filtered, output_file)
    
    if success:
        print(f"\n🎉 Proceso completado exitosamente!")
        print(f"Archivo generado: {output_file}")
        print(f"Total de registros extraídos: {len(df)}")
        print(f"Registros filtrados (TI): {len(df_filtered)}")
    else:
        print("\n❌ Error en la exportación")

if __name__ == "__main__":
    main()
