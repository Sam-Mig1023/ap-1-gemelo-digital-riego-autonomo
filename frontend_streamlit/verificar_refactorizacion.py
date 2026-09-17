"""
Script de verificación post-refactorización
Verifica que todos los archivos fueron actualizados correctamente
"""
import os
import sys

def verificar_archivo(ruta, debe_contener, no_debe_contener=None):
    """Verifica que un archivo contiene ciertos strings y no contiene otros"""
    if not os.path.exists(ruta):
        return False, f"❌ Archivo no encontrado: {ruta}"
    
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar que contiene lo que debe
    for texto in debe_contener:
        if texto not in contenido:
            return False, f"❌ No contiene '{texto}'"
    
    # Verificar que NO contiene lo que no debe
    if no_debe_contener:
        for texto in no_debe_contener:
            if texto in contenido:
                return False, f"❌ Aún contiene '{texto}' (debe ser eliminado)"
    
    return True, "✅ OK"

def main():
    print("=" * 60)
    print("VERIFICACIÓN POST-REFACTORIZACIÓN")
    print("=" * 60)
    print()
    
    errores = 0
    exitosos = 0
    
    # Verificaciones
    verificaciones = [
        {
            "nombre": "modulos/theme.py",
            "debe_contener": ["plotly_template", "plotly_layout", "status_colors", "_is_dark"],
            "no_debe_contener": []
        },
        {
            "nombre": "app.py",
            "debe_contener": ["CSS adaptativo", "var(--primary-color", "class=\"user-card\""],
            "no_debe_contener": []
        },
        {
            "nombre": "pages/dashboard.py",
            "debe_contener": ["from modulos.theme import", "status_colors()", "plotly_layout"],
            "no_debe_contener": ["#0f172a", "#1e293b"]
        },
        {
            "nombre": "pages/control_riego.py",
            "debe_contener": ["Control de Riego VRI"],
            "no_debe_contener": ["💧", "🔧", "✅", "❌"]
        },
        {
            "nombre": "pages/agente_rl.py",
            "debe_contener": ["from modulos.theme import", "status_colors"],
            "no_debe_contener": ["#16a34a", "#dc2626", "#d97706"]
        },
        {
            "nombre": "modulos/visualizacion_3d.py",
            "debe_contener": ["from .theme import status_colors", "_color_cwsi"],
            "no_debe_contener": ["🌾", "📐", "🌡️", "🚨"]
        },
        {
            "nombre": "modulos/auth.py",
            "debe_contener": ["VRI Digital Twin", "Iniciar sesión"],
            "no_debe_contener": []
        },
    ]
    
    for verif in verificaciones:
        resultado, mensaje = verificar_archivo(
            verif["nombre"],
            verif["debe_contener"],
            verif.get("no_debe_contener")
        )
        
        print(f"{verif['nombre']:40} {mensaje}")
        
        if resultado:
            exitosos += 1
        else:
            errores += 1
    
    print()
    print("=" * 60)
    print(f"RESUMEN: {exitosos} exitosos, {errores} errores")
    print("=" * 60)
    
    if errores == 0:
        print()
        print("✅ ¡Refactorización completada exitosamente!")
        print("   Todos los archivos fueron actualizados correctamente.")
        print()
        print("📋 Próximos pasos:")
        print("   1. Ejecuta: streamlit run app.py")
        print("   2. Prueba cambiar entre tema claro y oscuro")
        print("   3. Verifica que todos los gráficos se ven bien")
        print()
        return 0
    else:
        print()
        print("⚠️  Algunos archivos tienen problemas.")
        print("   Revisa los errores arriba y corrige los archivos necesarios.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())