# --- SISTEMA DE INTELIGENCIA DE MERCADO v5.4 (Prioridad por IA) ---
# Autor: Asesor Senior en Contratación Pública (COMPRAS PÚBLICAS ECUADOR)
# Fecha: 23 de septiembre de 2025
# Descripción: Versión final donde la IA (Gemini) asigna automáticamente la prioridad
#              a cada oportunidad, optimizando el flujo de trabajo.

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from datetime import datetime, timezone
import os
import time
import json
import google.generativeai as genai

# --- CONFIGURACIÓN DE API ---
# ¡ACCIÓN REQUERIDA! Pega aquí tu clave de API de Gemini.
GEMINI_API_KEY = "AIzaSyBAEB8s88fT27iszbPejZVa5Zq0pL_a9fQ"
MODELO_IA = None
try:
    if not GEMINI_API_KEY or "TU_CLAVE" in GEMINI_API_KEY:
        raise ValueError("La clave de API de Gemini no ha sido configurada.")
    genai.configure(api_key=GEMINI_API_KEY)
    MODELO_IA = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("  > Modelo de IA (Gemini) configurado correctamente.")
except Exception as e:
    print(f"  ! Advertencia: {e}")
    print("  ! El análisis con IA estará deshabilitado.")


# --- CONFIGURACIÓN ESTRATÉGICA ---
EXCEL_FILENAME = "1._AI_Base_de_Datos_SERCOP.xlsx"
KEYWORDS_HUREONSYS1 = {
    "Datos & IA": [
         "datos",
        "análisis de datos",
    ]
}

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
        "análisis de datos",          # Añadido para mayor especificidad
        "analítica",
        "procesamiento de datos",     # Captura procesos de ETL y limpieza
        "ETL",                        # Término técnico que puede aparecer
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

YEAR_TO_SEARCH = datetime.now().year

