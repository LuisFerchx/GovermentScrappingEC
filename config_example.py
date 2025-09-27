#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo de configuración de ejemplo para el Extractor de Datos de Contratación Pública
Copia este archivo como 'config.py' y modifica los valores según tus necesidades
"""

# =============================================================================
# CONFIGURACIÓN DE API DE GEMINI
# =============================================================================
# Obtén tu API Key desde: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "TU_CLAVE_API_AQUI"

# Modelo de IA a usar (opciones: gemini-1.5-flash, gemini-2.5-flash)
GEMINI_MODEL = "gemini-2.5-flash"

# =============================================================================
# CONFIGURACIÓN DE EXTRACCIÓN
# =============================================================================
# URL del SERCOP (no modificar a menos que cambie la estructura)
SERCOP_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/FrmNCOListado.cpe"

# Número máximo de páginas a procesar (None = todas las páginas disponibles)
MAX_PAGES = 50

# Tiempo de espera entre páginas (segundos)
PAGE_DELAY = 2

# Tiempo de espera para cargar contenido dinámico (segundos)
LOAD_DELAY = 5

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS DE SALIDA
# =============================================================================
# Archivo principal de salida
OUTPUT_FILE = "necesidades_contratacion_filtrado_TI.xlsx"

# Archivo de detalles de productos
PRODUCT_DETAILS_FILE = "detalles_productos.xlsx"

# Archivo de análisis consolidado con IA
CONSOLIDATED_ANALYSIS_FILE = "analisis_gemini_consolidado.xlsx"

# =============================================================================
# CONFIGURACIÓN DE FILTROS
# =============================================================================
# Palabras clave para filtrado (puedes agregar más)
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

# =============================================================================
# CONFIGURACIÓN DE SELENIUM
# =============================================================================
# Configuración del navegador
BROWSER_OPTIONS = {
    "headless": True,  # Ejecutar en segundo plano
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Tiempo de espera para elementos (segundos)
ELEMENT_WAIT_TIMEOUT = 30

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# Mostrar progreso detallado
SHOW_DETAILED_PROGRESS = True

# =============================================================================
# CONFIGURACIÓN DE ANÁLISIS CON IA
# =============================================================================
# Habilitar análisis con IA
ENABLE_AI_ANALYSIS = True

# Tiempo de espera entre análisis (segundos)
AI_ANALYSIS_DELAY = 4.1

# Máximo número de productos a analizar por sesión
MAX_AI_ANALYSES_PER_SESSION = 100

# =============================================================================
# CONFIGURACIÓN AVANZADA
# =============================================================================
# Reintentos en caso de error
MAX_RETRIES = 3

# Tiempo de espera entre reintentos (segundos)
RETRY_DELAY = 5

# Guardar HTML de páginas de detalle para debugging
SAVE_DEBUG_HTML = False

# Directorio para archivos de debug
DEBUG_DIR = "debug_files"
