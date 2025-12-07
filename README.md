# 📚 Biblioteca Pública

Sistema de gestión de préstamos de libros desarrollado con Django y PostgreSQL.

## 🚀 Características

- Gestión de libros y géneros
- Sistema de préstamos con seguimiento de estado
- Autenticación y permisos diferenciados
- Interfaz moderna y responsiva

## 🛠️ Tecnologías

- Django 5.x
- PostgreSQL
- HTML/CSS/JavaScript

## ⚙️ Instalación

```bash
# Clonar repositorio
git clone https://github.com/julianaalgarin/django_library.git
cd biblioteca_publica

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Instalar dependencias
pip install django psycopg2-binary

# Configurar base de datos en settings.py
# Crear BD: biblioteca_publica

# Migrar y crear superusuario
python manage.py migrate
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

Acceder en: http://127.0.0.1:8000/

## 👥 Usuarios

**Regular**: Ver catálogo, crear préstamos  
**Admin**: Todo lo anterior + crear/eliminar libros, gestionar préstamos

## 📝 Modelos

- **Genre**: Géneros literarios
- **Book**: Libros con autor, género, año, disponibilidad
- **Reader**: Lectores registrados
- **Loan**: Préstamos (activo/devuelto)
- **LoanItem**: Detalle de libros por préstamo

---

**Autor**: Juliana Algarín | [@julianaalgarin](https://github.com/julianaalgarin)
