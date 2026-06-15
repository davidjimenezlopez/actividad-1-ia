import unittest
from werkzeug.security import generate_password_hash
from src.app import app, db, Usuario, Libro, Reserva

class TestBiblioIA(unittest.TestCase):
    
    def setUp(self):
        """Se ejecuta ANTES de cada prueba. Prepara el entorno y la base de datos temporal."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Base de datos en memoria
        app.config['WTF_CSRF_ENABLED'] = False # Por si acaso se usan formularios seguros luego
        
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Se ejecuta DESPUÉS de cada prueba. Limpia el entorno para que no interfiera con la siguiente."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Función auxiliar para crear un usuario y un libro para las pruebas
    def crear_datos_prueba(self, copias_libro=1, es_admin=False):
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='admin_user' if es_admin else 'test_user',
                correo_usuario='admin@test.com' if es_admin else 'test@test.com',
                nombre_completo_usuario='Usuario Prueba',
                hash_contrasena=generate_password_hash('password123'),
                es_admin=es_admin
            )
            libro = Libro(
                titulo='Libro de Prueba',
                autor='Autor Test',
                isbn='123-TEST',
                copias_totales=copias_libro,
                copias_disponibles=copias_libro
            )
            db.session.add(usuario)
            db.session.add(libro)
            db.session.commit()
            return usuario.id, libro.id

    def test_registro_y_login(self):
        """1. Prueba que un usuario pueda registrarse y luego iniciar sesión."""
        # Probar Registro
        response_registro = self.client.post('/registro', data={
            'nombre_usuario': 'nuevo_usuario',
            'correo_usuario': 'nuevo@test.com',
            'nombre_completo_usuario': 'Juan Nuevo',
            'password': 'mi_password_seguro'
        }, follow_redirects=True)
        # Decodificamos a utf-8 para manejar sin problemas los acentos en los mensajes Flash
        self.assertIn('Registro exitoso', response_registro.data.decode('utf-8'))
        
        # Probar Login
        response_login = self.client.post('/login', data={
            'nombre_usuario': 'nuevo_usuario',
            'password': 'mi_password_seguro'
        }, follow_redirects=True)
        self.assertIn('Has iniciado sesión correctamente', response_login.data.decode('utf-8'))

    def test_reserva_exitosa(self):
        """2. Prueba que un usuario pueda reservar un libro con stock."""
        id_usuario, id_libro = self.crear_datos_prueba(copias_libro=1)
        
        # Iniciar sesión
        self.client.post('/login', data={'nombre_usuario': 'test_user', 'password': 'password123'})
        
        # Guardamos el estado inicial
        with app.app_context():
            copias_antes = Libro.query.get(id_libro).copias_disponibles
            self.assertEqual(copias_antes, 1)

        # Realizar la reserva
        response = self.client.post(f'/reservar/{id_libro}', follow_redirects=True)
        self.assertIn('Reserva realizada con éxito', response.data.decode('utf-8'))
        
        # Validamos que se haya restado el inventario y creado el registro y relación correctos
        with app.app_context():
            copias_despues = Libro.query.get(id_libro).copias_disponibles
            self.assertEqual(copias_despues, 0)
            reserva = Reserva.query.filter_by(usuario_id=id_usuario, libro_id=id_libro).first()
            self.assertIsNotNone(reserva)

    def test_reserva_sin_stock(self):
        """3. Prueba que NO se pueda reservar si no hay stock (copias disp. = 0)."""
        id_usuario, id_libro = self.crear_datos_prueba(copias_libro=0)
        
        self.client.post('/login', data={'nombre_usuario': 'test_user', 'password': 'password123'})
        
        # Internar reservar
        response = self.client.post(f'/reservar/{id_libro}', follow_redirects=True)
        self.assertIn('No hay copias disponibles', response.data.decode('utf-8'))
        
        # Validar en base de datos que ninguna reserva se creó
        with app.app_context():
            reserva = Reserva.query.filter_by(usuario_id=id_usuario, libro_id=id_libro).first()
            self.assertIsNone(reserva)

    def test_proteccion_admin(self):
        """4. Prueba que un usuario NO admin no pueda entrar al formulario de crear libros."""
        # Se crea usuario sin poder admin (False)
        id_usuario, id_libro = self.crear_datos_prueba(es_admin=False)
        self.client.post('/login', data={'nombre_usuario': 'test_user', 'password': 'password123'})

        # Intentar acceder a un espacio protegido
        response = self.client.get('/admin/agregar_libro', follow_redirects=True)
        self.assertIn('Acceso denegado', response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()