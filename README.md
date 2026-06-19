# PyStock_Manager

Sistema de Gestión de Inventario 📦
Un sistema robusto y modular desarrollado en **Python** diseñado para optimizar el control de existencias, facturación, reportes y la gestión integral de clientes y proveedores. El proyecto sigue una arquitectura limpia y organizada por componentes para garantizar su escalabilidad y fácil mantenimiento.


 🚀 Características Principales

•	Gestión de Inventario: Control total de existencias, entradas y salidas de mercancía.

•	Módulo de Facturación: Creación, detalle y seguimiento de facturas emitidas de manera estructurada.

•	Gestión de Terceros: Directorio y administración optimizada de Clientes (Customers) y Proveedores (Suppliers).

•	Reportes Estadísticos: Generación de vistas e informes analíticos del estado actual del inventario y las ventas.

•	Estructura Modular: Código desacoplado basado en vistas independientes para cada entidad del sistema.


🛠️ Tecnologías Utilizadas
1.	Lenguaje: Python 3.11+
2.	Paradigma: Programación Orientada a Objetos (POO)
3.	Arquitectura: Diseño basado en Vistas y Configuración Centralizada


 📂 Estructura del Proyecto
La raíz del proyecto se organiza de la siguiente manera (las carpetas de caché `__pycache__` se omiten en producción):

```text
Inventario/
│
├── config.py                 # Configuración global y parámetros del sistema
│
└── views/                    # Vistas y componentes de la interfaz/lógica de presentación
    ├── customer_supplier_view.py   # Gestión de Clientes y Proveedores
    ├── invoice_detail_view.py      # Control y desglose de detalles de facturas
    ├── invoice_view.py             # Gestión general de facturación
    ├── order_view.py               # Procesamiento y visualización de órdenes
    ├── product_view.py             # Control, registro y edición de productos
    └── report_view.py              # Generación de reportes y estadísticas



🔧 Instalación y Configuración
Sigue estos pasos para ejecutar el proyecto en tu entorno local:
 1. Pre requisitos
Asegúrate de tener instalado **Python 3.11** o superior en tu sistema. Puedes verificarlo ejecutando:
```bash
Python –version

2. Clonar o Descomprimir el Proyecto
Extrae el contenido del archivo comprimido o clona el repositorio en tu directorio de trabajo. Luego, navega hacia la carpeta raíz:
```bash
Cd inventario

3. Configuración del Entorno (Opcional pero recomendado)
Es buena práctica utilizar un entorno virtual para aislar las dependencias:
```bash
# Crear entorno virtual
Python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\activate

# Activar entorno (Linux/macOS)
Source venv/bin/activate

 4. Configurar el Sistema
Revisa el archivo config.py en caso de que necesites ajustar variables de entorno, rutas de almacenamiento o parámetros iniciales del sistema.


💻 Ejecución de la Aplicación
Para iniciar el sistema de inventario, ejecuta el archivo principal desde la consola de comandos:
```bash
Python main.py
Nota: Asegúrate de que tu archivo de arranque principal esté en la raíz apuntando a la inicialización de las vistas correspondientes).


👥 Desarrolladores
	Carlos J. Molina R. V-28.774.022
	Crismar C. Hernández L. V-28.767.682
	Luis F. Colina M. V-30.400.695
	Migfrannys C. Martínez N. V-28.735.102
	Rafael A. Velasco A. V-31.577.792
Estudiante de Ingeniería de Sistemas
08S-2630-D1


💡 Consejos adicionales:
1. Archivo `main.py`: Si tu script ejecutable principal está fuera de la carpeta `inventario` o tiene otro nombre (por ejemplo, `run.py`), solo cámbialo en la sección de **Ejecución**.
2. Dependencias: Si usas librerías externas (como `Flask`, `Tkinter` avanzado, etc.), puedes añadir una sección intermedia que diga `pip install -r requirements.txt` para que se vea aún más profesional.

