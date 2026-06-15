import random
from werkzeug.security import generate_password_hash
from app import app, db, Usuario, Libro

def run_seed():
    with app.app_context():
        # Nos aseguramos que las tablas existan siempre
        db.create_all()

        # Verificamos si la base de datos ya está poblada buscando al admin
        admin_existente = Usuario.query.filter_by(correo_usuario="admin@biblio.com").first()
        if admin_existente:
            print("La base de datos ya está poblada. No se requieren cambios.")
            return

        print("Creando usuario Administrador...")
        admin = Usuario(
            nombre_usuario="admin",
            correo_usuario="admin@biblio.com",
            nombre_completo_usuario="Administrador del Sistema",
            hash_contrasena=generate_password_hash("admin"),
            es_admin=True
        )
        db.session.add(admin)

        print("Creando usuario estándar (No Admin)...")
        usuario_tales = Usuario(
            nombre_usuario="tales",
            correo_usuario="tales@correo.com",
            nombre_completo_usuario="Tales de Mileto",
            hash_contrasena=generate_password_hash("tales"),
            es_admin=False
        )
        db.session.add(usuario_tales)

        print("Preparando lista de libros...")
        datos_libros = [
           {"titulo": "Sobre héroes y tumbas", "autor": "Ernesto Sabato", "isbn": "9788432230141", "anio_publicacion": 1961, "temas": "Argentine fiction", "url_portada": "https://covers.openlibrary.org/b/id/8078732-L.jpg"},
           {"titulo": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "isbn": "9780198306153", "anio_publicacion": 1600, "temas": "Don Quixote (Cervantes Saavedra, Miguel de)", "url_portada": "https://covers.openlibrary.org/b/id/14428305-L.jpg"},
           {"titulo": "1984 (adaptation)", "autor": "George Orwell", "isbn": "1405862416", "anio_publicacion": 2003, "temas": "Totalitarianism", "url_portada": "https://covers.openlibrary.org/b/id/8745958-L.jpg"},
           {"titulo": "Crónica de una muerte anunciada", "autor": "Gabriel García Márquez", "isbn": "0606330402", "anio_publicacion": 1980, "temas": "ritual", "url_portada": "https://covers.openlibrary.org/b/id/8489859-L.jpg"},
           {"titulo": "El Principito", "autor": "Antoine de Saint-Exupéry", "isbn": "9788418797453", "anio_publicacion": 2018, "temas": "General", "url_portada": "https://covers.openlibrary.org/b/id/13499066-L.jpg"},
           {"titulo": "Fahrenheit 451", "autor": "Ray Bradbury", "isbn": "9781613832493", "anio_publicacion": 1953, "temas": "Mechanical Hound", "url_portada": "https://covers.openlibrary.org/b/id/12993656-L.jpg"},
           {"titulo": "La sombra del viento", "autor": "Carlos Ruiz Zafón", "isbn": "9780297851196", "anio_publicacion": 2001, "temas": "Mothers and sons", "url_portada": "https://covers.openlibrary.org/b/id/10107644-L.jpg"},
           {"titulo": "Rayuela", "autor": "Julio Cortázar", "isbn": "950557133X", "anio_publicacion": 1963, "temas": "Chronology", "url_portada": "https://covers.openlibrary.org/b/id/1047466-L.jpg"},
           {"titulo": "Pedro Páramo", "autor": "Juan Rulfo", "isbn": "9781983675607", "anio_publicacion": 1955, "temas": "Ficción", "url_portada": "https://covers.openlibrary.org/b/id/5419076-L.jpg"},
           {"titulo": "Orgullo y prejuicio", "autor": "Jane Austen", "isbn": "9788469833346", "anio_publicacion": 2013, "temas": "General", "url_portada": "https://covers.openlibrary.org/b/id/13574150-L.jpg"},
           {"titulo": "El Nombre de la Rosa", "autor": "Umberto Eco", "isbn": "9780307882776", "anio_publicacion": 2011, "temas": "General", "url_portada": "Sin portada"},
           {"titulo": "Matar a un ruisenor", "autor": "Harper Lee", "isbn": "9781681419770", "anio_publicacion": 2015, "temas": "General", "url_portada": "https://covers.openlibrary.org/b/id/13628885-L.jpg"},
           {"titulo": "La casa de los espíritus", "autor": "Isabel Allende", "isbn": "1442077999", "anio_publicacion": 1982, "temas": "Chilean literature", "url_portada": "https://covers.openlibrary.org/b/id/3205226-L.jpg"},
           {"titulo": "El túnel", "autor": "Ernesto Sabato", "isbn": "9586140857", "anio_publicacion": 1948, "temas": "Spanish fiction", "url_portada": "https://covers.openlibrary.org/b/id/5517733-L.jpg"},
           {"titulo": "HOBBIT. LA DESOLACION DE SMAUG, EL", "autor": "J. R. R. Tolkien", "isbn": "9505471580", "anio_publicacion": 2013, "temas": "General", "url_portada": "https://covers.openlibrary.org/b/id/12345036-L.jpg"},
           {"titulo": "Los detectives salvajes", "autor": "Roberto Bolaño", "isbn": "9782823613131", "anio_publicacion": 1998, "temas": "Fiction, mystery & detective, general", "url_portada": "https://covers.openlibrary.org/b/id/3706128-L.jpg"},
           {"titulo": "El alquimista", "autor": "Paulo Coelho", "isbn": "9786073138765", "anio_publicacion": 2016, "temas": "Novela brasileña", "url_portada": "https://covers.openlibrary.org/b/id/12674818-L.jpg"},
           {"titulo": "Ensayo Sobre la Ceguera", "autor": "José Saramago", "isbn": "8466312307", "anio_publicacion": 2007, "temas": "General", "url_portada": "https://covers.openlibrary.org/b/id/2270923-L.jpg"}
        ]

        print("Insertando libros...")
        for datos in datos_libros:
            copias = random.randint(1, 3)
            portada_url = datos.get("portada", datos.get("url_portada", ""))
            
            libro = Libro(
                titulo=datos["titulo"],
                autor=datos["autor"],
                isbn=datos["isbn"],
                anio_publicacion=datos["anio_publicacion"],
                temas=datos["temas"],
                portada=portada_url,
                copias_totales=copias,
                copias_disponibles=copias
            )
            db.session.add(libro)

        print("Guardando cambios en la base de datos...")
        db.session.commit()
        
        print("¡Proceso completado exitosamente! Base de datos inicializada y poblada.")

if __name__ == '__main__':
    run_seed()