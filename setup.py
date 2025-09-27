#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuración para el Extractor de Datos de Contratación Pública
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"   Salida: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado. Se requiere Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def create_virtual_environment():
    """Crea el entorno virtual"""
    if os.path.exists("venv"):
        print("📁 Entorno virtual ya existe")
        return True
    
    return run_command("python -m venv venv", "Creando entorno virtual")

def install_dependencies():
    """Instala las dependencias"""
    # Determinar el comando pip según el SO
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    # Actualizar pip
    run_command(f"{pip_cmd} install --upgrade pip", "Actualizando pip")
    
    # Instalar dependencias
    return run_command(f"{pip_cmd} install -r requirements.txt", "Instalando dependencias")

def create_run_script():
    """Crea un script de ejecución"""
    if os.name == 'nt':  # Windows
        script_content = """@echo off
echo 🚀 Activando entorno virtual...
call venv\\Scripts\\activate
echo ✅ Entorno virtual activado
echo 🚀 Ejecutando extractor de datos...
python extract_table_data_pagination.py
pause
"""
        with open("run.bat", "w") as f:
            f.write(script_content)
        print("✅ Script de ejecución creado: run.bat")
    else:  # Linux/Mac
        script_content = """#!/bin/bash
echo "🚀 Activando entorno virtual..."
source venv/bin/activate
echo "✅ Entorno virtual activado"
echo "🚀 Ejecutando extractor de datos..."
python extract_table_data_pagination.py
"""
        with open("run.sh", "w") as f:
            f.write(script_content)
        os.chmod("run.sh", 0o755)
        print("✅ Script de ejecución creado: run.sh")

def main():
    """Función principal de configuración"""
    print("🚀 CONFIGURACIÓN DEL EXTRACTOR DE DATOS DE CONTRATACIÓN PÚBLICA")
    print("=" * 70)
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Crear entorno virtual
    if not create_virtual_environment():
        return False
    
    # Instalar dependencias
    if not install_dependencies():
        return False
    
    # Crear script de ejecución
    create_run_script()
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Activar el entorno virtual:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Ejecutar el programa:")
    print("   python extract_table_data_pagination.py")
    print("   O usar el script: run.bat (Windows) o ./run.sh (Linux/Mac)")
    print("\n💡 CONSEJO: Revisa el archivo README.md para más información")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ La configuración falló. Revisa los errores anteriores.")
        sys.exit(1)
    else:
        print("\n✅ ¡Todo listo para usar!")
