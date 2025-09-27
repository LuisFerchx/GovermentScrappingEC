#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate DataFrame functionality
"""

import pandas as pd
from extract_table_data_pagination import main, display_dataframe_info

def test_dataframe_functionality():
    """
    Test the DataFrame functionality
    """
    print("=== PRUEBA DE FUNCIONALIDAD DE DATAFRAME ===\n")
    
    # Execute the main extraction function
    result = main()
    
    if result is None:
        print("❌ No se pudieron extraer datos")
        return
    
    # Handle different return types
    if isinstance(result, dict) and 'original_df' in result:
        original_df = result['original_df']
        filtered_df = result['filtered_df']
        excel_file = result['excel_file']
        
        print(f"\n🎯 RESULTADOS DE LA EXTRACCIÓN:")
        print("=" * 50)
        print(f"📁 Archivo Excel generado: {excel_file}")
        print(f"📊 DataFrame original: {original_df.shape[0]} filas x {original_df.shape[1]} columnas")
        print(f"🔍 DataFrame filtrado: {filtered_df.shape[0]} filas x {filtered_df.shape[1]} columnas")
        
        # Demonstrate DataFrame operations
        print(f"\n🔧 OPERACIONES CON DATAFRAMES:")
        print("=" * 40)
        
        # Basic statistics
        print(f"• Total de registros extraídos: {len(original_df)}")
        print(f"• Registros filtrados por TI: {len(filtered_df)}")
        print(f"• Porcentaje de relevancia: {len(filtered_df)/len(original_df)*100:.1f}%")
        
        # Column analysis
        print(f"\n📋 Análisis de columnas del DataFrame filtrado:")
        for col in filtered_df.columns:
            non_null = filtered_df[col].notna().sum()
            print(f"   • {col}: {non_null} valores no nulos")
        
        # Category analysis if available
        if 'Categoría' in filtered_df.columns:
            print(f"\n📊 Análisis por categoría:")
            category_counts = filtered_df['Categoría'].value_counts()
            for category, count in category_counts.items():
                print(f"   • {category}: {count} registros")
        
        return {
            'original': original_df,
            'filtered': filtered_df,
            'excel_file': excel_file
        }
    
    elif isinstance(result, pd.DataFrame):
        print(f"\n🎯 RESULTADO DE LA EXTRACCIÓN:")
        print("=" * 40)
        print(f"📊 DataFrame: {result.shape[0]} filas x {result.shape[1]} columnas")
        
        # Show basic info
        display_dataframe_info(result, "DataFrame Extraído")
        
        return result
    
    else:
        print("❌ Formato de resultado no reconocido")
        return None

if __name__ == "__main__":
    # Run the test
    dataframes = test_dataframe_functionality()
    
    if dataframes:
        print(f"\n✅ Prueba completada exitosamente!")
        print(f"💡 Los DataFrames están disponibles para análisis adicional")
    else:
        print(f"\n❌ La prueba falló")
