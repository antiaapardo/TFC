from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dto import (get_events, get_categories, add_favorite, 
                 remove_favorite, get_favorite, register_user, 
                 login_user, add_event, delete_event, 
                 verify_user, response_wrapper, update_user_foto, update_user_info, change_password,delete_past_events, update_event_image, update_event_info)
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)


# ==========================================
# RUTAS DE EVENTOS Y CATEGORÍAS
# ==========================================

@app.route("/api/eventos", methods=["GET"])
def get_eventos():
    """
    Obtiene la lista de todos los eventos (mercadillos) a través de una petición HTTP GET.

    Parámetros:
        Ninguno.

    Retorna:
        Response: Una respuesta de Flask en formato JSON conteniendo la lista de eventos o el mensaje de error.

    Notas:
        No requiere autenticación previa.
    """
    delete_past_events()
    res, code = get_events()
    return make_response(jsonify(res), code)

@app.route("/api/eventos", methods=["POST"])
def create_evento():
    """
    Crea un nuevo evento (mercadillo) a través de una petición HTTP POST.
    """
    body = request.get_json(silent=True)
    if not body:
         return make_response(jsonify(response_wrapper("111", "Datos vacíos o JSON inválido")), 400)

    raw_usuario = body.get('id_usuario')
    if isinstance(raw_usuario, dict):
        id_organizador = raw_usuario.get('id_usuario', 1)
    else:
        id_organizador = raw_usuario
        
    id_categoria = body.get('id_categoria')
    titulo = body.get('titulo')
    descripcion = body.get('descripcion', '')
    direccion_texto = body.get('direccion_texto')
    latitud = body.get('latitud')
    longitud = body.get('longitud')
    fecha_inicio = body.get('fecha_inicio')
    foto_url = body.get('foto_url', '')
    
    fecha_fin = body.get('fecha_fin')
    if not fecha_fin:
        fecha_fin = fecha_inicio 
        
    if latitud is None or longitud is None:
         return make_response(jsonify(response_wrapper("112", "Faltan las coordenadas geográficas de la dirección")), 400)

    res, code = add_event(id_organizador, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin, foto_url)
    return make_response(jsonify(res), code)
@app.route("/api/eventos/<int:id_evento>", methods=["PUT"])
def edit_evento(id_evento):
    """
    Modifica un evento existente.
    """
    body = request.get_json(silent=True)
    if not body:
         return make_response(jsonify(response_wrapper("111", "Datos vacíos o JSON inválido")), 400)

    id_categoria = body.get('id_categoria')
    titulo = body.get('titulo')
    descripcion = body.get('descripcion', '')
    direccion_texto = body.get('direccion_texto')
    latitud = body.get('latitud')
    longitud = body.get('longitud')
    fecha_inicio = body.get('fecha_inicio')
    
    fecha_fin = body.get('fecha_fin')
    if not fecha_fin:
        fecha_fin = fecha_inicio 
        
    res, code = update_event_info(id_evento, id_categoria, titulo, descripcion, direccion_texto, latitud, longitud, fecha_inicio, fecha_fin)
    return make_response(jsonify(res), code)

@app.route("/api/eventos/<int:id_evento>", methods=["DELETE"])
def delete_evento(id_evento):
    """
    Elimina un evento específico de la BD y pulveriza su carpeta física
    esquivando los bloqueos de permisos de Windows.
    """
    res, code = delete_event(id_evento)
    
    if code == 200:
        try:
            import stat  
            
            base_path = os.path.dirname(os.path.abspath(__file__))
            carpeta_evento = os.path.join(base_path, 'static', 'img_eventos', str(id_evento))
            
            if os.path.exists(carpeta_evento):
                for root, dirs, files in os.walk(carpeta_evento, topdown=False):
                    for name in files:
                        archivo_path = os.path.join(root, name)
                        os.chmod(archivo_path, stat.S_IWRITE)
                        os.remove(archivo_path)
                    for name in dirs:
                        subcarpeta_path = os.path.join(root, name)
                        os.chmod(subcarpeta_path, stat.S_IWRITE)
                        os.rmdir(subcarpeta_path)
                
                os.chmod(carpeta_evento, stat.S_IWRITE)
                os.rmdir(carpeta_evento)
                print(f"🗑️ Carpeta con ID {id_evento} pulverizada por completo de static/img_eventos/")
                
        except Exception as e:
            print(f"⚠️ Error al borrar la carpeta física del evento {id_evento}: {e}")

    return make_response(jsonify(res), code)
