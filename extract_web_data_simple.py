#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para extraer datos de tabla web y exportar a Excel
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def extract_table_from_web(url):
    """
    Extraer datos de tabla desde URL web usando pandas
    """
    print(f"Extrayendo datos desde: {url}")
    
    try:
        # Intentar leer tablas directamente con pandas
        print("Intentando leer tablas con pandas...")
        tables = pd.read_html(url)
        
        if tables:
            print(f"Se encontraron {len(tables)} tablas")
            # Usar la primera tabla que tenga datos
            for i, table in enumerate(tables):
                if len(table) > 0 and len(table.columns) > 5:  # Tabla con suficientes columnas
                    print(f"Usando tabla {i+1} con {len(table)} filas y {len(table.columns)} columnas")
                    return table
            
        print("No se encontraron tablas válidas con pandas")
        return None
        
    except Exception as e:
        print(f"Error con pandas: {e}")
        return None

def extract_with_requests(url):
    """
    Extraer datos usando requests y BeautifulSoup
    """
    print("Intentando con requests y BeautifulSoup...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar tabla con id="table_id"
        table = soup.find('table', {'id': 'table_id'})
        
        if table:
            print("Tabla encontrada, extrayendo datos...")
            
            # Extraer headers
            headers = []
            header_row = table.find('thead').find('tr')
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
            
            print(f"Headers encontrados: {headers}")
            
            # Extraer datos
            data_rows = []
            tbody = table.find('tbody')
            
            if tbody:
                for row in tbody.find_all('tr'):
                    row_data = []
                    cells = row.find_all('td')
                    
                    for i, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        
                        # Manejar enlaces en la columna de Entidad Contratante
                        if i == 7:  # Columna de Entidad Contratante
                            link = cell.find('a')
                            if link:
                                cell_text = link.get_text(strip=True)
                        
                        row_data.append(cell_text)
                    
                    if len(row_data) == len(headers):
                        data_rows.append(row_data)
            
            print(f"Extraídas {len(data_rows)} filas de datos")
            
            if data_rows:
                df = pd.DataFrame(data_rows, columns=headers)
                return df
        
        print("No se encontró tabla con datos")
        return None
        
    except Exception as e:
        print(f"Error con requests: {e}")
        return None

def export_to_excel(df, filename):
    """
    Exportar DataFrame a Excel
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Necesidades de Contratación', index=False)
            
            # Ajustar ancho de columnas
            workbook = writer.book
            worksheet = writer.sheets['Necesidades de Contratación']
            
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
        
        print(f"✅ Datos exportados exitosamente a {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error exportando a Excel: {e}")
        return False

def main():
    """
    Función principal
    """
    url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/FrmNCOListado.cpe"
    output_file = "necesidades_contratacion_web.xlsx"
    
    print("=== EXTRACTOR DE DATOS DE CONTRATACIÓN PÚBLICA ===\n")
    
    # Intentar extraer datos
    df = extract_table_from_web(url)
    
    if df is None or df.empty:
        print("\nMétodo pandas falló, intentando con requests...")
        df = extract_with_requests(url)
    
    if df is None or df.empty:
        print("\n❌ No se pudieron extraer datos de la página web")
        print("La página puede requerir JavaScript para cargar los datos dinámicamente")
        return
    
    print(f"\n📊 Datos extraídos: {len(df)} filas, {len(df.columns)} columnas")
    print(f"Columnas: {list(df.columns)}")
    
    # Mostrar primeras filas
    print("\nPrimeras 3 filas de datos:")
    print(df.head(3).to_string())
    
    # Exportar a Excel
    print(f"\n💾 Exportando a {output_file}...")
    success = export_to_excel(df, output_file)
    
    if success:
        print(f"\n🎉 Proceso completado exitosamente!")
        print(f"Archivo generado: {output_file}")
    else:
        print("\n❌ Error en la exportación")

if __name__ == "__main__":
    main()
