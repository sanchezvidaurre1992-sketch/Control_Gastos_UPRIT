# Control de Gastos – Semana 06 / Práctica Calificada 02

Aplicación web para registrar gastos personales, consultar el total acumulado y generar reportes por fechas. Desarrollada con **Python, Flask, SQLite, HTML, CSS y Bootstrap 5**.

## 1. Funcionalidades

- Inicio de sesión con usuario y contraseña.
- Registro de gastos: fecha, descripción y monto.
- Listado de últimos movimientos.
- Eliminación de gastos.
- Resumen del total registrado y del mes actual.
- Reporte con filtro por fecha inicial y final.
- Exportación del reporte a CSV (compatible con Excel).
- Base de datos SQLite creada automáticamente.
- Contraseñas almacenadas mediante hash, no como texto plano.

## 2. Capturas de pantalla

Las capturas se deben actualizar con imágenes tomadas de la aplicación ejecutándose en tu computadora. Guarda las imágenes en `docs/capturas/` con estos nombres para que aparezcan aquí:

### Inicio de sesión
![Pantalla de inicio de sesión](docs/capturas/login.png)

### Panel principal y registro de gastos
![Panel principal](docs/capturas/panel.png)

### Reporte de gastos
![Reporte de gastos](docs/capturas/reporte.png)

> Para tomar las capturas: ejecuta la aplicación, abre `http://127.0.0.1:5000`, inicia sesión y captura cada pantalla. Crea la carpeta `docs/capturas` y guarda las imágenes con los nombres indicados.

## 3. Requisitos

- Python 3.10 o superior.
- pip.
- Navegador web.

## 4. Instalación y ejecución en Windows

Abre CMD o la terminal de Visual Studio Code dentro de la carpeta del proyecto y ejecuta:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Luego abre en el navegador:

`http://127.0.0.1:5000`

**Credenciales iniciales de la práctica**

| Campo | Valor |
|---|---|
| Usuario | `admin` |
| Contraseña | `123` |

La base de datos y sus tablas se crean automáticamente en `instance/gastos.db` al iniciar la aplicación.

## 5. Cómo funciona

1. El usuario ingresa sus credenciales en el formulario de acceso.
2. Flask valida el usuario y compara la contraseña con el hash almacenado en SQLite.
3. Al ingresar, se muestra el panel principal con el resumen de gastos.
4. Se registra cada gasto indicando fecha, descripción y monto.
5. En **Reportes**, se puede filtrar por un rango de fechas, ver el total y exportar los datos a CSV.
6. El usuario puede cerrar sesión desde el botón **Salir**.

## 6. Estructura del proyecto

```text
Control_Gastos_UPRIT/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
├── README.md
├── instance/              # Se crea al ejecutar; no se sube a GitHub
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html
    ├── login.html
    ├── index.html
    ├── reportes.html
    └── 404.html
```

## 7. Publicar en GitHub

1. Crea un repositorio público llamado `Control_Gastos_UPRIT` en GitHub.
2. No inicialices el repositorio con otro README si ya usarás este proyecto.
3. Abre la terminal dentro de la carpeta del proyecto y ejecuta:

```bash
git init
git add .
git commit -m "Proyecto Control de Gastos - PC02"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/Control_Gastos_UPRIT.git
git push -u origin main
```

4. Reemplaza `TU_USUARIO` por tu usuario real de GitHub.
5. Verifica que el repositorio sea **Public** y que el README muestre las capturas.

## 8. Seguridad y observaciones académicas

- La contraseña `123` se deja como credencial inicial solicitada para la demostración académica. **No la uses en un sistema real.**
- Para publicar o desplegar el sistema, define una `SECRET_KEY` larga y aleatoria y cambia `ADMIN_PASSWORD`.
- No subas `instance/gastos.db`, archivos `.env`, contraseñas reales ni claves secretas a GitHub.
- Para despliegue con HTTPS, configura `COOKIE_SECURE=1`. El `Procfile` permite usar Gunicorn en plataformas compatibles.

## 9. Tecnologías utilizadas

- Python 3
- Flask
- SQLite
- Werkzeug (hash de contraseñas)
- HTML5 y CSS3
- Bootstrap 5
- Git y GitHub
