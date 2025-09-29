# 🚀 Extractor de Datos de Contratación Pública - SERCOP

Este programa extrae datos de contratación pública del SERCOP (Sistema Oficial de Contratación Pública) de Ecuador, los filtra por palabras clave relacionadas con tecnología, y analiza los detalles de productos usando inteligencia artificial.

## 📋 Características

- ✅ **Extracción automática** de datos desde URL web
- ✅ **Navegación por paginación** (múltiples páginas)
- ✅ **Filtrado inteligente** por palabras clave de TI
- ✅ **Extracción de detalles** de productos solo de registros filtrados
- ✅ **Análisis con IA** usando Gemini 2.5 Flash
- ✅ **Exportación a Excel** con múltiples archivos de salida

## 🛠️ Requisitos del Sistema

- **Python 3.8+**
- **Google Chrome** (para Selenium WebDriver)
- **Conexión a Internet**
- **API Key de Google Gemini** (opcional, para análisis con IA)

## 📦 Instalación

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes git
git clone <url-del-repositorio>
cd compraspublicas

# O descargar y extraer el archivo ZIP
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
# Instalar desde requirements.txt
pip install -r requirements.txt

# O instalar manualmente:
pip install pandas beautifulsoup4 openpyxl lxml selenium webdriver-manager requests google-generativeai
```

### 4. Configurar API Key de Gemini (Opcional)

Edita el archivo `extract_table_data_pagination.py` y reemplaza la línea:

```python
GEMINI_API_KEY = "AIzaSyBAEB8s88fT27iszbPejZVa5Zq0pL_a9fQ"
```

Con tu propia API Key de Google Gemini:

```python
GEMINI_API_KEY = "TU_CLAVE_API_AQUI"
```

## 🚀 Uso

### Ejecución Básica

```bash
# Asegúrate de que el entorno virtual esté activado
python extract_table_data_pagination.py
```

### Configuración Avanzada

Puedes modificar los siguientes parámetros en el archivo `extract_table_data_pagination.py`:

```python
# Línea 631: Número de páginas a procesar
df = extract_all_pages_data(url, max_pages=50)  # Cambiar 50 por el número deseado

# Línea 625: URL del SERCOP
url = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/NCO/FrmNCOListado.cpe"

# Línea 626: Nombre del archivo de salida
output_file = "necesidades_contratacion_filtrado_TI.xlsx"
```

## 📊 Archivos de Salida

El programa genera los siguientes archivos Excel:

1. **`necesidades_contratacion_filtrado_TI.xlsx`** - Datos principales filtrados por TI
2. **`detalles_productos.xlsx`** - Detalles de productos extraídos
3. **`analisis_gemini_consolidado.xlsx`** - Análisis con IA (si está configurado)

## 🔧 Estructura del Proyecto

```
compraspublicas/
├── extract_table_data_pagination.py    # Script principal
├── requirements.txt                     # Dependencias
├── README.md                           # Este archivo
├── venv/                               # Entorno virtual (creado automáticamente)
└── archivos_generados/                 # Archivos Excel de salida
    ├── necesidades_contratacion_filtrado_TI.xlsx
    ├── detalles_productos.xlsx
    └── analisis_gemini_consolidado.xlsx
```

## ⚙️ Configuración de Palabras Clave

El programa filtra por las siguientes categorías de palabras clave:

### Desarrollo Software
- software, sistema informático, plataforma digital, sistema de gestión, aplicativo, implementación de software, mantenimiento de software, firma electrónica

### Ciberseguridad
- ciberseguridad, seguridad informática, análisis de vulnerabilidades, pentesting, seguridad de la información, consultoría en seguridad, ISO 27001

### Datos & IA
- datos, análisis de datos, analítica, procesamiento de datos, ETL, inteligencia de negocios, business intelligence, visualización de datos, modelado de datos, análisis estadístico, estadística, modelado predictivo, inteligencia artificial

### Consultoría y Soporte TI
- consultoría tecnológica, soporte técnico, mesa de ayuda, interoperabilidad, servicios TI

## 🐛 Solución de Problemas

### Error: "ChromeDriver not found"
```bash
# El programa descarga automáticamente ChromeDriver, pero si falla:
pip install --upgrade webdriver-manager
```

### Error: "Module not found"
```bash
# Asegúrate de que el entorno virtual esté activado
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "API Key not configured"
```bash
# Si no tienes API Key de Gemini, el programa funcionará sin análisis de IA
# Solo comentar o eliminar la configuración de Gemini en el código
```

### Error de Conexión
```bash
# Verifica tu conexión a Internet
# El programa necesita acceso a www.compraspublicas.gob.ec
```

## 📈 Flujo del Programa

1. **PASO 1**: Extrae datos principales de todas las páginas (sin detalles)
2. **PASO 2**: Filtra datos por palabras clave de TI
3. **PASO 3**: Extrae detalles de productos solo de registros filtrados
4. **PASO 4**: Analiza con IA (si está configurado)
5. **PASO 5**: Exporta resultados a archivos Excel

## 🔍 Ejemplo de Uso

```python
# Ejecutar el programa
python extract_table_data_pagination.py

# El programa mostrará:
# - Progreso de extracción por páginas
# - Número de registros encontrados
# - Progreso de filtrado
# - Análisis con IA (si está configurado)
# - Archivos generados
```

## 📝 Notas Importantes

- **Crear archivo .env**: Crear un archivo .env con la GEMINI_API_KEY ya que no va a estar en el codigo.
- **Tiempo de ejecución**: Depende del número de páginas (aproximadamente 2-3 segundos por página)
- **Conexión estable**: Se requiere conexión a Internet estable
- **Recursos**: El programa usa Chrome en modo headless, consume memoria moderada
- **Límites**: El SERCOP puede tener límites de velocidad, el programa incluye pausas automáticas

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de "Solución de Problemas"
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que el entorno virtual esté activado
4. Comprueba tu conexión a Internet

## 📊 Estadísticas del Programa

- **Páginas procesadas**: Configurable (por defecto: 50)
- **Registros por página**: 10
- **Tiempo promedio**: 2-3 segundos por página
- **Memoria utilizada**: ~200-500 MB
- **Archivos generados**: 3 archivos Excel

---

**¡Disfruta extrayendo datos de contratación pública! 🚀**
