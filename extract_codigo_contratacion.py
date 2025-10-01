#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer el código de necesidad de contratación de la página HTML
y agregarlo a cada registro del archivo detalles_productos.xlsx
"""

import pandas as pd
from bs4 import BeautifulSoup
import re
import os

def extract_codigo_from_html(html_file_path):
    """
    Extrae el código de necesidad de contratación del archivo HTML
    """
    try:
        print(f"[INFO] Leyendo archivo HTML: {html_file_path}")
        
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Buscar el texto "Código Necesidad de Contratación:"
        codigo_element = soup.find('strong', string=re.compile(r'Código Necesidad de Contratación'))
        
        if codigo_element:
            # Obtener el texto del elemento padre (que contiene el código)
            parent_text = codigo_element.parent.get_text(strip=True)
            
            # Extraer el código usando regex - buscar el patrón NIC-XXXXX-XXXX-XXXXX
            # El formato parece ser: "Código Necesidad de Contratación: NIC-0860045180001-2025-00008"
            codigo_match = re.search(r'Código Necesidad de Contratación:\s*(NIC-[0-9]+-[0-9]+-[0-9]+)', parent_text)
            
            if codigo_match:
                codigo = codigo_match.group(1).strip()
                print(f"[OK] Código encontrado: {codigo}")
                return codigo
            else:
                print("[ERROR] No se pudo extraer el código del texto")
                print(f"[DEBUG] Texto encontrado: {parent_text[:100]}...")
                return None
        else:
            print("[ERROR] No se encontró el elemento con 'Código Necesidad de Contratación'")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error leyendo archivo HTML: {e}")
        return None

def add_codigo_to_excel(excel_file_path, codigo_contratacion):
    """
    Agrega el código de necesidad de contratación a cada registro del archivo Excel
    """
    try:
        print(f"[INFO] Leyendo archivo Excel: {excel_file_path}")
        
        # Leer el archivo Excel
        df = pd.read_excel(excel_file_path)
        
        print(f"[INFO] Registros encontrados: {len(df)}")
        print(f"[INFO] Columnas actuales: {list(df.columns)}")
        
        # Agregar nueva columna con el código de contratación
        df['Codigo_Necesidad_Contratacion'] = codigo_contratacion
        
        print(f"[OK] Código agregado a todos los registros: {codigo_contratacion}")
        
        # Guardar el archivo actualizado
        output_file = excel_file_path.replace('.xlsx', '_con_codigo.xlsx')
        df.to_excel(output_file, index=False)
        
        print(f"[OK] Archivo actualizado guardado como: {output_file}")
        
        # Mostrar una muestra de los datos
        print(f"\n[INFO] Muestra de los datos actualizados:")
        print("=" * 80)
        print(df[['Registro_ID', 'Entidad_Contratante', 'Codigo_Necesidad_Contratacion']].head().to_string(index=False))
        
        return output_file
        
    except Exception as e:
        print(f"[ERROR] Error procesando archivo Excel: {e}")
        return None

def main():
    """
    Función principal
    """
    print("=== EXTRACTOR DE CODIGO DE NECESIDAD DE CONTRATACION ===\n")
    
    # Rutas de archivos
    html_file = "Necesidades de Contratación y Recepción de Proformas2.html"
    excel_file = "detalles_productos.xlsx"
    
    # Verificar que los archivos existan
    if not os.path.exists(html_file):
        print(f"[ERROR] No se encontró el archivo HTML: {html_file}")
        return
    
    if not os.path.exists(excel_file):
        print(f"[ERROR] No se encontró el archivo Excel: {excel_file}")
        return
    
    # PASO 1: Extraer código del HTML
    print("[PASO 1] Extrayendo código de necesidad de contratación del HTML...")
    codigo = extract_codigo_from_html(html_file)
    
    if not codigo:
        print("[ERROR] No se pudo extraer el código de contratación")
        return
    
    # PASO 2: Agregar código al archivo Excel
    print(f"\n[PASO 2] Agregando código a cada registro del archivo Excel...")
    output_file = add_codigo_to_excel(excel_file, codigo)
    
    if output_file:
        print(f"\n[OK] Proceso completado exitosamente!")
        print(f"[INFO] Archivo original: {excel_file}")
        print(f"[INFO] Archivo actualizado: {output_file}")
        print(f"[INFO] Código agregado: {codigo}")
    else:
        print(f"\n[ERROR] Error en el proceso")

if __name__ == "__main__":
    main()
