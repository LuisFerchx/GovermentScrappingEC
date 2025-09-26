#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract table data from web URL and export to Excel
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

def fetch_web_content_requests(url):
    """
    Fetch content from web URL using requests (faster, but may not work with dynamic content)
    """
    print(f"Fetching data from URL using requests: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching web content with requests: {e}")
        return None

def fetch_web_content_selenium(url):
    """
    Fetch content from web URL using Selenium for dynamic content
    """
    print(f"Fetching data from URL using Selenium: {url}")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        # Initialize Chrome driver with webdriver-manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # Wait for the table to load
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "table_id")))
        
        # Wait a bit more for data to load
        time.sleep(5)
        
        # Get page source
        html_content = driver.page_source
        return html_content
        
    except Exception as e:
        print(f"Error fetching web content with Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def fetch_web_content(url):
    """
    Fetch content from web URL using Selenium for dynamic content
    """
    print("Using Selenium to fetch dynamic content...")
    # Use Selenium directly since the page loads data dynamically
    html_content = fetch_web_content_selenium(url)
    
    if html_content:
        print("Successfully fetched content using Selenium")
        return html_content
    
    print("Selenium method failed, trying requests as fallback...")
    # Try requests as fallback
    html_content = fetch_web_content_requests(url)
    
    if html_content and "table_id" in html_content:
        print("Successfully fetched content using requests")
        return html_content
    
    print("Both methods failed to fetch content")
    return None

def extract_table_data_from_url(url):
    """
    Extract table data from web URL and return as DataFrame
    """
    # Fetch HTML content from URL
    html_content = fetch_web_content(url)
    
    if not html_content:
        print("Failed to fetch content from URL")
        return None
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table with id="table_id"
    table = soup.find('table', {'id': 'table_id'})
    
    if not table:
        print("Table with id='table_id' not found")
        return None
    
    # Extract headers
    headers = []
    header_row = table.find('thead').find('tr')
    for th in header_row.find_all('th'):
        headers.append(th.get_text(strip=True))
    
    print(f"Found headers: {headers}")
    
    # Extract data rows
    data_rows = []
    tbody = table.find('tbody')
    
    if tbody:
        for row in tbody.find_all('tr'):
            row_data = []
            cells = row.find_all('td')
            
            for i, cell in enumerate(cells):
                # Clean up the text content
                cell_text = cell.get_text(strip=True)
                
                # Handle special cases for certain columns
                if i == 7:  # Entidad Contratante column (index 7)
                    # Extract text from link if present
                    link = cell.find('a')
                    if link:
                        cell_text = link.get_text(strip=True)
                
                row_data.append(cell_text)
            
            # Only add row if it has the expected number of columns
            if len(row_data) == len(headers):
                data_rows.append(row_data)
    
    print(f"Extracted {len(data_rows)} data rows")
    
    # Create DataFrame
    df = pd.DataFrame(data_rows, columns=headers)
    
    return df

def clean_data(df):
    """
    Clean and format the data
    """
    # Remove any empty rows
    df = df.dropna(how='all')
    
    # Clean up column names to match the requested format
    column_mapping = {
        'Tipo de Necesidad': 'Tipo de Necesidad',
        'Código Necesidad de Contratación': 'Código Necesidad de Contratación',
        'Fecha de Publicación': 'Fecha de Publicación',
        'Provincia - Cantón': 'Provincia - Cantón',
        'Descripción del Objeto de compra': 'Descripción del Objeto de compra',
        'Estado de la Necesidad': 'Estado de la Necesidad',
        'Fecha límite para la entrega de proformas': 'Fecha límite para la entrega de proformas',
        'Entidad Contratante': 'Entidad Contratante',
        'Dirección de Entrega': 'Dirección de Entrega',
        'Contacto': 'Contacto'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
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
        # Create Excel writer with formatting
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
                
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
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
    # Web URL and output file paths
    web_url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/FrmNCOListado.cpe"
    excel_file = "necesidades_contratacion.xlsx"
    
    print("Extracting table data from web URL...")
    
    # Extract data from URL
    df = extract_table_data_from_url(web_url)
    
    if df is None or df.empty:
        print("No data extracted from web URL")
        return
    
    print(f"Extracted {len(df)} rows of data")
    
    # Clean data
    df = clean_data(df)
    
    # Display first few rows
    print("\nFirst 5 rows of extracted data:")
    print(df.head())
    
    # Export to Excel
    print(f"\nExporting data to {excel_file}...")
    success = export_to_excel(df, excel_file)
    
    if success:
        print(f"\n✅ Successfully exported {len(df)} records to {excel_file}")
        print(f"Columns exported: {list(df.columns)}")
    else:
        print("❌ Failed to export data to Excel")

if __name__ == "__main__":
    main()