@app.route('/api/eventos/<int:id_evento>/imagenes', methods=['POST'])
def subir_imagenes_evento(id_evento):
    try:
        if 'imagenes' not in request.files:
            return jsonify({"status": {"msg": "No hay archivos en la petición"}}), 400

        archivos = request.files.getlist('imagenes')
        urls_finales = []

        base_path = os.path.dirname(os.path.abspath(__file__))
        carpeta_evento = os.path.join(base_path, 'static', 'img_eventos', str(id_evento))
        
        os.makedirs(carpeta_evento, exist_ok=True)

        for indice, file in enumerate(archivos):
            if file.filename != '':
                extension = os.path.splitext(file.filename)[1].lower()
                nombre_archivo = f"img_{indice}{extension}"
                file_path = os.path.join(carpeta_evento, nombre_archivo)
                
                file.save(file_path)
                
                urls_finales.append(f"http://localhost:5000/static/img_eventos/{id_evento}/{nombre_archivo}")

        urls_string = ",".join(urls_finales)
        res, code = update_event_image(id_evento, urls_string)
        
        return make_response(jsonify(res), code)

    except Exception as e:
        return jsonify({"status": {"msg": f"Error interno: {str(e)}"}}), 500

# ==========================================
# RUTAS DE CATEGORIAS
# ==========================================
    
@app.route("/api/categorias", methods=["GET"])
def get_categorias():
    """
    Obtiene la lista de todas las categorías disponibles a través de una petición HTTP GET.

    Parámetros:
        Ninguno.

    Retorna:
        Response: Una respuesta de Flask en formato JSON conteniendo la lista de categorías.
    """
    res, code = get_categories()
    return make_response(jsonify(res), code)

# ==========================================
# RUTAS DE FAVORITOS
# ==========================================

@app.route("/api/favoritos", methods=["POST"])
def add_favorito():
    """
    Añade un evento a la lista de favoritos de un usuario mediante una petición HTTP POST.

    Parámetros:
        Ninguno por URL. Los datos (id_usuario e id_evento) se extraen del body (JSON).

    Retorna:
        Response: Una respuesta de Flask indicando si el evento fue guardado correctamente.
    """
    body = request.get_json(silent=True)
    if not body:
         return make_response(jsonify(response_wrapper("111", "Datos vacíos o JSON inválido")), 400)
         
    res, code = add_favorite(body.get('id_usuario'), body.get('id_evento'))
    return make_response(jsonify(res), code)

@app.route("/api/favoritos", methods=["DELETE"])
def remove_favorito():
    """
    Elimina un evento de la lista de favoritos de un usuario mediante una petición HTTP DELETE.

    Parámetros:
        Ninguno por URL. Los datos (id_usuario e id_evento) se extraen del body (JSON).

    Retorna:
        Response: Una respuesta de Flask indicando el éxito de la eliminación.
    """
    body = request.get_json(silent=True)
    if not body:
         return make_response(jsonify(response_wrapper("111", "Datos vacíos o JSON inválido")), 400)
         
    res, code = remove_favorite(body.get('id_usuario'), body.get('id_evento'))
    return make_response(jsonify(res), code)

@app.route("/api/favoritos/<int:id_usuario>", methods=["GET"])
def get_favoritos(id_usuario):
    """
    Obtiene todos los eventos favoritos asociados a un usuario mediante una petición HTTP GET.

    Parámetros:
        id_usuario (int): El ID del usuario del que se quieren obtener los favoritos.

    Retorna:
        Response: Una respuesta de Flask en formato JSON con la lista de IDs de los eventos favoritos.
    """
    res, code = get_favorite(id_usuario)
    return make_response(jsonify(res), code)

# ==========================================
# RUTAS DE USUARIOS Y AUTENTICACIÓN
# ==========================================

