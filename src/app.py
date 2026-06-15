import os
from datetime import datetime, timezone
from flask import Flask, request, redirect, url_for, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================

app = Flask(__name__)
# Nota: En desarrollo usamos un secret temporal, en producción debe ser una variable de entorno estática
app.secret_key = 'clave_secreta_fija_para_desarrollo_biblio_ia'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblio_ia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta funcionalidad."

# ==========================================
# DEFINICIÓN DE MODELOS
# ==========================================

# Se añade UserMixin para que Flask-Login pueda manejar la sesión de este modelo
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    hash_contrasena = db.Column(db.String(255), nullable=False)
    es_admin = db.Column(db.Boolean, default=False, nullable=False)
    correo_usuario = db.Column(db.String(120), unique=True, nullable=False)
    nombre_completo_usuario = db.Column(db.String(150), nullable=False)

    reservas = db.relationship('Reserva', backref='usuario', lazy=True)


class Libro(db.Model):
    __tablename__ = 'libro'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    copias_totales = db.Column(db.Integer, nullable=False, default=1)
    copias_disponibles = db.Column(db.Integer, nullable=False, default=1)
    portada = db.Column(db.String(255), nullable=True)
    
    # Nuevos campos añadidos
    anio_publicacion = db.Column(db.Integer, nullable=True)
    temas = db.Column(db.String(255), nullable=True)

    reservas = db.relationship('Reserva', backref='libro', lazy=True)


class Reserva(db.Model):
    __tablename__ = 'reserva'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    libro_id = db.Column(db.Integer, db.ForeignKey('libro.id'), nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

# ==========================================
# GESTIÓN DE SESIÓN
# ==========================================

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ==========================================
# LÓGICA DE RUTAS
# ==========================================

# RF3: Catálogo Público (Home)
@app.route('/')
def index():
    libros = Libro.query.all()
    # Usamos la plantilla de Tailwind CSS
    return render_template('index.html', libros=libros)

# RF1: Auth - Registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        correo_usuario = request.form['correo_usuario']
        nombre_completo_usuario = request.form['nombre_completo_usuario']
        password = request.form['password']

        # Validación simple por si el usuario ya existe
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first() or \
           Usuario.query.filter_by(correo_usuario=correo_usuario).first():
            flash("El usuario o correo ya existe.", "error")
            return redirect(url_for('registro'))

        # Creamos al usuario con la contraseña propiamente cifrada con hash
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            correo_usuario=correo_usuario,
            nombre_completo_usuario=nombre_completo_usuario,
            hash_contrasena=generate_password_hash(password),
            # Para facilitar las pruebas, el que se llame "admin" obtendrá provilegios
            es_admin=(nombre_usuario.lower() == 'admin') 
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash("Registro exitoso. Ya puedes iniciar sesión.")
        return redirect(url_for('login'))
        
    return render_template('registro.html')

# RF1: Auth - Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        
        user = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        # Validamos credenciales usando werkzeug
        if user and check_password_hash(user.hash_contrasena, password):
            login_user(user)
            flash("Has iniciado sesión correctamente.")
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            
    return render_template('login.html')

# RF1: Auth - Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión satisfactoriamente.")
    return redirect(url_for('index'))

# RF4: Motor de Reservas
@app.route('/reservar/<int:id_libro>', methods=['POST'])
@login_required
def reservar(id_libro):
    libro = Libro.query.get_or_404(id_libro)
    
    if libro.copias_disponibles > 0:
        # Lógica de reserva transaccional básica
        libro.copias_disponibles -= 1
        nueva_reserva = Reserva(usuario_id=current_user.id, libro_id=libro.id)
        
        db.session.add(nueva_reserva)
        db.session.commit()
        
        flash(f"Reserva realizada con éxito: '{libro.titulo}'.")
    else:
        flash(f"No hay copias disponibles para este libro: '{libro.titulo}'.", "error")
        
    return redirect(url_for('index'))

# RF5: Admin - Agregar Libro
@app.route('/admin/agregar_libro', methods=['GET', 'POST'])
@login_required
def agregar_libro():
    # Bloque de seguridad: Solo admins
    if not current_user.es_admin:
        flash("Acceso denegado: Necesitas permisos de administrador.", "error")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        # Procesamos el año de publicación (puede venir vacío del formulario)
        anio_val = request.form.get('anio_publicacion')
        anio_publicacion = int(anio_val) if anio_val and anio_val.isdigit() else None

        nuevo_libro = Libro(
            titulo=request.form['titulo'],
            autor=request.form['autor'],
            isbn=request.form['isbn'],
            copias_totales=int(request.form['copias_totales']),
            copias_disponibles=int(request.form['copias_totales']), # Inicializa igual a totales
            portada=request.form.get('portada', ''),
            anio_publicacion=anio_publicacion,         # <-- Campo capturado
            temas=request.form.get('temas', '')        # <-- Campo capturado
        )
        db.session.add(nuevo_libro)
        db.session.commit()
        flash("Libro agregado exitosamente al catálogo.")
        return redirect(url_for('index'))

    return render_template('admin_agregar.html')

# Extra: Visualización de las reservas del usuario actual (Estándar)
@app.route('/mis_reservas')
@login_required
def mis_reservas():
    reservas = Reserva.query.filter_by(usuario_id=current_user.id).all()
    return render_template('mis_reservas.html', reservas=reservas)

# ==========================================
# INICIALIZACIÓN
# ==========================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)