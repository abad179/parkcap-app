# TS2CAD - Convertidora Estación Total a AutoCAD/CivilCAD

Aplicación de escritorio “todo-en-uno” para convertir archivos de campo de estaciones totales (Sokkia / Topcon / Leica / Hi-Target y genéricos) a formatos listos para AutoCAD/CivilCAD/Civil 3D. El formato de exportación principal por defecto es **TXT NXY** con orden **n, x, y**.

## Características
- Importación genérica de TXT/CSV con separadores comunes.
- Normalización de puntos con esquema común: `n, x, y, z, desc`.
- Reglas de limpieza, renumeración y diccionario de códigos → capas.
- Exportación a TXT (NXY, PNEZD, PENZD), CSV configurable, SCR y DXF.
- Reporte final de conversión.
- Configuración persistente en JSON.

## Requisitos
- Python 3.11+
- Dependencias:
  - `PySide6` o `tkinter` (incluido en Python). Esta implementación usa **tkinter**.
  - `ezdxf` para exportar DXF.

Instalación de dependencias:
```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación
```bash
python -m ts2cad.ui.app
```

## Empaquetado (Windows)
Usar **PyInstaller** para generar un `.exe`:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile -n ts2cad_app src/ts2cad/ui/app.py
```

Para distribución portable (carpeta):
```bash
pyinstaller --noconsole -n ts2cad_app src/ts2cad/ui/app.py
```
El ejecutable se genera en `dist/`.

## Estructura
```
src/ts2cad/
  core/         # modelos, configuración, reporte
  importers/    # importadores por marca y genérico
  normalizer/   # limpieza y validaciones
  exporters/    # TXT, CSV, SCR, DXF, reporte
  ui/           # interfaz gráfica
samples/        # ejemplos
```

## Samples
Ver carpeta `samples/` para archivos de ejemplo.

## Supuestos y decisiones
- Si el archivo no tiene encabezados reconocibles, se asume orden: `n, x, y, z, desc`.
- Los formatos propietarios se manejan **best-effort** con importadores de texto y se recomienda usar el importador genérico si el parseo falla.
- El formato de exportación principal se puede cambiar en Configuración sin afectar la normalización interna.

## Pruebas
```bash
pytest
```