def requests_retry_session(retries=3, backoff_factor=1, status_forcelist=(500, 502, 504, 429), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries, read=retries, connect=retries,
        backoff_factor=backoff_factor, status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def analizar_con_gemini(contrato_texto, modelo):
    if not modelo: return {}
    # --- PROMPT ACTUALIZADO ---
    # Ahora le pedimos a la IA que determine y devuelva la prioridad.
    prompt = f"""
    Eres un Asesor Senior en Contratación Pública Ecuatoriana. Analiza el siguiente contrato del SERCOP para tu cliente HureonSys (experto en Desarrollo de Software, Ciberseguridad, y Análisis de Datos con Estadística) y determina su relevancia.
    Contrato: "{contrato_texto}"
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

def consultar_y_enriquecer(year, search_keyword, session):
    BASE_URL_SEARCH = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/search_ocds"
    BASE_URL_RECORD = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/record"
    params_search = {'year': year, 'search': search_keyword, 'page': 1}
    
    print(f"  > Buscando '{search_keyword}'...")
    try:
        response = session.get(BASE_URL_SEARCH, params=params_search, timeout=30)
        response.raise_for_status()
        oportunidades_encontradas = response.json().get('data', [])
        
        oportunidades_enriquecidas = []
        print(f"  > Enriqueciendo {len(oportunidades_encontradas)} contratos...")
        for contrato in oportunidades_encontradas:
            ocid = contrato.get('ocid')
            if not ocid: continue
            time.sleep(0.5)
            params_record = {'ocid': ocid}
            response_record = session.get(BASE_URL_RECORD, params=params_record, timeout=30)
            if response_record.status_code != 200: continue
            
            release = response_record.json().get('records', [{}])[0].get('releases', [{}])[0]
            tender = release.get('tender', {})
            
            contrato.update({
                'estado_proceso': tender.get('status', 'No disponible'),
                'fecha_limite_postulacion': tender.get('tenderPeriod', {}).get('endDate'),
                'presupuesto_referencial': tender.get('value', {}).get('amount'),
                'categoria_busqueda': search_keyword,
                'release_completo': release
            })
            oportunidades_enriquecidas.append(contrato)
        return oportunidades_enriquecidas
    except Exception as e:
        print(f"  ! Error grave al consultar para '{search_keyword}': {e}")
        return []

# --- BLOQUE PRINCIPAL DE EJECUCIÓN ---
if __name__ == "__main__":
    session = requests_retry_session()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, EXCEL_FILENAME)
    
    print("--- INICIANDO SISTEMA DE INTELIGENCIA DE MERCADO v5.4 ---")
    
    df_historico = pd.DataFrame()
    if os.path.exists(full_path):
        try:
            print(f"  > Cargando historial desde '{EXCEL_FILENAME}'...")
            df_historico = pd.read_excel(full_path)
        except Exception as e:
            print(f"  ! No se pudo leer el archivo Excel. Se creará uno nuevo. Error: {e}")

    nuevos_resultados = []
    for category, keywords in KEYWORDS_HUREONSYS.items():
        print(f"\n[BUSCANDO CATEGORÍA: {category}]")
        for keyword in keywords:
            results = consultar_y_enriquecer(YEAR_TO_SEARCH, keyword, session)
            if results:
                nuevos_resultados.extend(results)

    if not nuevos_resultados and df_historico.empty:
        print("\n--- PROCESO FINALIZADO: Sin datos nuevos ni historial. ---")
    else:
        print("\n--- CONSOLIDANDO DATOS ---")
        df_nuevos = pd.DataFrame(nuevos_resultados)
        df_consolidado = pd.concat([df_historico, df_nuevos])
        df_consolidado.drop_duplicates(subset=['ocid'], inplace=True, keep='last')
        
        if MODELO_IA:
            print(f"\n--- INICIANDO ANÁLISIS CON GEMINI ---")
            for index, row in df_consolidado.iterrows():
                if pd.isna(row.get('Puntuación IA')):
                    print(f"  > Analizando OCID: {row.get('ocid', 'N/A')}...")
                    resultado_ia = analizar_con_gemini(row.get('release_completo'), MODELO_IA)
                    # --- LÓGICA ACTUALIZADA ---
                    # Ahora llenamos también la prioridad con la respuesta de la IA
                    df_consolidado.loc[index, 'Puntuación IA'] = resultado_ia.get('puntuacion_relevancia')
                    df_consolidado.loc[index, 'Prioridad'] = resultado_ia.get('prioridad') # <--- NUEVO
                    df_consolidado.loc[index, 'Motivo IA'] = resultado_ia.get('motivo')
                    df_consolidado.loc[index, 'Acción IA'] = resultado_ia.get('accion_recomendada')
                    time.sleep(4.1)
        
        print("\n--- PROCESANDO Y GENERANDO REPORTE ESTRATÉGICO ---")
        df_consolidado['fecha_limite_postulacion'] = pd.to_datetime(df_consolidado['fecha_limite_postulacion'], errors='coerce', utc=True)
        
        # Columnas de gestión manual (Prioridad ahora viene de la IA)
        for col in ['Estado Postulación', 'Responsable', 'Notas']:
            if col not in df_consolidado.columns:
                df_consolidado[col] = ''
        df_consolidado['Estado Postulación'].fillna('Por Revisar', inplace=True)

        columnas = {
            'Puntuación IA': 'Puntuación IA',
            'Prioridad': 'Prioridad IA', # Renombrado para claridad
            'Acción IA': 'Acción IA',
            'Motivo IA': 'Motivo IA',
            'Estado Postulación': 'Estado Postulación',
            'Responsable': 'Responsable',
            'Notas': 'Notas',
            'estado_proceso': 'Estado del Proceso',
            'fecha_limite_postulacion': 'Fecha Límite',
            'presupuesto_referencial': 'Presupuesto',
            'ocid': 'OCID',
            'buyerName': 'Entidad Compradora',
            'title': 'Título Proceso',
            'description': 'Descripción',
            'internal_type': 'Tipo Contratación',
            'categoria_busqueda': 'Palabra Clave Origen'
        }
        
        columnas_existentes = [col for col in columnas.keys() if col in df_consolidado.columns]
        df_reporte = df_consolidado[columnas_existentes].rename(columns=columnas)
        df_reporte.insert(0, 'Días para Postular', '')
        
        if 'Puntuación IA' in df_reporte.columns:
            df_reporte['Puntuación IA'] = pd.to_numeric(df_reporte['Puntuación IA'], errors='coerce')
            df_reporte.sort_values(by=['Puntuación IA'], ascending=[False], inplace=True, na_position='last')

        writer = pd.ExcelWriter(full_path, engine='openpyxl', datetime_format='YYYY-MM-DD HH:MM')
        df_reporte.to_excel(writer, sheet_name='Oportunidades', index=False)
        worksheet = writer.sheets['Oportunidades']

        try:
            col_fecha_limite_letra = [c[0].column_letter for c in worksheet.columns if c[0].value == 'Fecha Límite'][0]
            for i in range(2, len(df_reporte) + 2):
                worksheet[f'A{i}'] = f'=IF({col_fecha_limite_letra}{i}<>"", INT({col_fecha_limite_letra}{i}-TODAY()), "N/A")'
        except IndexError:
            print("  ! Advertencia: No se encontró la columna 'Fecha Límite', no se pudo generar la fórmula.")

        worksheet.auto_filter.ref = worksheet.dimensions
        writer.close()
        
        print(f"\n✅ BASE DE DATOS ACTUALIZADA: {EXCEL_FILENAME}")
        print(f"   Total de registros: {len(df_reporte)}")
        print("--- PROCESO COMPLETADO ---")