@app.route("/api/register", methods=["POST"])
def register():
    """
    Registra un nuevo usuario en el sistema a través de una petición HTTP POST.

    Parámetros:
        Ninguno por URL. Los datos del usuario se extraen del body (JSON).

    Retorna:
        Response: Una respuesta de Flask en formato JSON con la confirmación del registro.

    Notas:
        El proceso delega en el DTO la generación del token y el envío automático del correo de verificación.
    """
    body = request.get_json(silent=True)
    if not body:
        return make_response(jsonify(response_wrapper("111", "Datos vacíos o JSON inválido")), 400)
        
    nombre_completo = body.get('nombre_completo')
    email = body.get('email')
    password = body.get('password')
    tipo_usuario = body.get('tipo_usuario', 'visitante') 
    telefono = body.get('telefono', '')
    
    res, code = register_user(nombre_completo, email, password, tipo_usuario, telefono)
    return make_response(jsonify(res), code)

@app.route("/api/verificar/<token>", methods=["GET"])
def verificar_cuenta(token):
    """
    Verifica la cuenta de correo de un usuario usando un token único.

    Parámetros:
        token (str): El identificador único (UUID) enviado al correo del usuario.

    Retorna:
        Response: Una respuesta de Flask en formato JSON indicando si la cuenta fue validada.
    """
    res, code = verificar_usuario_dto(token) 
    return make_response(jsonify(res), code)

@app.route("/api/login", methods=["POST"])
def login():
    """
    Autentica a un usuario en el sistema a través de una petición HTTP POST.

    Parámetros:
        Ninguno por URL. El email y password se extraen del body (JSON).

    Retorna:
        Response: Una respuesta de Flask en formato JSON conteniendo los datos del usuario logueado.

    Notas:
        Retorna código 403 si el usuario no ha verificado su cuenta previamente.
    """
    body = request.get_json(silent=True)
    if not body:
         return make_response(jsonify(response_wrapper("111", "Datos vacíos o JSON inválido")), 400)

    email = body.get('email')
    password = body.get('password')
    
    res, code = login_user(email, password)
    return make_response(jsonify(res), code)

# ==========================================
# GESTIÓN DE PERFIL Y FOTO
# ==========================================

@app.route('/api/usuarios/<int:id_usuario>/avatar', methods=['POST'])
def subir_avatar(id_usuario):
    if 'avatar' not in request.files:
        return jsonify({"status": {"msg": "No hay archivo"}}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"status": {"msg": "Archivo vacío"}}), 400

    if file:
        _, extension = os.path.splitext(file.filename)
        
        nombre_archivo = f"profile_imagen{extension.lower()}"

        carpeta_usuario = os.path.join(os.getcwd(), 'static', 'img_perfil', str(id_usuario))
        
        os.makedirs(carpeta_usuario, exist_ok=True)

        file_path = os.path.join(carpeta_usuario, nombre_archivo)
        file.save(file_path)

        url_final = f"http://localhost:5000/static/img_perfil/{id_usuario}/{nombre_archivo}"

        res, code = update_user_foto(id_usuario, url_final)
        return make_response(jsonify(res), code)
    
@app.route('/api/usuarios/<int:id_usuario>/avatar', methods=['DELETE'])
def borrar_avatar(id_usuario):
    """
    Elimina la foto de perfil del usuario.
    1. Pone la URL a NULL en la base de datos.
    2. Borra el archivo físico del servidor.
    """
    res, code = update_user_foto(id_usuario, None)
    
    if code == 200:
        try:
            carpeta_usuario = os.path.join(os.getcwd(), 'static', 'img_perfil', str(id_usuario))
            if os.path.exists(carpeta_usuario):
                shutil.rmtree(carpeta_usuario) 
        except Exception as e:
            print(f"Aviso: No se pudo borrar la carpeta física: {e}")

    return make_response(jsonify(res), code)

@app.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
def update_perfil(id_usuario):
    """Actualiza datos básicos como el nombre."""
    body = request.get_json(silent=True)
    nombre_completo = body.get('nombre_completo')
    
    res, code = update_user_info(id_usuario, nombre_completo)
    return make_response(jsonify(res), code)

@app.route('/api/usuarios/<int:id_usuario>/password', methods=['PUT'])
def change_password_route(id_usuario):
    """Cambia la contraseña verificando la actual."""
    body = request.get_json(silent=True)
    password_actual = body.get('actual')
    password_nueva = body.get('nueva')
    
    res, code = change_password(id_usuario, password_actual, password_nueva)
    return make_response(jsonify(res), code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)