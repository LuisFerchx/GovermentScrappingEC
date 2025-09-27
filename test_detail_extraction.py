#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para extraer datos de páginas de detalle
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
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
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        return None

def test_detail_page_extraction():
    """
    Test extraction from a single detail page
    """
    # Example detail URL from the main page
    detail_url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/NCORegistroDetalle.cpe?&id=1fQpwPnqcDzqoVtByJKe5gMDvVJ0q59BtxtqA9vpkL4,&op=0"
    
    driver = None
    try:
        print(f"🔍 Probando extracción de página de detalle: {detail_url}")
        
        driver = setup_driver()
        if not driver:
            print("❌ No se pudo configurar el driver")
            return
        
        # Navigate to detail page
        driver.get(detail_url)
        time.sleep(5)  # Wait for page to load
        
        # Get page source
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("📄 Contenido de la página:")
        print("=" * 50)
        
        # Look for all tables
        tables = soup.find_all('table')
        print(f"🔍 Se encontraron {len(tables)} tablas en la página")
        
        for i, table in enumerate(tables):
            print(f"\n📋 Tabla {i+1}:")
            print("-" * 30)
            
            # Get table headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text(strip=True))
                print(f"Headers: {headers}")
            
            # Get table rows
            rows = table.find_all('tr')[1:]  # Skip header row
            print(f"Filas encontradas: {len(rows)}")
            
            for j, row in enumerate(rows[:3]):  # Show first 3 rows
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                print(f"  Fila {j+1}: {row_data}")
        
        # Look for specific elements that might contain product information
        print(f"\n🔍 Buscando elementos específicos:")
        print("-" * 30)
        
        # Look for divs with product information
        product_divs = soup.find_all('div', class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))
        print(f"Divs de productos: {len(product_divs)}")
        
        # Look for spans with product information
        product_spans = soup.find_all('span', string=lambda x: x and ('producto' in x.lower() or 'item' in x.lower()))
        print(f"Spans de productos: {len(product_spans)}")
        
        # Look for any text containing "CPC" or "Descripción"
        cpc_elements = soup.find_all(string=lambda x: x and 'CPC' in x)
        print(f"Elementos con 'CPC': {len(cpc_elements)}")
        
        desc_elements = soup.find_all(string=lambda x: x and 'Descripción' in x)
        print(f"Elementos con 'Descripción': {len(desc_elements)}")
        
        # Save HTML for inspection
        with open('detail_page.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 HTML guardado en 'detail_page.html' para inspección")
        
    except Exception as e:
        print(f"❌ Error en la extracción: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_detail_page_extraction()
